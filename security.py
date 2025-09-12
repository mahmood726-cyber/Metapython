"""
Security Module - Phase 8
Security hardening, compliance, authentication, and data protection
"""

import os
import re
import hashlib
import secrets
import time
import json
import logging
from typing import Dict, Any, Optional, List, Set, Callable, Union
from dataclasses import dataclass, field
from functools import wraps
from pathlib import Path
import threading
from datetime import datetime, timedelta
from urllib.parse import urlparse

# Authentication and JWT (optional)
try:
    from jose import JWTError, jwt
    from passlib.context import CryptContext
    HAS_AUTH = True
except ImportError:
    HAS_AUTH = False

# FastAPI security (optional)
try:
    from fastapi import HTTPException, Depends, status
    from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
    from fastapi.middleware.cors import CORSMiddleware
    from fastapi.middleware.trustedhost import TrustedHostMiddleware
    HAS_FASTAPI_SECURITY = True
except ImportError:
    HAS_FASTAPI_SECURITY = False

# Cryptography (optional)
try:
    from cryptography.fernet import Fernet
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
    import base64
    HAS_CRYPTOGRAPHY = True
except ImportError:
    HAS_CRYPTOGRAPHY = False

logger = logging.getLogger(__name__)

@dataclass
class SecurityConfig:
    """Security configuration settings"""
    # Authentication
    enable_auth: bool = False
    jwt_secret_key: Optional[str] = None
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # API Security
    enable_rate_limiting: bool = True
    rate_limit_requests_per_minute: int = 60
    max_request_size_mb: int = 100
    request_timeout_seconds: int = 300
    
    # CORS settings
    cors_origins: List[str] = field(default_factory=lambda: ["*"])
    cors_methods: List[str] = field(default_factory=lambda: ["GET", "POST"])
    cors_headers: List[str] = field(default_factory=lambda: ["*"])
    
    # Data protection
    enable_encryption_at_rest: bool = False
    encryption_key: Optional[str] = None
    anonymize_logs: bool = True
    
    # Compliance
    enable_audit_logging: bool = True
    audit_log_path: str = "audit.log"
    enable_pii_scanning: bool = True
    
    # Content Security
    allowed_file_extensions: Set[str] = field(default_factory=lambda: {
        '.csv', '.xlsx', '.json', '.yaml', '.yml'
    })
    max_file_size_mb: int = 500
    
    # Network security
    trusted_hosts: List[str] = field(default_factory=lambda: ["localhost", "127.0.0.1"])
    require_https: bool = False

class RateLimiter:
    """Token bucket rate limiter"""
    
    def __init__(self, requests_per_minute: int = 60):
        self.requests_per_minute = requests_per_minute
        self.tokens = requests_per_minute
        self.last_update = time.time()
        self.lock = threading.Lock()
    
    def allow_request(self, client_id: str = "default") -> bool:
        """Check if request is allowed under rate limit"""
        with self.lock:
            now = time.time()
            time_passed = now - self.last_update
            
            # Add tokens based on time passed
            self.tokens = min(
                self.requests_per_minute,
                self.tokens + (time_passed * self.requests_per_minute / 60.0)
            )
            self.last_update = now
            
            if self.tokens >= 1:
                self.tokens -= 1
                return True
            else:
                return False

