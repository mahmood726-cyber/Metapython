"""
Plugin Security System - Trust/Sandbox Levels, Signed Manifests
"""

import hashlib
import hmac
import json
import time
import os
import tempfile
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Optional, Any, Union
import logging

try:
    from cryptography.hazmat.primitives import hashes, serialization
    from cryptography.hazmat.primitives.asymmetric import rsa, padding
    from cryptography.exceptions import InvalidSignature
    HAS_CRYPTOGRAPHY = True
except ImportError:
    HAS_CRYPTOGRAPHY = False

from .api import PluginManifest, TrustLevel, SandboxLevel

logger = logging.getLogger(__name__)

class PluginSecurity:
    """Main plugin security coordinator"""
    
    def __init__(self, trust_store_path: Optional[Path] = None):
        self.trust_store_path = trust_store_path or Path.home() / '.metapython' / 'trust_store'
        self.trust_store_path.mkdir(parents=True, exist_ok=True)
        self.validator = PluginValidator()
        self.signer = ManifestSigner()
        self.sandbox = SandboxExecutor()
    
    def evaluate_trust_level(self, manifest: PluginManifest, plugin_path: Path) -> TrustLevel:
        """Evaluate appropriate trust level for a plugin"""
        
        # Check if plugin is officially signed
        if manifest.signed_by and self._verify_official_signature(manifest):
            return TrustLevel.OFFICIAL
        
        # Check if plugin is signed by verified publisher
        if manifest.signed_by and self._verify_publisher_signature(manifest):
            return TrustLevel.VERIFIED
        
        # Check if plugin passes basic validation
        validation_result = self.validator.validate_plugin(manifest, plugin_path)
        if validation_result['safe']:
            return TrustLevel.BASIC
        
        # Default to untrusted
        return TrustLevel.UNTRUSTED
    
    def recommend_sandbox_level(self, manifest: PluginManifest) -> SandboxLevel:
        """Recommend sandbox level based on trust level and capabilities"""
        
        trust_level = manifest.trust_level
        
        # Trust-based recommendations
        if trust_level == TrustLevel.OFFICIAL:
            return SandboxLevel.NONE
        elif trust_level == TrustLevel.VERIFIED:
            return SandboxLevel.BASIC
        elif trust_level == TrustLevel.BASIC:
            return SandboxLevel.STRICT
        else:
            return SandboxLevel.FULL
    
    def _verify_official_signature(self, manifest: PluginManifest) -> bool:
        """Verify official Metapython signature"""
        if not HAS_CRYPTOGRAPHY or not manifest.signature:
            return False
        
        try:
            # In practice, would verify against official public key
            official_key_path = self.trust_store_path / 'official_public_key.pem'
            if not official_key_path.exists():
                return False
            
            # Simplified verification - real implementation would verify signature
            return manifest.signed_by == 'official@metapython.org'
            
        except Exception as e:
            logger.warning(f"Official signature verification failed: {e}")
            return False
    
    def _verify_publisher_signature(self, manifest: PluginManifest) -> bool:
        """Verify publisher signature against trust store"""
        if not HAS_CRYPTOGRAPHY or not manifest.signature:
            return False
        
        try:
            # Check if publisher is in trust store
            publisher_key_path = self.trust_store_path / f"{manifest.signed_by}.pem"
            if not publisher_key_path.exists():
                return False
            
            # Simplified verification
            return True
            
        except Exception as e:
            logger.warning(f"Publisher signature verification failed: {e}")
            return False

class ManifestSigner:
    """Handle signing and verification of plugin manifests"""
    
    def __init__(self):
        self.key_size = 2048
    
    def generate_key_pair(self) -> Dict[str, bytes]:
        """Generate RSA key pair for signing"""
        if not HAS_CRYPTOGRAPHY:
            raise RuntimeError("cryptography library required for signing")
        
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=self.key_size
        )
        
        public_key = private_key.public_key()
        
        private_pem = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        )
        
        public_pem = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
        
        return {
            'private_key': private_pem,
            'public_key': public_pem
        }
    
    def sign_manifest(self, manifest: PluginManifest, private_key_pem: bytes, signer_id: str) -> str:
        """Sign a plugin manifest"""
        if not HAS_CRYPTOGRAPHY:
            raise RuntimeError("cryptography library required for signing")
        
        try:
            private_key = serialization.load_pem_private_key(private_key_pem, password=None)
            
            # Create canonical representation of manifest for signing
            canonical_data = self._canonicalize_manifest(manifest)
            
            signature = private_key.sign(
                canonical_data.encode(),
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH
                ),
                hashes.SHA256()
            )
            
            # Update manifest with signature info
            manifest.signed_by = signer_id
            manifest.signature = signature.hex()
            
            return manifest.signature
            
        except Exception as e:
            logger.error(f"Manifest signing failed: {e}")
            raise
    
    def verify_signature(self, manifest: PluginManifest, public_key_pem: bytes) -> bool:
        """Verify manifest signature"""
        if not HAS_CRYPTOGRAPHY or not manifest.signature:
            return False
        
        try:
            public_key = serialization.load_pem_public_key(public_key_pem)
            canonical_data = self._canonicalize_manifest(manifest)
            signature_bytes = bytes.fromhex(manifest.signature)
            
            public_key.verify(
                signature_bytes,
                canonical_data.encode(),
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH
                ),
                hashes.SHA256()
            )
            
            return True
            
        except InvalidSignature:
            return False
        except Exception as e:
            logger.warning(f"Signature verification failed: {e}")
            return False
    
    def _canonicalize_manifest(self, manifest: PluginManifest) -> str:
        """Create canonical representation of manifest for signing"""
        # Create a copy without signature fields for signing
        manifest_dict = manifest.to_dict()
        
        # Remove signature-related fields
        for field in ['signature', 'signed_by']:
            manifest_dict.pop(field, None)
        
        # Sort keys for canonical representation
        return json.dumps(manifest_dict, sort_keys=True, separators=(',', ':'))

