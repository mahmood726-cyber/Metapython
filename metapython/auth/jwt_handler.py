"""
JWT Authentication Handler

Provides:
- JWT token generation and validation
- Access and refresh tokens
- Token-based authentication
- Password reset tokens
- Email verification tokens

References:
- PyJWT: https://pyjwt.readthedocs.io/
- OAuth2 with Password flow: https://fastapi.tiangolo.com/tutorial/security/oauth2-jwt/
"""

from typing import Optional, Dict, Any
from datetime import datetime, timedelta
import os

import jwt
from jwt.exceptions import PyJWTError

from metapython.core.config import logger


class JWTConfig:
    """JWT configuration."""

    def __init__(
        self,
        secret_key: Optional[str] = None,
        algorithm: str = "HS256",
        access_token_expire_minutes: int = 30,
        refresh_token_expire_days: int = 7,
        verification_token_expire_hours: int = 24,
        password_reset_token_expire_hours: int = 1
    ):
        """
        Initialize JWT configuration.

        Args:
            secret_key: Secret key for signing tokens (default: from environment)
            algorithm: JWT algorithm
            access_token_expire_minutes: Access token expiration in minutes
            refresh_token_expire_days: Refresh token expiration in days
            verification_token_expire_hours: Email verification token expiration
            password_reset_token_expire_hours: Password reset token expiration
        """
        self.secret_key = secret_key or self._get_secret_key()
        self.algorithm = algorithm
        self.access_token_expire_minutes = access_token_expire_minutes
        self.refresh_token_expire_days = refresh_token_expire_days
        self.verification_token_expire_hours = verification_token_expire_hours
        self.password_reset_token_expire_hours = password_reset_token_expire_hours

    def _get_secret_key(self) -> str:
        """Get secret key from environment or generate."""
        secret = os.getenv("JWT_SECRET_KEY")
        if secret:
            return secret

        # Generate random secret for development
        import secrets
        logger.warning("Using generated JWT secret key. Set JWT_SECRET_KEY environment variable for production.")
        return secrets.token_urlsafe(32)


