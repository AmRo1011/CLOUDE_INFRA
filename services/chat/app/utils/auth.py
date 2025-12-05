"""
Authentication utilities (JWT validation)
"""
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from datetime import datetime, timezone
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
        token = credentials.credentials
        payload = jwt.decode(
            token,
            settings.JWT_SECRET,
            algorithms=[settings.JWT_ALGORITHM]
        )
        
        # Check expiration
        exp = payload.get("exp")
        if exp and datetime.fromtimestamp(exp, tz=timezone.utc) < datetime.now(timezone.utc):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={"code": "AUTH_TOKEN_EXPIRED", "message": "Token has expired"},
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        user_id = payload.get("sub")
        if user_id is None:
            raise credentials_exception
        
        return {
            "id": user_id,
            "email": payload.get("email"),
            "role": payload.get("role"),
            "permissions": payload.get("permissions", [])
        }
        
    except JWTError as e:
        logger.warning(f"JWT validation failed: {e}")
        raise credentials_exception

