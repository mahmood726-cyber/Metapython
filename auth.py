"""
Enterprise Authentication and Multi-Tenancy - Phase 8
OIDC/OAuth2 authentication, RBAC, multi-tenant namespace scoping
"""

import os
import time
import json
import logging
from typing import Dict, Any, Optional, List, Set, Callable, Union
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import threading
import hashlib
import secrets
from functools import wraps

# FastAPI authentication (optional)
try:
    from fastapi import HTTPException, Depends, status, Request
    from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials, OAuth2PasswordBearer
    from fastapi.responses import RedirectResponse
    HAS_FASTAPI = True
except ImportError:
    HAS_FASTAPI = False

# OIDC/OAuth2 support (optional)
try:
    from authlib.integrations.starlette_client import OAuth
    from authlib.integrations.starlette_client import OAuthError
    from authlib.jose import JsonWebToken, JWTClaims
    import httpx
    HAS_OAUTH = True
except ImportError:
    HAS_OAUTH = False

# JWT handling (optional)
try:
    from jose import JWTError, jwt
    from passlib.context import CryptContext
    HAS_JWT = True
except ImportError:
    HAS_JWT = False

logger = logging.getLogger(__name__)

class UserRole(Enum):
    """User roles for RBAC"""
    VIEWER = "viewer"
    RUNNER = "runner"
    ADMIN = "admin"
    TENANT_ADMIN = "tenant_admin"

class Permission(Enum):
    """System permissions"""
    READ_DATA = "read_data"
    WRITE_DATA = "write_data"
    RUN_ANALYSIS = "run_analysis"
    MANAGE_USERS = "manage_users"
    VIEW_AUDIT_LOGS = "view_audit_logs"
    MANAGE_TENANTS = "manage_tenants"
    SYSTEM_CONFIG = "system_config"

@dataclass
class User:
    """User representation"""
    user_id: str
    email: str
    name: str
    roles: List[UserRole]
    tenant_id: Optional[str] = None
    is_active: bool = True
    created_at: datetime = field(default_factory=datetime.utcnow)
    last_login: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def has_role(self, role: UserRole) -> bool:
        """Check if user has specific role"""
        return role in self.roles
    
    def has_permission(self, permission: Permission) -> bool:
        """Check if user has specific permission"""
        role_permissions = {
            UserRole.VIEWER: {Permission.READ_DATA},
            UserRole.RUNNER: {Permission.READ_DATA, Permission.RUN_ANALYSIS},
            UserRole.ADMIN: {Permission.READ_DATA, Permission.WRITE_DATA, 
                           Permission.RUN_ANALYSIS, Permission.VIEW_AUDIT_LOGS},
            UserRole.TENANT_ADMIN: {Permission.READ_DATA, Permission.WRITE_DATA, 
                                  Permission.RUN_ANALYSIS, Permission.MANAGE_USERS,
                                  Permission.VIEW_AUDIT_LOGS}
        }
        
        for role in self.roles:
            if permission in role_permissions.get(role, set()):
                return True
        return False

@dataclass
class Tenant:
    """Tenant representation for multi-tenancy"""
    tenant_id: str
    name: str
    description: str = ""
    is_active: bool = True
    created_at: datetime = field(default_factory=datetime.utcnow)
    settings: Dict[str, Any] = field(default_factory=dict)
    quotas: Dict[str, int] = field(default_factory=dict)
    retention_policy: Dict[str, Any] = field(default_factory=dict)
    
    def get_quota(self, resource_type: str) -> Optional[int]:
        """Get quota for specific resource type"""
        return self.quotas.get(resource_type)
    
    def get_retention_days(self, data_type: str) -> int:
        """Get retention period for data type"""
        return self.retention_policy.get(data_type, 90)  # Default 90 days

@dataclass
class AuthConfig:
    """Authentication configuration"""
    # OIDC/OAuth2 settings
    enable_oidc: bool = False
    oidc_issuer_url: Optional[str] = None
    oidc_client_id: Optional[str] = None
    oidc_client_secret: Optional[str] = None
    oidc_redirect_uri: Optional[str] = None
    
    # JWT settings
    jwt_secret_key: str = field(default_factory=lambda: secrets.token_urlsafe(32))
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7
    
    # API token settings
    enable_api_tokens: bool = True
    api_token_expire_days: int = 365
    
    # Multi-tenancy
    enable_multi_tenancy: bool = False
    default_tenant_id: str = "default"
    
    # Session settings
    session_timeout_minutes: int = 480  # 8 hours
    max_concurrent_sessions: int = 5

