"""
Authentication service
"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime, timedelta, timezone
from typing import Optional
import logging

from app.models.user import User, UserSession
from app.utils.security import verify_password, create_access_token, get_password_hash
from app.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class AuthService:
    """Service for authentication operations"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def authenticate_user(self, email: str, password: str) -> Optional[User]:
        """Authenticate user with email and password"""
        # Get user by email
        result = await self.db.execute(
            select(User).where(User.email == email, User.is_active == True)
        )
        user = result.scalar_one_or_none()
        
        if not user:
            logger.warning(f"Authentication failed: user {email} not found")
            return None
        
        # Verify password
        if not verify_password(password, user.password_hash):
            logger.warning(f"Authentication failed: invalid password for {email}")
            return None
        
        logger.info(f"User {email} authenticated successfully")
        return user
    
    async def create_access_token(self, user: User) -> dict:
        """Create JWT access token for user"""
        from app.services.user_service import UserService
        
        # Get user permissions
        user_service = UserService(self.db)
        permissions = await user_service.get_role_permissions(user.role)
        
        # Create token
        token_data = {
            "sub": str(user.id),
            "email": user.email,
            "role": user.role,
            "permissions": permissions
        }
        
        expires_delta = timedelta(hours=settings.JWT_EXPIRATION_HOURS)
        access_token = create_access_token(token_data, expires_delta)
        
        # Create session record
        await self._create_session(user.id, access_token, expires_delta)
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "expires_in": int(expires_delta.total_seconds()),
            "user": {
                "id": str(user.id),
                "email": user.email,
                "role": user.role
            }
        }
    
    async def _create_session(self, user_id: str, token: str, expires_delta: timedelta):
        """Create session record in database"""
        session = UserSession(
            user_id=user_id,
            token_hash=get_password_hash(token[:50]),  # Hash part of token
            expires_at=datetime.now(timezone.utc) + expires_delta
        )
        self.db.add(session)
        await self.db.flush()
    
    async def invalidate_session(self, user_id: str):
        """Invalidate all sessions for a user"""
        result = await self.db.execute(
            select(UserSession).where(UserSession.user_id == user_id)
        )
        sessions = result.scalars().all()
        
        for session in sessions:
            await self.db.delete(session)
        
        await self.db.flush()
        logger.info(f"All sessions invalidated for user {user_id}")

