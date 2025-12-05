"""
Pydantic schemas for user-related operations
"""
from pydantic import BaseModel, EmailStr, Field, ConfigDict
from typing import Optional, List
from datetime import datetime
from uuid import UUID


class UserBase(BaseModel):
    """Base user schema"""
    email: EmailStr
    first_name: Optional[str] = Field(None, max_length=100)
    last_name: Optional[str] = Field(None, max_length=100)


class UserCreate(UserBase):
    """Schema for user registration"""
    password: str = Field(..., min_length=8, max_length=100)
    role: str = Field(default="student", pattern="^(admin|instructor|student)$")


class UserUpdate(BaseModel):
    """Schema for user profile update"""
    first_name: Optional[str] = Field(None, max_length=100)
    last_name: Optional[str] = Field(None, max_length=100)
    
    model_config = ConfigDict(from_attributes=True)


class UserResponse(UserBase):
    """Schema for user response"""
    id: UUID
    role: str
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class UserWithPermissions(UserResponse):
    """User response with permissions"""
    permissions: List[str] = []


class UserInDB(UserBase):
    """Schema for user in database (includes password hash)"""
    id: UUID
    password_hash: str
    role: str
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class LoginRequest(BaseModel):
    """Schema for login request"""
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    """Schema for token response"""
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user: UserResponse


class TokenData(BaseModel):
    """Schema for JWT token payload"""
    sub: str  # user_id
    email: str
    role: str
    permissions: List[str] = []
    exp: Optional[datetime] = None


class RoleUpdate(BaseModel):
    """Schema for updating user role"""
    role: str = Field(..., pattern="^(admin|instructor|student)$")


class PaginatedUsers(BaseModel):
    """Schema for paginated user list"""
    users: List[UserResponse]
    pagination: dict