class JWTHandler:
    """
    JWT token handler for authentication.

    Features:
    - Access token generation (short-lived)
    - Refresh token generation (long-lived)
    - Token validation and decoding
    - Email verification tokens
    - Password reset tokens
    - Claims extraction

    Example:
        >>> jwt_handler = JWTHandler()
        >>> access_token = jwt_handler.create_access_token(user_id=1, username="alice")
        >>> payload = jwt_handler.decode_token(access_token)
        >>> print(payload["user_id"])  # 1
    """

    def __init__(self, config: Optional[JWTConfig] = None):
        """
        Initialize JWT handler.

        Args:
            config: JWT configuration (default: auto-detect from environment)
        """
        self.config = config or JWTConfig()

    def create_access_token(
        self,
        user_id: int,
        username: str,
        role: Optional[str] = None,
        additional_claims: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Create access token.

        Args:
            user_id: User ID
            username: Username
            role: User role
            additional_claims: Additional claims to include

        Returns:
            JWT access token
        """
        now = datetime.utcnow()
        expires = now + timedelta(minutes=self.config.access_token_expire_minutes)

        payload = {
            "user_id": user_id,
            "username": username,
            "role": role,
            "token_type": "access",
            "iat": now,
            "exp": expires,
        }

        if additional_claims:
            payload.update(additional_claims)

        token = jwt.encode(
            payload,
            self.config.secret_key,
            algorithm=self.config.algorithm
        )

        return token

    def create_refresh_token(
        self,
        user_id: int,
        username: str
    ) -> str:
        """
        Create refresh token.

        Args:
            user_id: User ID
            username: Username

        Returns:
            JWT refresh token
        """
        now = datetime.utcnow()
        expires = now + timedelta(days=self.config.refresh_token_expire_days)

        payload = {
            "user_id": user_id,
            "username": username,
            "token_type": "refresh",
            "iat": now,
            "exp": expires,
        }

        token = jwt.encode(
            payload,
            self.config.secret_key,
            algorithm=self.config.algorithm
        )

        return token

    def create_verification_token(
        self,
        user_id: int,
        email: str
    ) -> str:
        """
        Create email verification token.

        Args:
            user_id: User ID
            email: Email address

        Returns:
            Email verification token
        """
        now = datetime.utcnow()
        expires = now + timedelta(hours=self.config.verification_token_expire_hours)

        payload = {
            "user_id": user_id,
            "email": email,
            "token_type": "verification",
            "iat": now,
            "exp": expires,
        }

        token = jwt.encode(
            payload,
            self.config.secret_key,
            algorithm=self.config.algorithm
        )

        return token

    def create_password_reset_token(
        self,
        user_id: int,
        email: str
    ) -> str:
        """
        Create password reset token.

        Args:
            user_id: User ID
            email: Email address

        Returns:
            Password reset token
        """
        now = datetime.utcnow()
        expires = now + timedelta(hours=self.config.password_reset_token_expire_hours)

        payload = {
            "user_id": user_id,
            "email": email,
            "token_type": "password_reset",
            "iat": now,
            "exp": expires,
        }

        token = jwt.encode(
            payload,
            self.config.secret_key,
            algorithm=self.config.algorithm
        )

        return token

    def decode_token(
        self,
        token: str,
        expected_type: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Decode and validate JWT token.

        Args:
            token: JWT token
            expected_type: Expected token type ("access", "refresh", etc.)

        Returns:
            Token payload if valid, None otherwise
        """
        try:
            payload = jwt.decode(
                token,
                self.config.secret_key,
                algorithms=[self.config.algorithm]
            )

            # Validate token type
            if expected_type and payload.get("token_type") != expected_type:
                logger.warning(f"Invalid token type: expected {expected_type}, got {payload.get('token_type')}")
                return None

            return payload

        except jwt.ExpiredSignatureError:
            logger.warning("Token has expired")
            return None

        except PyJWTError as e:
            logger.warning(f"Token validation error: {e}")
            return None

    def verify_access_token(self, token: str) -> Optional[Dict[str, Any]]:
        """
        Verify access token.

        Args:
            token: Access token

        Returns:
            Token payload if valid
        """
        return self.decode_token(token, expected_type="access")

    def verify_refresh_token(self, token: str) -> Optional[Dict[str, Any]]:
        """
        Verify refresh token.

        Args:
            token: Refresh token

        Returns:
            Token payload if valid
        """
        return self.decode_token(token, expected_type="refresh")

    def refresh_access_token(self, refresh_token: str) -> Optional[str]:
        """
        Generate new access token from refresh token.

        Args:
            refresh_token: Valid refresh token

        Returns:
            New access token if refresh token is valid
        """
        payload = self.verify_refresh_token(refresh_token)
        if payload is None:
            return None

        # Create new access token
        return self.create_access_token(
            user_id=payload["user_id"],
            username=payload["username"],
            role=payload.get("role")
        )

    def get_token_expiration(self, token: str) -> Optional[datetime]:
        """
        Get token expiration time.

        Args:
            token: JWT token

        Returns:
            Expiration datetime
        """
        payload = self.decode_token(token)
        if payload is None or "exp" not in payload:
            return None

        return datetime.fromtimestamp(payload["exp"])

    def is_token_expired(self, token: str) -> bool:
        """
        Check if token is expired.

        Args:
            token: JWT token

        Returns:
            True if expired
        """
        exp = self.get_token_expiration(token)
        if exp is None:
            return True

        return datetime.utcnow() > exp


# Global JWT handler instance
_jwt_handler: Optional[JWTHandler] = None


def get_jwt_handler(config: Optional[JWTConfig] = None) -> JWTHandler:
    """
    Get global JWT handler instance.

    Args:
        config: Optional JWT configuration

    Returns:
        JWT handler
    """
    global _jwt_handler
    if _jwt_handler is None:
        _jwt_handler = JWTHandler(config)
    return _jwt_handler


__all__ = [
    'JWTConfig',
    'JWTHandler',
    'get_jwt_handler',
]
