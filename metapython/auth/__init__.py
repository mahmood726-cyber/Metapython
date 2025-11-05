"""
Authentication Module

Complete authentication system with:
- JWT token-based authentication
- OAuth2 password flow
- User registration and login
- Email verification
- Password reset
- Role-based authorization
- Permission checking

Usage:
    >>> from metapython.auth import get_jwt_handler, get_current_user
    >>>
    >>> # Create tokens
    >>> jwt_handler = get_jwt_handler()
    >>> access_token = jwt_handler.create_access_token(
    ...     user_id=1,
    ...     username="researcher"
    ... )
    >>>
    >>> # Use in FastAPI
    >>> @app.get("/protected")
    >>> async def protected_route(user: User = Depends(get_current_user)):
    ...     return {"user": user.username}
"""

# JWT handling
from metapython.auth.jwt_handler import (
    JWTConfig,
    JWTHandler,
    get_jwt_handler,
)

# Dependencies
from metapython.auth.dependencies import (
    oauth2_scheme,
    http_bearer,
    get_current_user,
    get_current_active_user,
    get_current_verified_user,
    require_role,
    require_admin,
    require_researcher,
    PermissionChecker,
)

# Routes
from metapython.auth.routes import router as auth_router

__all__ = [
    # JWT
    'JWTConfig',
    'JWTHandler',
    'get_jwt_handler',

    # Dependencies
    'oauth2_scheme',
    'http_bearer',
    'get_current_user',
    'get_current_active_user',
    'get_current_verified_user',
    'require_role',
    'require_admin',
    'require_researcher',
    'PermissionChecker',

    # Router
    'auth_router',
]
