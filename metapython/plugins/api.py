"""
Plugin API Core - Versioned Entry Points and Capability System
"""

import json
import hashlib
import time
import uuid
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Any, Union, Callable, Type
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

class TrustLevel(Enum):
    """Trust levels for plugins"""
    UNTRUSTED = "untrusted"      # No trust, full sandbox
    BASIC = "basic"              # Basic validation passed
    VERIFIED = "verified"        # Signed by verified publisher
    OFFICIAL = "official"        # Official Metapython plugins

class SandboxLevel(Enum):
    """Sandbox execution levels"""
    NONE = "none"                # No sandboxing (trusted plugins only)
    BASIC = "basic"              # Limited file system access
    STRICT = "strict"            # Isolated execution environment
    FULL = "full"                # Complete isolation with resource limits

@dataclass
class PluginCapability:
    """Semantic capability flags for plugin functionality"""
    name: str
    version: str
    description: str
    required_metapython_version: str
    optional_dependencies: List[str] = field(default_factory=list)
    data_types: List[str] = field(default_factory=list)
    output_formats: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'name': self.name,
            'version': self.version,
            'description': self.description,
            'required_metapython_version': self.required_metapython_version,
            'optional_dependencies': self.optional_dependencies,
            'data_types': self.data_types,
            'output_formats': self.output_formats
        }

@dataclass
class PluginManifest:
    """Plugin manifest with metadata and provenance"""
    plugin_id: str
    name: str
    version: str
    description: str
    author: str
    author_email: str
    homepage: str
    plugin_type: str
    api_version: str
    capabilities: List[PluginCapability]
    trust_level: TrustLevel = TrustLevel.UNTRUSTED
    sandbox_level: SandboxLevel = SandboxLevel.STRICT
    
    # Provenance and security
    created_at: float = field(default_factory=time.time)
    signed_by: Optional[str] = None
    signature: Optional[str] = None
    checksum: Optional[str] = None
    
    # Dependencies
    required_dependencies: List[str] = field(default_factory=list)
    optional_dependencies: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'plugin_id': self.plugin_id,
            'name': self.name,
            'version': self.version,
            'description': self.description,
            'author': self.author,
            'author_email': self.author_email,
            'homepage': self.homepage,
            'plugin_type': self.plugin_type,
            'api_version': self.api_version,
            'capabilities': [cap.to_dict() for cap in self.capabilities],
            'trust_level': self.trust_level.value,
            'sandbox_level': self.sandbox_level.value,
            'created_at': self.created_at,
            'signed_by': self.signed_by,
            'signature': self.signature,
            'checksum': self.checksum,
            'required_dependencies': self.required_dependencies,
            'optional_dependencies': self.optional_dependencies
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'PluginManifest':
        capabilities = [
            PluginCapability(**cap) if isinstance(cap, dict) else cap 
            for cap in data.get('capabilities', [])
        ]
        
        return cls(
            plugin_id=data['plugin_id'],
            name=data['name'],
            version=data['version'],
            description=data['description'],
            author=data['author'],
            author_email=data['author_email'],
            homepage=data['homepage'],
            plugin_type=data['plugin_type'],
            api_version=data['api_version'],
            capabilities=capabilities,
            trust_level=TrustLevel(data.get('trust_level', 'untrusted')),
            sandbox_level=SandboxLevel(data.get('sandbox_level', 'strict')),
            created_at=data.get('created_at', time.time()),
            signed_by=data.get('signed_by'),
            signature=data.get('signature'),
            checksum=data.get('checksum'),
            required_dependencies=data.get('required_dependencies', []),
            optional_dependencies=data.get('optional_dependencies', [])
        )
    
    def generate_checksum(self, plugin_code: str) -> str:
        """Generate checksum for plugin integrity verification"""
        content = f"{self.plugin_id}{self.version}{plugin_code}"
        return hashlib.sha256(content.encode()).hexdigest()

