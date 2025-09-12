"""
Plugin Discovery System - Local and Remote Plugin Discovery
"""

import os
import json
import importlib.util
from pathlib import Path
from typing import Dict, List, Optional, Any, Union
import logging
import fnmatch
import hashlib

try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False

try:
    import packaging.version as version
    HAS_PACKAGING = True
except ImportError:
    HAS_PACKAGING = False

from .api import PluginManifest, TrustLevel, SandboxLevel

logger = logging.getLogger(__name__)

class CompatibilityChecker:
    """Check plugin compatibility with current system"""
    
    def __init__(self, metapython_version: str = "0.7.0"):
        self.metapython_version = metapython_version
    
    def check_version_compatibility(self, required_version: str) -> Dict[str, Any]:
        """Check if plugin version requirements are met"""
        if not HAS_PACKAGING:
            return {
                'compatible': True,
                'reason': 'packaging library not available - skipping version check'
            }
        
        try:
            current = version.parse(self.metapython_version)
            required = version.parse(required_version)
            
            compatible = current >= required
            
            return {
                'compatible': compatible,
                'current_version': str(current),
                'required_version': str(required),
                'reason': f"Current version {current} {'meets' if compatible else 'does not meet'} requirement {required}"
            }
        except Exception as e:
            return {
                'compatible': False,
                'reason': f"Version parsing error: {e}"
            }
    
    def check_dependencies(self, 
                          required_deps: List[str], 
                          optional_deps: List[str]) -> Dict[str, Any]:
        """Check if plugin dependencies are available"""
        missing_required = []
        missing_optional = []
        available_deps = []
        
        for dep in required_deps:
            try:
                importlib.import_module(dep)
                available_deps.append(dep)
            except ImportError:
                missing_required.append(dep)
        
        for dep in optional_deps:
            try:
                importlib.import_module(dep)
                available_deps.append(dep)
            except ImportError:
                missing_optional.append(dep)
        
        return {
            'compatible': len(missing_required) == 0,
            'missing_required': missing_required,
            'missing_optional': missing_optional,
            'available': available_deps,
            'reason': f"Missing required dependencies: {missing_required}" if missing_required else "All required dependencies available"
        }
    
    def check_full_compatibility(self, manifest: PluginManifest) -> Dict[str, Any]:
        """Perform comprehensive compatibility check"""
        results = {
            'overall_compatible': True,
            'issues': [],
            'warnings': [],
            'details': {}
        }
        
        # Version compatibility
        for capability in manifest.capabilities:
            version_check = self.check_version_compatibility(capability.required_metapython_version)
            results['details'][f'version_check_{capability.name}'] = version_check
            
            if not version_check['compatible']:
                results['overall_compatible'] = False
                results['issues'].append(f"Version incompatibility for {capability.name}: {version_check['reason']}")
        
        # Dependency compatibility
        dep_check = self.check_dependencies(manifest.required_dependencies, manifest.optional_dependencies)
        results['details']['dependency_check'] = dep_check
        
        if not dep_check['compatible']:
            results['overall_compatible'] = False
            results['issues'].append(dep_check['reason'])
        
        if dep_check['missing_optional']:
            results['warnings'].append(f"Missing optional dependencies: {dep_check['missing_optional']}")
        
        return results