class APITokenManager:
    """Manage API tokens for authentication"""
    
    def __init__(self):
        self.tokens: Dict[str, Dict[str, Any]] = {}
        self.lock = threading.Lock()
    
    def generate_token(self, user_id: str, tenant_id: str, 
                      expires_in_days: int = 365, 
                      scopes: List[str] = None) -> str:
        """Generate API token for user"""
        token = secrets.token_urlsafe(32)
        
        with self.lock:
            self.tokens[token] = {
                'user_id': user_id,
                'tenant_id': tenant_id,
                'created_at': datetime.utcnow(),
                'expires_at': datetime.utcnow() + timedelta(days=expires_in_days),
                'scopes': scopes or [],
                'last_used': None,
                'usage_count': 0
            }
        
        logger.info(f"Generated API token for user {user_id}")
        return token
    
    def validate_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Validate API token and return token info"""
        with self.lock:
            token_info = self.tokens.get(token)
            
            if not token_info:
                return None
            
            # Check expiration
            if datetime.utcnow() > token_info['expires_at']:
                del self.tokens[token]
                return None
            
            # Update usage
            token_info['last_used'] = datetime.utcnow()
            token_info['usage_count'] += 1
            
            return token_info.copy()
    
    def revoke_token(self, token: str) -> bool:
        """Revoke API token"""
        with self.lock:
            if token in self.tokens:
                del self.tokens[token]
                logger.info(f"Revoked API token")
                return True
            return False
    
    def list_user_tokens(self, user_id: str) -> List[Dict[str, Any]]:
        """List all tokens for a user"""
        with self.lock:
            user_tokens = []
            for token, info in self.tokens.items():
                if info['user_id'] == user_id:
                    user_tokens.append({
                        'token_preview': token[:8] + '...',
                        'created_at': info['created_at'],
                        'expires_at': info['expires_at'],
                        'last_used': info['last_used'],
                        'usage_count': info['usage_count'],
                        'scopes': info['scopes']
                    })
            return user_tokens

class OIDCProvider:
    """OIDC/OAuth2 authentication provider"""
    
    def __init__(self, config: AuthConfig):
        self.config = config
        self.oauth_client = None
        
        if HAS_OAUTH and config.enable_oidc:
            self._setup_oauth_client()
    
    def _setup_oauth_client(self):
        """Setup OAuth client"""
        try:
            self.oauth_client = OAuth()
            self.oauth_client.register(
                name='oidc',
                client_id=self.config.oidc_client_id,
                client_secret=self.config.oidc_client_secret,
                server_metadata_url=f"{self.config.oidc_issuer_url}/.well-known/openid_configuration",
                client_kwargs={
                    'scope': 'openid profile email'
                }
            )
            logger.info("OIDC client configured successfully")
        except Exception as e:
            logger.error(f"Failed to setup OIDC client: {e}")
            self.oauth_client = None
    
    async def get_authorization_url(self, redirect_uri: str, state: str = None) -> str:
        """Get authorization URL for OIDC flow"""
        if not self.oauth_client:
            raise ValueError("OIDC not configured")
        
        # Generate state if not provided
        if state is None:
            state = secrets.token_urlsafe(32)
        
        authorization_url = await self.oauth_client.oidc.authorize_redirect(
            redirect_uri, state=state
        )
        return authorization_url
    
    async def exchange_code_for_token(self, code: str, redirect_uri: str) -> Dict[str, Any]:
        """Exchange authorization code for access token"""
        if not self.oauth_client:
            raise ValueError("OIDC not configured")
        
        try:
            token = await self.oauth_client.oidc.authorize_access_token()
            
            # Parse ID token
            id_token = token.get('id_token')
            if id_token:
                # Verify and decode ID token
                claims = self._verify_id_token(id_token)
                
                return {
                    'access_token': token.get('access_token'),
                    'id_token': id_token,
                    'claims': claims,
                    'expires_in': token.get('expires_in', 3600)
                }
            else:
                raise ValueError("No ID token received")
        
        except Exception as e:
            logger.error(f"Token exchange failed: {e}")
            raise
    
    def _verify_id_token(self, id_token: str) -> Dict[str, Any]:
        """Verify and decode ID token"""
        if not HAS_JWT:
            raise ValueError("JWT library not available")
        
        try:
            # In production, you would fetch and verify against OIDC keys
            # This is a simplified implementation
            unverified_claims = jwt.get_unverified_claims(id_token)
            
            # Basic validation
            now = time.time()
            if unverified_claims.get('exp', 0) < now:
                raise ValueError("Token expired")
            
            if unverified_claims.get('iss') != self.config.oidc_issuer_url:
                raise ValueError("Invalid issuer")
            
            return unverified_claims
        
        except Exception as e:
            logger.error(f"ID token verification failed: {e}")
            raise

class UserManager:
    """User management with RBAC"""
    
    def __init__(self):
        self.users: Dict[str, User] = {}
        self.lock = threading.Lock()
        self._create_default_admin()
    
    def _create_default_admin(self):
        """Create default admin user"""
        admin_user = User(
            user_id="admin",
            email="admin@metapython.local",
            name="System Administrator",
            roles=[UserRole.ADMIN],
            tenant_id="default"
        )
        self.users["admin"] = admin_user
    
    def create_user(self, user_id: str, email: str, name: str,
                   roles: List[UserRole], tenant_id: str = "default") -> User:
        """Create new user"""
        with self.lock:
            if user_id in self.users:
                raise ValueError(f"User {user_id} already exists")
            
            user = User(
                user_id=user_id,
                email=email,
                name=name,
                roles=roles,
                tenant_id=tenant_id
            )
            
            self.users[user_id] = user
            logger.info(f"Created user {user_id} with roles {[r.value for r in roles]}")
            return user
    
    def get_user(self, user_id: str) -> Optional[User]:
        """Get user by ID"""
        return self.users.get(user_id)
    
    def update_user_roles(self, user_id: str, roles: List[UserRole]) -> bool:
        """Update user roles"""
        with self.lock:
            user = self.users.get(user_id)
            if user:
                user.roles = roles
                logger.info(f"Updated roles for user {user_id}: {[r.value for r in roles]}")
                return True
            return False
    
    def deactivate_user(self, user_id: str) -> bool:
        """Deactivate user"""
        with self.lock:
            user = self.users.get(user_id)
            if user:
                user.is_active = False
                logger.info(f"Deactivated user {user_id}")
                return True
            return False
    
    def list_users(self, tenant_id: Optional[str] = None) -> List[User]:
        """List users, optionally filtered by tenant"""
        users = list(self.users.values())
        if tenant_id:
            users = [u for u in users if u.tenant_id == tenant_id]
        return users
    
    def update_last_login(self, user_id: str):
        """Update user's last login time"""
        user = self.users.get(user_id)
        if user:
            user.last_login = datetime.utcnow()

