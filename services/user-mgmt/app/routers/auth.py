"""
Authentication routes
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Annotated
import logging

from app.database import get_db
from app.schemas.user import UserCreate, UserResponse, LoginRequest, TokenResponse
from app.services.auth_service import AuthService
from app.services.user_service import UserService
from app.utils.security import get_current_user

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/register", response_model=dict, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserCreate,
    db: Annotated[AsyncSession, Depends(get_db)]
):
    """Register a new user"""
    user_service = UserService(db)
    auth_service = AuthService(db)
    
    # Check if email already exists
    existing_user = await user_service.get_user_by_email(user_data.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "code": "USER_EMAIL_EXISTS",
                "message": "Email already registered"
            }
        )
    
    # Create user
    user = await user_service.create_user(user_data)
    
    return {
        "status": "success",
        "data": {
            "user": UserResponse.model_validate(user).model_dump()
        },
        "message": "User registered successfully"
    }


@router.post("/login", response_model=dict)
async def login(
    credentials: LoginRequest,
    db: Annotated[AsyncSession, Depends(get_db)]
):
    """Authenticate user and return JWT token"""
    auth_service = AuthService(db)
    
    # Authenticate user
    user = await auth_service.authenticate_user(credentials.email, credentials.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "code": "AUTH_INVALID_CREDENTIALS",
                "message": "Invalid email or password"
            }
        )
    
    # Generate token
    token_data = await auth_service.create_access_token(user)
    
    return {
        "status": "success",
        "data": token_data
    }


@router.post("/logout", response_model=dict)
async def logout(
    current_user: Annotated[dict, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)]
):
    """Logout current user (invalidate session)"""
    auth_service = AuthService(db)
    await auth_service.invalidate_session(current_user["id"])
    
    return {
        "status": "success",
        "message": "Logged out successfully"
    }


@router.post("/refresh", response_model=dict)
async def refresh_token(
    current_user: Annotated[dict, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)]
):
    """Refresh access token"""
    auth_service = AuthService(db)
    user_service = UserService(db)
    
    # Get fresh user data
    user = await user_service.get_user_by_id(current_user["id"])
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "code": "USER_NOT_FOUND",
                "message": "User not found"
            }
        )
    
    # Generate new token
    token_data = await auth_service.create_access_token(user)
    
    return {
        "status": "success",
        "data": {
            "access_token": token_data["access_token"],
            "expires_in": token_data["expires_in"]
        }
    }


@router.get("/health")
async def health():
    """Health check for auth routes"""
    return {
        "status": "healthy",
        "service": "user-mgmt",
        "version": "1.0.0"
    }

