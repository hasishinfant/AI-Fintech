"""Authentication and authorization utilities."""

from datetime import datetime, timedelta, UTC
from typing import Optional
from uuid import UUID
import jwt
from fastapi import Depends, HTTPException, status, Header

from app.core.config import settings


class TokenData:
    """Token payload data."""
    def __init__(self, user_id: UUID, role: str, exp: datetime):
        self.user_id = user_id
        self.role = role
        self.exp = exp


def create_access_token(user_id: UUID, role: str, expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT access token."""
    if expires_delta:
        expire = datetime.now(UTC) + expires_delta
    else:
        expire = datetime.now(UTC) + timedelta(hours=24)

    payload = {
        "user_id": str(user_id),
        "role": role,
        "exp": expire,
        "iat": datetime.now(UTC)
    }

    encoded_jwt = jwt.encode(
        payload,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )
    return encoded_jwt


def verify_token(token: str) -> TokenData:
    """Verify and decode JWT token."""
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        user_id: str = payload.get("user_id")
        role: str = payload.get("role")
        exp: int = payload.get("exp")

        if user_id is None or role is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )

        return TokenData(
            user_id=UUID(user_id),
            role=role,
            exp=datetime.fromtimestamp(exp)
        )
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired"
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )


async def get_current_user(authorization: Optional[str] = Header(None)) -> TokenData:
    """Get current authenticated user from token."""
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authorization header"
        )
    
    try:
        scheme, token = authorization.split()
        if scheme.lower() != "bearer":
            raise ValueError("Invalid scheme")
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorization header format"
        )
    
    return verify_token(token)


async def require_credit_officer(current_user: TokenData = Depends(get_current_user)) -> TokenData:
    """Require user to have Credit Officer role."""
    if current_user.role != "credit_officer":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Operation requires Credit Officer role"
        )
    return current_user
