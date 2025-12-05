"""
User service for user management operations
"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import Optional, List, Tuple
import logging

from app.models.user import User, Role, Permission, RolePermission
from app.schemas.user import UserCreate, UserUpdate
from app.utils.security import get_password_hash

logger = logging.getLogger(__name__)

# Default role permissions mapping
DEFAULT_PERMISSIONS = {
    "admin": [
        "user.manage", "user.view",
        "document.upload", "document.view", "document.delete",
        "quiz.create", "quiz.take", "quiz.grade",
        "chat.use"
    ],
    "instructor": [
        "user.view",
        "document.upload", "document.view", "document.delete",
        "quiz.create", "quiz.take", "quiz.grade",
        "chat.use"
    ],
    "student": [
        "document.view",
        "quiz.take",
        "chat.use"
    ]
}


class UserService:
    """Service for user management operations"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create_user(self, user_data: UserCreate) -> User:
        """Create a new user"""
        # Hash password
        password_hash = get_password_hash(user_data.password)
        
        # Create user
        user = User(
            email=user_data.email,
            password_hash=password_hash,
            first_name=user_data.first_name,
            last_name=user_data.last_name,
            role=user_data.role
        )
        
        self.db.add(user)
        await self.db.flush()
        await self.db.refresh(user)
        
        logger.info(f"Created user: {user.email}")
        return user
    
    async def get_user_by_id(self, user_id: str) -> Optional[User]:
        """Get user by ID"""
        result = await self.db.execute(
            select(User).where(User.id == user_id)
        )
        return result.scalar_one_or_none()
    
    async def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email"""
        result = await self.db.execute(
            select(User).where(User.email == email)
        )
        return result.scalar_one_or_none()
    
    async def update_user(self, user_id: str, user_data: UserUpdate) -> Optional[User]:
        """Update user profile"""
        user = await self.get_user_by_id(user_id)
        if not user:
            return None
        
        # Update fields
        update_data = user_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(user, field, value)
        
        await self.db.flush()
        await self.db.refresh(user)
        
        logger.info(f"Updated user: {user.email}")
        return user
    
    async def update_user_role(self, user_id: str, role: str) -> Optional[User]:
        """Update user role"""
        user = await self.get_user_by_id(user_id)
        if not user:
            return None
        
        user.role = role
        await self.db.flush()
        await self.db.refresh(user)
        
        logger.info(f"Updated role for user {user.email} to {role}")
        return user
    
    async def delete_user(self, user_id: str) -> bool:
        """Delete user"""
        user = await self.get_user_by_id(user_id)
        if not user:
            return False
        
        await self.db.delete(user)
        await self.db.flush()
        
        logger.info(f"Deleted user: {user.email}")
        return True
    
    async def list_users(
        self, 
        page: int = 1, 
        limit: int = 20, 
        role: Optional[str] = None
    ) -> Tuple[List[User], int]:
        """List users with pagination"""
        # Build query
        query = select(User)
        count_query = select(func.count(User.id))
        
        if role:
            query = query.where(User.role == role)
            count_query = count_query.where(User.role == role)
        
        # Get total count
        total_result = await self.db.execute(count_query)
        total = total_result.scalar() or 0
        
        # Get paginated users
        offset = (page - 1) * limit
        query = query.offset(offset).limit(limit).order_by(User.created_at.desc())
        
        result = await self.db.execute(query)
        users = result.scalars().all()
        
        return list(users), total
    
    async def get_role_permissions(self, role: str) -> List[str]:
        """Get permissions for a role"""
        # Try to get from database first
        try:
            result = await self.db.execute(
                select(Permission.name)
                .join(RolePermission, Permission.id == RolePermission.permission_id)
                .join(Role, Role.id == RolePermission.role_id)
                .where(Role.name == role)
            )
            permissions = [p for p in result.scalars().all()]
            if permissions:
                return permissions
        except Exception as e:
            logger.warning(f"Could not fetch permissions from DB: {e}")
        
        # Fall back to default permissions
        return DEFAULT_PERMISSIONS.get(role, [])