class PluginRegistry:
    """Central registry for discovered and installed plugins"""
    
    def __init__(self, registry_path: Optional[Path] = None):
        self.registry_path = registry_path or Path.home() / '.metapython' / 'plugins'
        self.registry_path.mkdir(parents=True, exist_ok=True)
        self.registry_file = self.registry_path / 'registry.json'
        self._plugins: Dict[str, PluginManifest] = {}
        self._load_registry()
    
    def _load_registry(self):
        """Load registry from disk"""
        if self.registry_file.exists():
            try:
                with open(self.registry_file, 'r') as f:
                    data = json.load(f)
                for plugin_id, manifest_data in data.items():
                    self._plugins[plugin_id] = PluginManifest.from_dict(manifest_data)
            except Exception as e:
                logger.warning(f"Failed to load plugin registry: {e}")
    
    def _save_registry(self):
        """Save registry to disk"""
        try:
            data = {pid: manifest.to_dict() for pid, manifest in self._plugins.items()}
            with open(self.registry_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save plugin registry: {e}")
    
    def register_plugin(self, manifest: PluginManifest) -> bool:
        """Register a plugin in the registry"""
        try:
            self._plugins[manifest.plugin_id] = manifest
            self._save_registry()
            logger.info(f"Registered plugin: {manifest.name} v{manifest.version}")
            return True
        except Exception as e:
            logger.error(f"Failed to register plugin {manifest.plugin_id}: {e}")
            return False
    
    def unregister_plugin(self, plugin_id: str) -> bool:
        """Remove a plugin from the registry"""
        if plugin_id in self._plugins:
            del self._plugins[plugin_id]
            self._save_registry()
            logger.info(f"Unregistered plugin: {plugin_id}")
            return True
        return False
    
    def get_plugin(self, plugin_id: str) -> Optional[PluginManifest]:
        """Get plugin manifest by ID"""
        return self._plugins.get(plugin_id)
    
    def list_plugins(self, plugin_type: Optional[str] = None, 
                    trust_level: Optional[TrustLevel] = None) -> List[PluginManifest]:
        """List registered plugins with optional filtering"""
        plugins = list(self._plugins.values())
        
        if plugin_type:
            plugins = [p for p in plugins if p.plugin_type == plugin_type]
        
        if trust_level:
            plugins = [p for p in plugins if p.trust_level == trust_level]
        
        return plugins
    
    def search_plugins(self, query: str) -> List[PluginManifest]:
        """Search plugins by name or description"""
        query_lower = query.lower()
        return [
            p for p in self._plugins.values()
            if query_lower in p.name.lower() or query_lower in p.description.lower()
        ]

class PluginAPI:
    """Main plugin API interface"""
    
    CURRENT_API_VERSION = "1.0.0"
    
    def __init__(self):
        self.registry = PluginRegistry()
        self._loaded_plugins: Dict[str, Any] = {}
    
    def register_plugin_type(self, plugin_type: str, base_class: Type) -> None:
        """Register a new plugin type"""
        if not hasattr(self, '_plugin_types'):
            self._plugin_types = {}
        self._plugin_types[plugin_type] = base_class
    
    def create_manifest(self, 
                       name: str,
                       version: str,
                       description: str,
                       author: str,
                       author_email: str,
                       plugin_type: str,
                       capabilities: List[PluginCapability],
                       **kwargs) -> PluginManifest:
        """Create a new plugin manifest"""
        plugin_id = f"{author}.{name}"
        
        return PluginManifest(
            plugin_id=plugin_id,
            name=name,
            version=version,
            description=description,
            author=author,
            author_email=author_email,
            homepage=kwargs.get('homepage', ''),
            plugin_type=plugin_type,
            api_version=self.CURRENT_API_VERSION,
            capabilities=capabilities,
            **kwargs
        )
    
    def validate_compatibility(self, manifest: PluginManifest) -> Dict[str, Any]:
        """Validate plugin compatibility with current system"""
        issues = []
        warnings = []
        
        # Check API version compatibility
        if manifest.api_version != self.CURRENT_API_VERSION:
            issues.append(f"API version mismatch: plugin requires {manifest.api_version}, system has {self.CURRENT_API_VERSION}")
        
        # Check required dependencies
        missing_deps = []
        for dep in manifest.required_dependencies:
            try:
                __import__(dep)
            except ImportError:
                missing_deps.append(dep)
        
        if missing_deps:
            issues.append(f"Missing required dependencies: {missing_deps}")
        
        # Check optional dependencies
        missing_optional = []
        for dep in manifest.optional_dependencies:
            try:
                __import__(dep)
            except ImportError:
                missing_optional.append(dep)
        
        if missing_optional:
            warnings.append(f"Missing optional dependencies (some features may be unavailable): {missing_optional}")
        
        return {
            'compatible': len(issues) == 0,
            'issues': issues,
            'warnings': warnings
        }
    
    def load_plugin(self, plugin_id: str, **kwargs) -> Optional[Any]:
        """Load and instantiate a plugin"""
        manifest = self.registry.get_plugin(plugin_id)
        if not manifest:
            logger.error(f"Plugin not found: {plugin_id}")
            return None
        
        # Check compatibility
        compat = self.validate_compatibility(manifest)
        if not compat['compatible']:
            logger.error(f"Plugin {plugin_id} is not compatible: {compat['issues']}")
            return None
        
        # Load the plugin (simplified - would use proper module loading)
        try:
            if plugin_id not in self._loaded_plugins:
                # This is a simplified version - real implementation would load from file
                logger.info(f"Loading plugin: {manifest.name} v{manifest.version}")
                # self._loaded_plugins[plugin_id] = actual_plugin_instance
            
            return self._loaded_plugins.get(plugin_id)
            
        except Exception as e:
            logger.error(f"Failed to load plugin {plugin_id}: {e}")
            return None

class PluginManager:
    """High-level plugin management interface"""
    
    def __init__(self):
        self.api = PluginAPI()
        self.registry = self.api.registry
    
    def discover_plugins(self, search_paths: Optional[List[Path]] = None) -> Dict[str, Any]:
        """Discover plugins in specified paths"""
        from .discovery import PluginDiscovery
        
        discovery = PluginDiscovery()
        return discovery.discover_all(search_paths)
    
    def install_plugin(self, plugin_path: Path, trust_level: TrustLevel = TrustLevel.UNTRUSTED) -> bool:
        """Install a plugin from path"""
        try:
            # Simplified installation process
            # Real implementation would copy files, validate signatures, etc.
            logger.info(f"Installing plugin from {plugin_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to install plugin: {e}")
            return False
    
    def uninstall_plugin(self, plugin_id: str) -> bool:
        """Uninstall a plugin"""
        return self.registry.unregister_plugin(plugin_id)
    
    def list_available_plugins(self, **filters) -> List[PluginManifest]:
        """List available plugins with filtering"""
        return self.registry.list_plugins(**filters)
    
    def get_plugin_info(self, plugin_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed information about a plugin"""
        manifest = self.registry.get_plugin(plugin_id)
        if not manifest:
            return None
        
        compat = self.api.validate_compatibility(manifest)
        
        return {
            'manifest': manifest.to_dict(),
            'compatibility': compat,
            'loaded': plugin_id in self.api._loaded_plugins
        }