class LocalPluginDiscovery:
    """Discover plugins in local filesystem"""
    
    def __init__(self):
        self.compatibility_checker = CompatibilityChecker()
    
    def discover_in_directory(self, directory: Path, recursive: bool = True) -> List[Dict[str, Any]]:
        """Discover plugins in a specific directory"""
        discovered = []
        
        if not directory.exists():
            logger.warning(f"Plugin directory does not exist: {directory}")
            return discovered
        
        # Look for plugin manifest files
        manifest_pattern = "**/plugin.json" if recursive else "plugin.json"
        
        for manifest_path in directory.glob(manifest_pattern):
            try:
                plugin_info = self._load_plugin_from_manifest(manifest_path)
                if plugin_info:
                    discovered.append(plugin_info)
            except Exception as e:
                logger.warning(f"Failed to load plugin from {manifest_path}: {e}")
        
        # Also look for Python files with plugin metadata
        py_pattern = "**/*.py" if recursive else "*.py"
        
        for py_path in directory.glob(py_pattern):
            try:
                plugin_info = self._load_plugin_from_python(py_path)
                if plugin_info:
                    discovered.append(plugin_info)
            except Exception as e:
                logger.debug(f"No plugin found in {py_path}: {e}")
        
        return discovered
    
    def _load_plugin_from_manifest(self, manifest_path: Path) -> Optional[Dict[str, Any]]:
        """Load plugin information from manifest file"""
        try:
            with open(manifest_path, 'r') as f:
                manifest_data = json.load(f)
            
            manifest = PluginManifest.from_dict(manifest_data)
            plugin_dir = manifest_path.parent
            
            # Look for main plugin file
            main_file = plugin_dir / f"{manifest.name}.py"
            if not main_file.exists():
                # Try common alternatives
                for alt_name in ['__init__.py', 'main.py', 'plugin.py']:
                    alt_file = plugin_dir / alt_name
                    if alt_file.exists():
                        main_file = alt_file
                        break
                else:
                    logger.warning(f"No main plugin file found for {manifest.name}")
                    return None
            
            # Check compatibility
            compat_check = self.compatibility_checker.check_full_compatibility(manifest)
            
            return {
                'manifest': manifest,
                'path': plugin_dir,
                'main_file': main_file,
                'compatibility': compat_check,
                'source': 'local_manifest'
            }
            
        except Exception as e:
            logger.error(f"Failed to load manifest {manifest_path}: {e}")
            return None
    
    def _load_plugin_from_python(self, py_path: Path) -> Optional[Dict[str, Any]]:
        """Try to extract plugin information from Python file"""
        try:
            # Load module to check for plugin metadata
            spec = importlib.util.spec_from_file_location("temp_plugin", py_path)
            if not spec or not spec.loader:
                return None
            
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            # Look for plugin metadata
            if not hasattr(module, '__plugin_manifest__'):
                return None
            
            manifest_data = module.__plugin_manifest__
            manifest = PluginManifest.from_dict(manifest_data)
            
            # Check compatibility
            compat_check = self.compatibility_checker.check_full_compatibility(manifest)
            
            return {
                'manifest': manifest,
                'path': py_path.parent,
                'main_file': py_path,
                'compatibility': compat_check,
                'source': 'local_python'
            }
            
        except Exception as e:
            logger.debug(f"No plugin metadata found in {py_path}: {e}")
            return None
    
    def discover_standard_locations(self) -> List[Dict[str, Any]]:
        """Discover plugins in standard locations"""
        discovered = []
        
        # Standard plugin directories
        standard_dirs = [
            Path.home() / '.metapython' / 'plugins',
            Path.cwd() / 'plugins',
            Path(__file__).parent / 'examples',
            Path('/usr/local/share/metapython/plugins'),  # System-wide on Unix
        ]
        
        for plugin_dir in standard_dirs:
            if plugin_dir.exists():
                discovered.extend(self.discover_in_directory(plugin_dir))
        
        return discovered

class RemotePluginDiscovery:
    """Discover plugins from remote repositories"""
    
    def __init__(self, registry_urls: Optional[List[str]] = None):
        self.registry_urls = registry_urls or [
            'https://plugins.metapython.org/api/v1/plugins',  # Official registry
            'https://pypi.org/search/?q=metapython-plugin',   # PyPI search
        ]
        self.compatibility_checker = CompatibilityChecker()
    
    def discover_from_registry(self, registry_url: str) -> List[Dict[str, Any]]:
        """Discover plugins from a remote registry"""
        if not HAS_REQUESTS:
            logger.warning("requests library not available - remote discovery disabled")
            return []
        
        try:
            response = requests.get(registry_url, timeout=10)
            response.raise_for_status()
            
            plugins_data = response.json()
            discovered = []
            
            for plugin_data in plugins_data.get('plugins', []):
                try:
                    manifest = PluginManifest.from_dict(plugin_data)
                    compat_check = self.compatibility_checker.check_full_compatibility(manifest)
                    
                    discovered.append({
                        'manifest': manifest,
                        'compatibility': compat_check,
                        'download_url': plugin_data.get('download_url'),
                        'source': 'remote_registry',
                        'registry_url': registry_url
                    })
                    
                except Exception as e:
                    logger.warning(f"Failed to parse plugin data: {e}")
            
            return discovered
            
        except Exception as e:
            logger.error(f"Failed to discover plugins from {registry_url}: {e}")
            return []
    
    def search_pypi(self, query: str = 'metapython-plugin') -> List[Dict[str, Any]]:
        """Search PyPI for plugins"""
        if not HAS_REQUESTS:
            logger.warning("requests library not available - PyPI search disabled")
            return []
        
        try:
            # Simple PyPI search - in practice would use proper PyPI API
            search_url = f"https://pypi.org/simple/"
            # This is a placeholder - real implementation would use PyPI JSON API
            logger.info(f"PyPI search functionality would query: {query}")
            return []
            
        except Exception as e:
            logger.error(f"PyPI search failed: {e}")
            return []
    
    def discover_all_registries(self) -> List[Dict[str, Any]]:
        """Discover plugins from all configured registries"""
        discovered = []
        
        for registry_url in self.registry_urls:
            try:
                registry_plugins = self.discover_from_registry(registry_url)
                discovered.extend(registry_plugins)
            except Exception as e:
                logger.warning(f"Failed to query registry {registry_url}: {e}")
        
        return discovered