class TenantManager:
    """Multi-tenant management"""
    
    def __init__(self):
        self.tenants: Dict[str, Tenant] = {}
        self.lock = threading.Lock()
        self._create_default_tenant()
    
    def _create_default_tenant(self):
        """Create default tenant"""
        default_tenant = Tenant(
            tenant_id="default",
            name="Default Tenant",
            description="Default tenant for single-tenant deployments",
            quotas={
                'max_analyses_per_day': 1000,
                'max_file_size_mb': 500,
                'max_concurrent_analyses': 10
            },
            retention_policy={
                'analysis_results': 90,
                'audit_logs': 365,
                'temporary_files': 7
            }
        )
        self.tenants["default"] = default_tenant
    
    def create_tenant(self, tenant_id: str, name: str, description: str = "",
                     quotas: Dict[str, int] = None,
                     retention_policy: Dict[str, int] = None) -> Tenant:
        """Create new tenant"""
        with self.lock:
            if tenant_id in self.tenants:
                raise ValueError(f"Tenant {tenant_id} already exists")
            
            tenant = Tenant(
                tenant_id=tenant_id,
                name=name,
                description=description,
                quotas=quotas or {},
                retention_policy=retention_policy or {}
            )
            
            self.tenants[tenant_id] = tenant
            logger.info(f"Created tenant {tenant_id}: {name}")
            return tenant
    
    def get_tenant(self, tenant_id: str) -> Optional[Tenant]:
        """Get tenant by ID"""
        return self.tenants.get(tenant_id)
    
    def update_tenant_quotas(self, tenant_id: str, quotas: Dict[str, int]) -> bool:
        """Update tenant quotas"""
        with self.lock:
            tenant = self.tenants.get(tenant_id)
            if tenant:
                tenant.quotas.update(quotas)
                logger.info(f"Updated quotas for tenant {tenant_id}")
                return True
            return False
    
    def check_quota(self, tenant_id: str, resource_type: str, 
                   current_usage: int) -> bool:
        """Check if tenant is within quota"""
        tenant = self.tenants.get(tenant_id)
        if not tenant:
            return False
        
        quota = tenant.get_quota(resource_type)
        if quota is None:
            return True  # No quota limit
        
        return current_usage < quota
    
    def list_tenants(self) -> List[Tenant]:
        """List all tenants"""
        return list(self.tenants.values())