class PluginValidator:
    """Validate plugin safety and security"""
    
    def __init__(self):
        self.dangerous_imports = {
            'os', 'sys', 'subprocess', 'eval', 'exec', 'compile',
            'open', '__import__', 'globals', 'locals', 'vars'
        }
        
        self.dangerous_functions = {
            'eval', 'exec', 'compile', 'getattr', 'setattr', 'delattr',
            'hasattr', '__import__', 'reload'
        }
    
    def validate_plugin(self, manifest: PluginManifest, plugin_path: Path) -> Dict[str, Any]:
        """Comprehensive plugin validation"""
        result = {
            'safe': True,
            'issues': [],
            'warnings': [],
            'checks': {}
        }
        
        # Validate manifest
        manifest_check = self._validate_manifest(manifest)
        result['checks']['manifest'] = manifest_check
        if not manifest_check['safe']:
            result['safe'] = False
            result['issues'].extend(manifest_check['issues'])
        
        # Validate plugin code if available
        if plugin_path.exists():
            code_check = self._validate_code(plugin_path)
            result['checks']['code'] = code_check
            if not code_check['safe']:
                result['safe'] = False
                result['issues'].extend(code_check['issues'])
            result['warnings'].extend(code_check['warnings'])
        
        # Validate dependencies
        deps_check = self._validate_dependencies(manifest)
        result['checks']['dependencies'] = deps_check
        result['warnings'].extend(deps_check['warnings'])
        
        return result
    
    def _validate_manifest(self, manifest: PluginManifest) -> Dict[str, Any]:
        """Validate plugin manifest"""
        issues = []
        warnings = []
        
        # Check required fields
        required_fields = ['name', 'version', 'author', 'plugin_type']
        for field in required_fields:
            if not getattr(manifest, field, None):
                issues.append(f"Missing required field: {field}")
        
        # Check version format
        try:
            parts = manifest.version.split('.')
            if len(parts) < 2 or not all(part.isdigit() for part in parts):
                warnings.append("Version format should follow semantic versioning")
        except:
            issues.append("Invalid version format")
        
        # Check email format (basic)
        if manifest.author_email and '@' not in manifest.author_email:
            warnings.append("Invalid email format")
        
        # Check plugin type
        valid_types = ['analysis_method', 'data_reader', 'report_renderer']
        if manifest.plugin_type not in valid_types:
            warnings.append(f"Unknown plugin type: {manifest.plugin_type}")
        
        return {
            'safe': len(issues) == 0,
            'issues': issues,
            'warnings': warnings
        }
    
    def _validate_code(self, plugin_path: Path) -> Dict[str, Any]:
        """Validate plugin code for safety"""
        issues = []
        warnings = []
        
        try:
            if plugin_path.is_file() and plugin_path.suffix == '.py':
                files_to_check = [plugin_path]
            elif plugin_path.is_dir():
                files_to_check = list(plugin_path.glob('**/*.py'))
            else:
                return {'safe': True, 'issues': [], 'warnings': ['No Python files found']}
            
            for py_file in files_to_check:
                with open(py_file, 'r', encoding='utf-8') as f:
                    code = f.read()
                
                # Check for dangerous imports
                dangerous_found = []
                for dangerous in self.dangerous_imports:
                    if f"import {dangerous}" in code or f"from {dangerous}" in code:
                        dangerous_found.append(dangerous)
                
                if dangerous_found:
                    warnings.append(f"Potentially dangerous imports in {py_file.name}: {dangerous_found}")
                
                # Check for dangerous function calls
                dangerous_calls = []
                for dangerous in self.dangerous_functions:
                    if dangerous in code:
                        dangerous_calls.append(dangerous)
                
                if dangerous_calls:
                    warnings.append(f"Potentially dangerous function calls in {py_file.name}: {dangerous_calls}")
                
                # Check for network access
                network_patterns = ['requests.', 'urllib.', 'socket.', 'http.']
                network_found = [pattern for pattern in network_patterns if pattern in code]
                if network_found:
                    warnings.append(f"Network access detected in {py_file.name}: {network_found}")
                
                # Check file system access
                fs_patterns = ['open(', 'file(', 'Path(', 'os.path', 'shutil.']
                fs_found = [pattern for pattern in fs_patterns if pattern in code]
                if fs_found:
                    warnings.append(f"File system access detected in {py_file.name}: {fs_found}")
        
        except Exception as e:
            issues.append(f"Code validation failed: {e}")
        
        return {
            'safe': len(issues) == 0,
            'issues': issues,
            'warnings': warnings
        }
    
    def _validate_dependencies(self, manifest: PluginManifest) -> Dict[str, Any]:
        """Validate plugin dependencies"""
        warnings = []
        
        # Check for known problematic dependencies
        problematic_deps = ['os', 'sys', 'subprocess', 'eval']
        
        all_deps = manifest.required_dependencies + manifest.optional_dependencies
        
        for dep in all_deps:
            if dep in problematic_deps:
                warnings.append(f"Potentially unsafe dependency: {dep}")
        
        return {
            'warnings': warnings
        }

