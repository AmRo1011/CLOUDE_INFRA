"""
Authentication utilities
"""
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from datetime import datetime, timezone
from typing import Callable
import logging

from app.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()
security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> dict:
    """Validate JWT and get current user"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail={"code": "AUTH_TOKEN_INVALID", "message": "Could not validate credentials"},
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(credentials.credentials, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
        
        exp = payload.get("exp")
        if exp and datetime.fromtimestamp(exp, tz=timezone.utc) < datetime.now(timezone.utc):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={"code": "AUTH_TOKEN_EXPIRED", "message": "Token has expired"}
            )
        
        user_id = payload.get("sub")
        if not user_id:
            raise credentials_exception
        
        return {
            "id": user_id,
            "email": payload.get("email"),
            "role": payload.get("role"),
            "permissions": payload.get("permissions", [])
        }
    except JWTError:
        raise credentials_exception


def require_permission(permission: str) -> Callable:
    """Require specific permission"""
    async def checker(current_user: dict = Depends(get_current_user)) -> dict:
        if current_user.get("role") == "admin":
            return current_user
        if permission not in current_user.get("permissions", []):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={"code": "AUTH_INSUFFICIENT_PERMISSIONS", "message": f"Permission '{permission}' required"}
            )
        return current_user
    return checker