class AuthenticationManager:
    """Central authentication management"""
    
    def __init__(self, config: AuthConfig):
        self.config = config
        self.user_manager = UserManager()
        self.tenant_manager = TenantManager()
        self.api_token_manager = APITokenManager()
        self.oidc_provider = OIDCProvider(config) if config.enable_oidc else None
        self.pwd_context = None
        
        if HAS_JWT:
            self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    
    def authenticate_with_credentials(self, username: str, password: str) -> Optional[User]:
        """Authenticate user with username/password"""
        user = self.user_manager.get_user(username)
        if not user or not user.is_active:
            return None
        
        # In a real implementation, you would verify the password hash
        # This is a simplified version
        if username == "admin" and password == "admin":
            self.user_manager.update_last_login(username)
            return user
        
        return None
    
    def authenticate_with_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Authenticate user with API token"""
        token_info = self.api_token_manager.validate_token(token)
        if not token_info:
            return None
        
        user = self.user_manager.get_user(token_info['user_id'])
        if not user or not user.is_active:
            return None
        
        return {
            'user': user,
            'token_info': token_info
        }
    
    def create_access_token(self, user: User, expires_delta: Optional[timedelta] = None) -> str:
        """Create JWT access token"""
        if not HAS_JWT:
            raise ValueError("JWT library not available")
        
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=self.config.access_token_expire_minutes)
        
        to_encode = {
            "sub": user.user_id,
            "email": user.email,
            "name": user.name,
            "roles": [role.value for role in user.roles],
            "tenant_id": user.tenant_id,
            "exp": expire
        }
        
        encoded_jwt = jwt.encode(
            to_encode,
            self.config.jwt_secret_key,
            algorithm=self.config.jwt_algorithm
        )
        return encoded_jwt
    
    def verify_access_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Verify JWT access token"""
        if not HAS_JWT:
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
    
    def check_permission(self, user: User, permission: Permission,
                        resource_tenant_id: Optional[str] = None) -> bool:
        """Check if user has permission for resource"""
        # Basic permission check
        if not user.has_permission(permission):
            return False
        
        # Multi-tenancy check
        if self.config.enable_multi_tenancy and resource_tenant_id:
            # Users can only access resources in their tenant
            # unless they're system admins
            if user.tenant_id != resource_tenant_id and UserRole.ADMIN not in user.roles:
                return False
        
        return True
    
    def get_user_context(self, user: User) -> Dict[str, Any]:
        """Get user context for request processing"""
        tenant = self.tenant_manager.get_tenant(user.tenant_id)
        
        return {
            'user_id': user.user_id,
            'email': user.email,
            'name': user.name,
            'roles': [role.value for role in user.roles],
            'tenant_id': user.tenant_id,
            'tenant_name': tenant.name if tenant else None,
            'permissions': [perm.value for perm in Permission if user.has_permission(perm)]
        }

# FastAPI dependencies for authentication
if HAS_FASTAPI:
    security = HTTPBearer()
    
    def get_current_user(auth_manager: AuthenticationManager):
        """FastAPI dependency for getting current user"""
        def _get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
            token = credentials.credentials
            
            # Try JWT token first
            payload = auth_manager.verify_access_token(token)
            if payload:
                user = auth_manager.user_manager.get_user(payload.get("sub"))
                if user and user.is_active:
                    return user
            
            # Try API token
            auth_result = auth_manager.authenticate_with_token(token)
            if auth_result:
                return auth_result['user']
            
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        return _get_current_user
    
    def require_permission(permission: Permission):
        """FastAPI dependency for requiring specific permission"""
        def _require_permission(user: User = Depends(get_current_user)):
            if not user.has_permission(permission):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Insufficient permissions: {permission.value} required"
                )
            return user
        
        return _require_permission
    
    def require_tenant_access(tenant_id: str):
        """FastAPI dependency for requiring tenant access"""
        def _require_tenant_access(user: User = Depends(get_current_user)):
            if user.tenant_id != tenant_id and UserRole.ADMIN not in user.roles:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Access denied to tenant {tenant_id}"
                )
            return user
        
        return _require_tenant_access

# Global authentication manager instance
_global_auth: Optional[AuthenticationManager] = None

def initialize_auth(config: Optional[AuthConfig] = None) -> AuthenticationManager:
    """Initialize global authentication manager"""
    global _global_auth
    _global_auth = AuthenticationManager(config or AuthConfig())
    return _global_auth

def get_auth() -> Optional[AuthenticationManager]:
    """Get global authentication manager"""
    return _global_auth

# Authentication decorators
def requires_auth(permission: Optional[Permission] = None):
    """Decorator to require authentication and optional permission"""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            # This would integrate with request context in a real application
            # For now, it's a placeholder
            return func(*args, **kwargs)
        return wrapper
    return decorator

def tenant_scoped(func: Callable) -> Callable:
    """Decorator to scope function to user's tenant"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        # Extract tenant context and filter data
        # This would be implemented based on the specific framework
        return func(*args, **kwargs)
    return wrapper