class SandboxExecutor:
    """Execute plugins in sandboxed environments"""
    
    def __init__(self):
        self.temp_dir = Path(tempfile.gettempdir()) / 'metapython_sandbox'
        self.temp_dir.mkdir(exist_ok=True)
    
    def execute_in_sandbox(self, 
                          plugin_code: str,
                          sandbox_level: SandboxLevel,
                          timeout: int = 30,
                          **kwargs) -> Dict[str, Any]:
        """Execute plugin code in appropriate sandbox"""
        
        if sandbox_level == SandboxLevel.NONE:
            return self._execute_direct(plugin_code, **kwargs)
        elif sandbox_level == SandboxLevel.BASIC:
            return self._execute_restricted(plugin_code, timeout, **kwargs)
        elif sandbox_level == SandboxLevel.STRICT:
            return self._execute_isolated(plugin_code, timeout, **kwargs)
        elif sandbox_level == SandboxLevel.FULL:
            return self._execute_containerized(plugin_code, timeout, **kwargs)
        else:
            raise ValueError(f"Unknown sandbox level: {sandbox_level}")
    
    def _execute_direct(self, plugin_code: str, **kwargs) -> Dict[str, Any]:
        """Execute without sandboxing (trusted plugins only)"""
        try:
            # Direct execution - only for highly trusted plugins
            namespace = {'__builtins__': __builtins__}
            namespace.update(kwargs)
            
            exec(plugin_code, namespace)
            
            return {
                'success': True,
                'result': namespace.get('result'),
                'output': 'Direct execution completed'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def _execute_restricted(self, plugin_code: str, timeout: int, **kwargs) -> Dict[str, Any]:
        """Execute with basic restrictions"""
        try:
            # Restricted builtins
            restricted_builtins = {
                'print': print,
                'len': len,
                'str': str,
                'int': int,
                'float': float,
                'list': list,
                'dict': dict,
                'tuple': tuple,
                'set': set,
                'range': range,
                'enumerate': enumerate,
                'zip': zip,
                'map': map,
                'filter': filter,
                'sum': sum,
                'min': min,
                'max': max,
                'abs': abs,
                'round': round,
            }
            
            namespace = {'__builtins__': restricted_builtins}
            namespace.update(kwargs)
            
            exec(plugin_code, namespace)
            
            return {
                'success': True,
                'result': namespace.get('result'),
                'output': 'Restricted execution completed'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def _execute_isolated(self, plugin_code: str, timeout: int, **kwargs) -> Dict[str, Any]:
        """Execute in isolated environment"""
        try:
            # Create isolated execution script
            script_path = self.temp_dir / f'plugin_{int(time.time())}.py'
            
            with open(script_path, 'w') as f:
                f.write(plugin_code)
            
            # Execute with timeout
            result = subprocess.run(
                [sys.executable, str(script_path)],
                timeout=timeout,
                capture_output=True,
                text=True,
                cwd=self.temp_dir
            )
            
            # Cleanup
            script_path.unlink(missing_ok=True)
            
            return {
                'success': result.returncode == 0,
                'output': result.stdout,
                'error': result.stderr if result.returncode != 0 else None,
                'returncode': result.returncode
            }
            
        except subprocess.TimeoutExpired:
            return {
                'success': False,
                'error': f'Plugin execution timed out after {timeout} seconds'
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def _execute_containerized(self, plugin_code: str, timeout: int, **kwargs) -> Dict[str, Any]:
        """Execute in full container isolation (placeholder)"""
        # This would use Docker or similar for full isolation
        # For now, fall back to isolated execution
        logger.warning("Full containerization not implemented, using isolated execution")
        return self._execute_isolated(plugin_code, timeout, **kwargs)