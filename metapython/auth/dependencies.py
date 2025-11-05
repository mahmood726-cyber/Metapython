"""
FastAPI Authentication Dependencies

Provides:
- OAuth2 password flow
- Current user dependency
- Role-based authorization
- Permission checking

References:
- FastAPI Security: https://fastapi.tiangolo.com/tutorial/security/
"""

from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from metapython.database import get_session, UserCRUD, User, UserRole
from metapython.auth.jwt_handler import get_jwt_handler


# OAuth2 scheme for token authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/auth/login")

# HTTP Bearer scheme (alternative)
http_bearer = HTTPBearer()


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    session: Session = Depends(get_session)
) -> User:
    """
    Get current authenticated user from JWT token.

    Args:
        token: JWT access token
        session: Database session

    Returns:
        Current user

    Raises:
        HTTPException: If token is invalid or user not found
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    # Decode token
    jwt_handler = get_jwt_handler()
    payload = jwt_handler.verify_access_token(token)

    if payload is None:
        raise credentials_exception

    # Get user ID from payload
    user_id = payload.get("user_id")
    if user_id is None:
        raise credentials_exception

    # Fetch user from database
    user = UserCRUD.get_user_by_id(session, user_id)
    if user is None:
        raise credentials_exception

    # Check if user is active
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user"
        )

    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Get current active user.

    Args:
        current_user: Current user

    Returns:
        Current active user

    Raises:
        HTTPException: If user is inactive
    """
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    return current_user


async def get_current_verified_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Get current verified user.

    Args:
        current_user: Current user

    Returns:
        Current verified user

    Raises:
        HTTPException: If user is not verified
    """
    if not current_user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Email not verified"
        )
    return current_user


def require_role(required_role: UserRole):
    """
    Create dependency to require specific user role.

    Args:
        required_role: Required user role

    Returns:
        Dependency function

    Example:
        @app.get("/admin")
        async def admin_only(user: User = Depends(require_role(UserRole.ADMIN))):
            return {"message": "Admin access granted"}
    """
    async def role_checker(current_user: User = Depends(get_current_user)) -> User:
        # Define role hierarchy
        role_hierarchy = {
            UserRole.VIEWER: 0,
            UserRole.REVIEWER: 1,
            UserRole.RESEARCHER: 2,
            UserRole.ADMIN: 3
        }

        user_level = role_hierarchy.get(current_user.role, 0)
        required_level = role_hierarchy.get(required_role, 0)

        if user_level < required_level:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Insufficient permissions. {required_role.value} role required."
            )

        return current_user

    return role_checker


def require_admin(current_user: User = Depends(get_current_user)) -> User:
    """Require admin role."""
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user


def require_researcher(current_user: User = Depends(get_current_user)) -> User:
    """Require researcher role or higher."""
    if current_user.role not in [UserRole.RESEARCHER, UserRole.ADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Researcher access required"
        )
    return current_user


class PermissionChecker:
    """
    Check permissions for project access.

    Example:
        checker = PermissionChecker(can_edit=True)
        @app.put("/projects/{project_id}")
        async def update_project(
            project_id: int,
            user: User = Depends(checker)
        ):
            ...
    """

    def __init__(
        self,
        can_view: bool = True,
        can_edit: bool = False,
        can_delete: bool = False,
        can_publish: bool = False
    ):
        """
        Initialize permission checker.

        Args:
            can_view: Require view permission
            can_edit: Require edit permission
            can_delete: Require delete permission
            can_publish: Require publish permission
        """
        self.can_view = can_view
        self.can_edit = can_edit
        self.can_delete = can_delete
        self.can_publish = can_publish

    async def __call__(
        self,
        current_user: User = Depends(get_current_user)
    ) -> User:
        """Check permissions."""
        # Admin has all permissions
        if current_user.role == UserRole.ADMIN:
            return current_user

        # Check role-based permissions
        if self.can_delete or self.can_publish:
            if current_user.role not in [UserRole.RESEARCHER, UserRole.ADMIN]:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Insufficient permissions"
                )

        if self.can_edit:
            if current_user.role not in [UserRole.RESEARCHER, UserRole.REVIEWER, UserRole.ADMIN]:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Edit permission required"
                )

        return current_user


__all__ = [
    'oauth2_scheme',
    'http_bearer',
    'get_current_user',
    'get_current_active_user',
    'get_current_verified_user',
    'require_role',
    'require_admin',
    'require_researcher',
    'PermissionChecker',
]