class PIIScanner:
    """PII and sensitive data scanner"""
    
    def __init__(self):
        # Common PII patterns
        self.patterns = {
            'email': re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'),
            'phone': re.compile(r'\b(?:\+?1[-.\s]?)?\(?[0-9]{3}\)?[-.\s]?[0-9]{3}[-.\s]?[0-9]{4}\b'),
            'ssn': re.compile(r'\b\d{3}-?\d{2}-?\d{4}\b'),
            'credit_card': re.compile(r'\b(?:\d{4}[-\s]?){3}\d{4}\b'),
            'ip_address': re.compile(r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b'),
            'api_key': re.compile(r'\b[A-Za-z0-9]{32,}\b'),  # Generic long alphanumeric strings
        }
        
        # Additional healthcare-specific patterns
        self.healthcare_patterns = {
            'mrn': re.compile(r'\b(?:MRN|Medical Record|Patient ID)[\s:]*([A-Z0-9]+)\b', re.IGNORECASE),
            'dob': re.compile(r'\b(?:DOB|Date of Birth)[\s:]*([0-9]{1,2}[/-][0-9]{1,2}[/-][0-9]{2,4})\b', re.IGNORECASE),
            'diagnosis_code': re.compile(r'\b[A-Z][0-9]{2}\.[0-9X]+\b'),  # ICD-10 codes
        }
    
    def scan_text(self, text: str, include_healthcare: bool = True) -> Dict[str, List[str]]:
        """Scan text for PII and return findings"""
        findings = {}
        
        # Scan with basic patterns
        for pattern_name, pattern in self.patterns.items():
            matches = pattern.findall(text)
            if matches:
                findings[pattern_name] = matches
        
        # Scan with healthcare patterns if enabled
        if include_healthcare:
            for pattern_name, pattern in self.healthcare_patterns.items():
                matches = pattern.findall(text)
                if matches:
                    findings[f"healthcare_{pattern_name}"] = matches
        
        return findings
    
    def scan_dataframe(self, df, sample_size: int = 100) -> Dict[str, Any]:
        """Scan pandas DataFrame for PII"""
        findings = {}
        
        # Sample rows if DataFrame is large
        if len(df) > sample_size:
            sample_df = df.sample(n=sample_size, random_state=42)
        else:
            sample_df = df
        
        # Scan string columns
        for column in sample_df.select_dtypes(include=['object']).columns:
            column_findings = {}
            
            for idx, value in sample_df[column].items():
                if pd.isna(value):
                    continue
                
                text_findings = self.scan_text(str(value))
                if text_findings:
                    column_findings[f"row_{idx}"] = text_findings
            
            if column_findings:
                findings[column] = column_findings
        
        return findings
    
    def anonymize_text(self, text: str, replacement: str = "[REDACTED]") -> str:
        """Anonymize PII in text"""
        anonymized = text
        
        # Replace with all patterns
        for pattern_name, pattern in {**self.patterns, **self.healthcare_patterns}.items():
            anonymized = pattern.sub(replacement, anonymized)
        
        return anonymized

class EncryptionManager:
    """Data encryption and decryption utilities"""
    
    def __init__(self, key: Optional[str] = None):
        self.cipher = None
        
        if HAS_CRYPTOGRAPHY:
            if key:
                self.cipher = Fernet(key.encode())
            else:
                # Generate a new key
                self.cipher = Fernet(Fernet.generate_key())
    
    def encrypt_data(self, data: Union[str, bytes]) -> bytes:
        """Encrypt data"""
        if not self.cipher:
            raise ValueError("Encryption not available - install cryptography package")
        
        if isinstance(data, str):
            data = data.encode()
        
        return self.cipher.encrypt(data)
    
    def decrypt_data(self, encrypted_data: bytes) -> bytes:
        """Decrypt data"""
        if not self.cipher:
            raise ValueError("Encryption not available - install cryptography package")
        
        return self.cipher.decrypt(encrypted_data)
    
    def encrypt_file(self, input_path: str, output_path: str) -> None:
        """Encrypt a file"""
        with open(input_path, 'rb') as infile:
            data = infile.read()
        
        encrypted_data = self.encrypt_data(data)
        
        with open(output_path, 'wb') as outfile:
            outfile.write(encrypted_data)
    
    def decrypt_file(self, input_path: str, output_path: str) -> None:
        """Decrypt a file"""
        with open(input_path, 'rb') as infile:
            encrypted_data = infile.read()
        
        decrypted_data = self.decrypt_data(encrypted_data)
        
        with open(output_path, 'wb') as outfile:
            outfile.write(decrypted_data)
    
    def get_key(self) -> str:
        """Get the encryption key"""
        if self.cipher:
            return self.cipher._signing_key.decode()
        return ""

class AuditLogger:
    """Security audit logging"""
    
    def __init__(self, log_path: str = "audit.log"):
        self.log_path = log_path
        self.logger = logging.getLogger("audit")
        
        # Setup file handler for audit logs
        handler = logging.FileHandler(log_path)
        formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        self.logger.setLevel(logging.INFO)
    
    def log_event(self, event_type: str, user_id: str = "anonymous",
                  details: Dict[str, Any] = None, success: bool = True) -> None:
        """Log security event"""
        event = {
            'event_type': event_type,
            'user_id': user_id,
            'timestamp': datetime.utcnow().isoformat(),
            'success': success,
            'details': details or {}
        }
        
        if success:
            self.logger.info(json.dumps(event))
        else:
            self.logger.warning(json.dumps(event))
    
    def log_access(self, resource: str, user_id: str = "anonymous",
                   action: str = "read", success: bool = True) -> None:
        """Log resource access"""
        self.log_event(
            event_type="resource_access",
            user_id=user_id,
            details={
                'resource': resource,
                'action': action
            },
            success=success
        )
    
    def log_authentication(self, user_id: str, success: bool = True,
                          details: Dict[str, Any] = None) -> None:
        """Log authentication attempt"""
        self.log_event(
            event_type="authentication",
            user_id=user_id,
            details=details,
            success=success
        )
    
    def log_data_access(self, data_type: str, user_id: str = "anonymous",
                       n_records: int = 0, success: bool = True) -> None:
        """Log data access"""
        self.log_event(
            event_type="data_access",
            user_id=user_id,
            details={
                'data_type': data_type,
                'n_records': n_records
            },
            success=success
        )

class AuthenticationManager:
    """JWT-based authentication management"""
    
    def __init__(self, config: SecurityConfig):
        self.config = config
        self.pwd_context = None
        
        if HAS_AUTH:
            self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        
        # Generate secret key if not provided
        if not config.jwt_secret_key:
            config.jwt_secret_key = secrets.token_urlsafe(32)
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify password against hash"""
        if not self.pwd_context:
            return False
        return self.pwd_context.verify(plain_password, hashed_password)
    
    def get_password_hash(self, password: str) -> str:
        """Generate password hash"""
        if not self.pwd_context:
            raise ValueError("Authentication not available - install python-jose and passlib")
        return self.pwd_context.hash(password)
    
    def create_access_token(self, data: Dict[str, Any], 
                           expires_delta: Optional[timedelta] = None) -> str:
        """Create JWT access token"""
        if not HAS_AUTH:
            raise ValueError("Authentication not available - install python-jose")
        
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=self.config.access_token_expire_minutes)
        
        to_encode.update({"exp": expire})
        
        encoded_jwt = jwt.encode(
            to_encode, 
            self.config.jwt_secret_key, 
            algorithm=self.config.jwt_algorithm
        )
        return encoded_jwt
    
    def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Verify and decode JWT token"""
        if not HAS_AUTH:
            return None
        
        try:
            payload = jwt.decode(
                token, 
                self.config.jwt_secret_key, 
                algorithms=[self.config.jwt_algorithm]
            )
            return payload
        except JWTError:
            return None

class SecurityManager:
    """Central security management"""
    
    def __init__(self, config: Optional[SecurityConfig] = None):
        self.config = config or SecurityConfig()
        
        # Initialize components
        self.rate_limiter = RateLimiter(self.config.rate_limit_requests_per_minute)
        self.pii_scanner = PIIScanner()
        self.audit_logger = AuditLogger(self.config.audit_log_path)
        self.auth_manager = AuthenticationManager(self.config)
        
        # Encryption manager
        self.encryption_manager = None
        if self.config.enable_encryption_at_rest:
            self.encryption_manager = EncryptionManager(self.config.encryption_key)
    
    def validate_file_upload(self, filename: str, file_size: int) -> Dict[str, Any]:
        """Validate file upload security"""
        validation_result = {
            'valid': True,
            'errors': [],
            'warnings': []
        }
        
        # Check file extension
        file_ext = Path(filename).suffix.lower()
        if file_ext not in self.config.allowed_file_extensions:
            validation_result['valid'] = False
            validation_result['errors'].append(f"File extension {file_ext} not allowed")
        
        # Check file size
        max_size_bytes = self.config.max_file_size_mb * 1024 * 1024
        if file_size > max_size_bytes:
            validation_result['valid'] = False
            validation_result['errors'].append(f"File size exceeds {self.config.max_file_size_mb}MB limit")
        
        # Check for suspicious filenames
        suspicious_patterns = [r'\.\.', r'[<>:"|?*]', r'^(CON|PRN|AUX|NUL|COM[1-9]|LPT[1-9])$']
        for pattern in suspicious_patterns:
            if re.search(pattern, filename, re.IGNORECASE):
                validation_result['valid'] = False
                validation_result['errors'].append("Suspicious filename pattern detected")
                break
        
        return validation_result
    
    def scan_data_for_pii(self, data: Any, data_type: str = "unknown") -> Dict[str, Any]:
        """Scan data for PII with compliance reporting"""
        scan_result = {
            'has_pii': False,
            'findings': {},
            'recommendations': [],
            'compliance_risk': 'low'
        }
        
        if not self.config.enable_pii_scanning:
            return scan_result
        
        try:
            if isinstance(data, str):
                findings = self.pii_scanner.scan_text(data)
            elif hasattr(data, 'to_string'):  # DataFrame-like
                # Convert to string for scanning (sample only)
                text_sample = str(data.head(10))
                findings = self.pii_scanner.scan_text(text_sample)
            else:
                findings = self.pii_scanner.scan_text(str(data))
            
            if findings:
                scan_result['has_pii'] = True
                scan_result['findings'] = findings
                
                # Assess compliance risk
                high_risk_types = ['ssn', 'credit_card', 'healthcare_mrn']
                medium_risk_types = ['email', 'phone', 'healthcare_dob']
                
                if any(pii_type in high_risk_types for pii_type in findings.keys()):
                    scan_result['compliance_risk'] = 'high'
                    scan_result['recommendations'].append("Immediate anonymization required for high-risk PII")
                elif any(pii_type in medium_risk_types for pii_type in findings.keys()):
                    scan_result['compliance_risk'] = 'medium'
                    scan_result['recommendations'].append("Consider anonymization for medium-risk PII")
                
                # Log PII detection
                self.audit_logger.log_event(
                    event_type="pii_detected",
                    details={
                        'data_type': data_type,
                        'pii_types': list(findings.keys()),
                        'risk_level': scan_result['compliance_risk']
                    }
                )
        
        except Exception as e:
            logger.warning(f"PII scanning failed: {e}")
            scan_result['recommendations'].append(f"PII scanning failed: {e}")
        
        return scan_result
    
    def anonymize_data(self, data: Any) -> Any:
        """Anonymize data by removing or masking PII"""
        if isinstance(data, str):
            return self.pii_scanner.anonymize_text(data)
        elif hasattr(data, 'copy'):  # DataFrame-like
            anonymized = data.copy()
            # Apply anonymization to string columns
            for col in anonymized.select_dtypes(include=['object']).columns:
                anonymized[col] = anonymized[col].astype(str).apply(
                    self.pii_scanner.anonymize_text
                )
            return anonymized
        else:
            return self.pii_scanner.anonymize_text(str(data))
    
    def secure_file_storage(self, file_path: str, encrypt: bool = None) -> str:
        """Securely store file with optional encryption"""
        if encrypt is None:
            encrypt = self.config.enable_encryption_at_rest
        
        if encrypt and self.encryption_manager:
            encrypted_path = f"{file_path}.encrypted"
            self.encryption_manager.encrypt_file(file_path, encrypted_path)
            
            # Remove original file
            os.remove(file_path)
            
            self.audit_logger.log_event(
                event_type="file_encrypted",
                details={'file_path': encrypted_path}
            )
            
            return encrypted_path
        
        return file_path
    
    def check_request_security(self, request_size: int, client_ip: str = "unknown") -> Dict[str, Any]:
        """Check request security constraints"""
        security_check = {
            'allowed': True,
            'reasons': []
        }
        
        # Rate limiting
        if not self.rate_limiter.allow_request(client_ip):
            security_check['allowed'] = False
            security_check['reasons'].append("Rate limit exceeded")
        
        # Request size check
        max_size_bytes = self.config.max_request_size_mb * 1024 * 1024
        if request_size > max_size_bytes:
            security_check['allowed'] = False
            security_check['reasons'].append(f"Request size exceeds {self.config.max_request_size_mb}MB limit")
        
        # Log security check
        self.audit_logger.log_event(
            event_type="request_security_check",
            details={
                'client_ip': client_ip,
                'request_size': request_size,
                'allowed': security_check['allowed'],
                'reasons': security_check['reasons']
            },
            success=security_check['allowed']
        )
        
        return security_check
    
    def generate_security_report(self) -> Dict[str, Any]:
        """Generate security status report"""
        return {
            'security_config': {
                'authentication_enabled': self.config.enable_auth,
                'rate_limiting_enabled': self.config.enable_rate_limiting,
                'encryption_at_rest': self.config.enable_encryption_at_rest,
                'pii_scanning_enabled': self.config.enable_pii_scanning,
                'audit_logging_enabled': self.config.enable_audit_logging
            },
            'compliance_features': {
                'audit_trail': os.path.exists(self.config.audit_log_path),
                'data_anonymization': True,
                'secure_file_storage': self.config.enable_encryption_at_rest,
                'access_controls': self.config.enable_auth
            },
            'dependencies': {
                'authentication': HAS_AUTH,
                'fastapi_security': HAS_FASTAPI_SECURITY,
                'cryptography': HAS_CRYPTOGRAPHY
            },
            'recommendations': self._get_security_recommendations()
        }
    
    def _get_security_recommendations(self) -> List[str]:
        """Get security improvement recommendations"""
        recommendations = []
        
        if not self.config.enable_auth:
            recommendations.append("Enable authentication for production use")
        
        if not self.config.enable_encryption_at_rest:
            recommendations.append("Enable encryption at rest for sensitive data")
        
        if not HAS_AUTH:
            recommendations.append("Install python-jose and passlib for authentication")
        
        if not HAS_CRYPTOGRAPHY:
            recommendations.append("Install cryptography package for encryption features")
        
        if self.config.cors_origins == ["*"]:
            recommendations.append("Restrict CORS origins in production")
        
        if not self.config.require_https:
            recommendations.append("Require HTTPS in production")
        
        return recommendations

# Security decorators and middleware

def require_authentication(security_manager: SecurityManager):
    """Decorator to require authentication"""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            # This would integrate with FastAPI dependency injection
            # For now, it's a placeholder
            return func(*args, **kwargs)
        return wrapper
    return decorator

def audit_access(resource_name: str, action: str = "access"):
    """Decorator to audit resource access"""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Get security manager from global state or context
            # This is a simplified implementation
            try:
                result = func(*args, **kwargs)
                # Log successful access
                logger.info(f"Audit: {action} on {resource_name} succeeded")
                return result
            except Exception as e:
                # Log failed access
                logger.warning(f"Audit: {action} on {resource_name} failed: {e}")
                raise
        return wrapper
    return decorator

def validate_input(max_size_mb: int = 100):
    """Decorator to validate input size and content"""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Basic input validation
            # In practice, this would be more sophisticated
            return func(*args, **kwargs)
        return wrapper
    return decorator

# Global security manager instance
_global_security: Optional[SecurityManager] = None

def initialize_security(config: Optional[SecurityConfig] = None) -> SecurityManager:
    """Initialize global security manager"""
    global _global_security
    _global_security = SecurityManager(config)
    return _global_security

def get_security() -> Optional[SecurityManager]:
    """Get global security manager"""
    return _global_security