class PluginDiscovery:
    """Main plugin discovery coordinator"""
    
    def __init__(self):
        self.local_discovery = LocalPluginDiscovery()
        self.remote_discovery = RemotePluginDiscovery()
    
    def discover_local(self, search_paths: Optional[List[Path]] = None) -> List[Dict[str, Any]]:
        """Discover local plugins"""
        discovered = []
        
        if search_paths:
            for path in search_paths:
                discovered.extend(self.local_discovery.discover_in_directory(path))
        else:
            discovered.extend(self.local_discovery.discover_standard_locations())
        
        return discovered
    
    def discover_remote(self, include_pypi: bool = False) -> List[Dict[str, Any]]:
        """Discover remote plugins"""
        discovered = []
        
        # Official registries
        discovered.extend(self.remote_discovery.discover_all_registries())
        
        # PyPI search if requested
        if include_pypi:
            discovered.extend(self.remote_discovery.search_pypi())
        
        return discovered
    
    def discover_all(self, 
                    search_paths: Optional[List[Path]] = None,
                    include_remote: bool = False,
                    include_pypi: bool = False) -> Dict[str, Any]:
        """Discover all available plugins"""
        
        local_plugins = self.discover_local(search_paths)
        remote_plugins = []
        
        if include_remote:
            remote_plugins = self.discover_remote(include_pypi)
        
        # Deduplicate plugins by ID
        all_plugins = {}
        
        # Add local plugins first (they take precedence)
        for plugin in local_plugins:
            plugin_id = plugin['manifest'].plugin_id
            all_plugins[plugin_id] = plugin
        
        # Add remote plugins if not already present locally
        for plugin in remote_plugins:
            plugin_id = plugin['manifest'].plugin_id
            if plugin_id not in all_plugins:
                all_plugins[plugin_id] = plugin
            else:
                # Add remote info to existing local plugin
                all_plugins[plugin_id]['remote_available'] = True
                all_plugins[plugin_id]['remote_info'] = {
                    'download_url': plugin.get('download_url'),
                    'registry_url': plugin.get('registry_url')
                }
        
        # Categorize plugins
        categorized = {
            'compatible': [],
            'incompatible': [],
            'warnings': [],
            'by_type': {},
            'by_trust_level': {}
        }
        
        for plugin_id, plugin_info in all_plugins.items():
            manifest = plugin_info['manifest']
            compat = plugin_info['compatibility']
            
            if compat['overall_compatible']:
                categorized['compatible'].append(plugin_info)
            else:
                categorized['incompatible'].append(plugin_info)
            
            if compat.get('warnings'):
                categorized['warnings'].append(plugin_info)
            
            # Group by type
            plugin_type = manifest.plugin_type
            if plugin_type not in categorized['by_type']:
                categorized['by_type'][plugin_type] = []
            categorized['by_type'][plugin_type].append(plugin_info)
            
            # Group by trust level
            trust_level = manifest.trust_level.value
            if trust_level not in categorized['by_trust_level']:
                categorized['by_trust_level'][trust_level] = []
            categorized['by_trust_level'][trust_level].append(plugin_info)
        
        return {
            'total_found': len(all_plugins),
            'local_count': len(local_plugins),
            'remote_count': len(remote_plugins),
            'plugins': list(all_plugins.values()),
            'categorized': categorized,
            'discovery_summary': {
                'compatible_count': len(categorized['compatible']),
                'incompatible_count': len(categorized['incompatible']),
                'warnings_count': len(categorized['warnings']),
                'types': list(categorized['by_type'].keys()),
                'trust_levels': list(categorized['by_trust_level'].keys())
            }
        }
    
    def filter_plugins(self, 
                      plugins: List[Dict[str, Any]],
                      plugin_type: Optional[str] = None,
                      trust_level: Optional[TrustLevel] = None,
                      compatible_only: bool = True,
                      name_pattern: Optional[str] = None) -> List[Dict[str, Any]]:
        """Filter plugins based on criteria"""
        
        filtered = plugins.copy()
        
        if compatible_only:
            filtered = [p for p in filtered if p['compatibility']['overall_compatible']]
        
        if plugin_type:
            filtered = [p for p in filtered if p['manifest'].plugin_type == plugin_type]
        
        if trust_level:
            filtered = [p for p in filtered if p['manifest'].trust_level == trust_level]
        
        if name_pattern:
            filtered = [p for p in filtered if fnmatch.fnmatch(p['manifest'].name.lower(), name_pattern.lower())]
        
        return filtered