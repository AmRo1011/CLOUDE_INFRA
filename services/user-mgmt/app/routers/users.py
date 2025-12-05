"""
User management routes
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Annotated, Optional
from uuid import UUID
import logging

from app.database import get_db
from app.schemas.user import UserResponse, UserUpdate, UserWithPermissions, RoleUpdate, PaginatedUsers
from app.services.user_service import UserService
from app.utils.security import get_current_user, require_permission

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/me", response_model=dict)
async def get_current_user_profile(
    current_user: Annotated[dict, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)]
):
    """Get current user's profile"""
    user_service = UserService(db)
    user = await user_service.get_user_by_id(current_user["id"])
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "USER_NOT_FOUND", "message": "User not found"}
        )
    
    # Get permissions for the user's role
    permissions = await user_service.get_role_permissions(user.role)
    
    return {
        "status": "success",
        "data": {
            **UserResponse.model_validate(user).model_dump(),
            "permissions": permissions
        }
    }


@router.put("/me", response_model=dict)
async def update_current_user_profile(
    user_update: UserUpdate,
    current_user: Annotated[dict, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)]
):
    """Update current user's profile"""
    user_service = UserService(db)
    
    updated_user = await user_service.update_user(current_user["id"], user_update)
    
    if not updated_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "USER_NOT_FOUND", "message": "User not found"}
        )
    
    return {
        "status": "success",
        "data": UserResponse.model_validate(updated_user).model_dump()
    }


@router.get("/", response_model=dict)
async def list_users(
    current_user: Annotated[dict, Depends(require_permission("user.manage"))],
    db: Annotated[AsyncSession, Depends(get_db)],
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=20, ge=1, le=100),
    role: Optional[str] = Query(default=None, pattern="^(admin|instructor|student)$")
):
    """List all users (admin only)"""
    user_service = UserService(db)
    
    users, total = await user_service.list_users(page=page, limit=limit, role=role)
    
    return {
        "status": "success",
        "data": {
            "users": [UserResponse.model_validate(u).model_dump() for u in users],
            "pagination": {
                "page": page,
                "limit": limit,
                "total": total,
                "pages": (total + limit - 1) // limit
            }
        }
    }


@router.get("/{user_id}", response_model=dict)
async def get_user(
    user_id: UUID,
    current_user: Annotated[dict, Depends(require_permission("user.manage"))],
    db: Annotated[AsyncSession, Depends(get_db)]
):
    """Get user by ID (admin only)"""
    user_service = UserService(db)
    user = await user_service.get_user_by_id(str(user_id))
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "USER_NOT_FOUND", "message": "User not found"}
        )
    
    return {
        "status": "success",
        "data": UserResponse.model_validate(user).model_dump()
    }


@router.put("/{user_id}/role", response_model=dict)
async def update_user_role(
    user_id: UUID,
    role_update: RoleUpdate,
    current_user: Annotated[dict, Depends(require_permission("user.manage"))],
    db: Annotated[AsyncSession, Depends(get_db)]
):
    """Update user role (admin only)"""
    user_service = UserService(db)
    
    # Don't allow changing own role
    if str(user_id) == current_user["id"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"code": "INVALID_OPERATION", "message": "Cannot change your own role"}
        )
    
    updated_user = await user_service.update_user_role(str(user_id), role_update.role)
    
    if not updated_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "USER_NOT_FOUND", "message": "User not found"}
        )
    
    return {
        "status": "success",
        "message": "User role updated successfully"
    }


@router.delete("/{user_id}", response_model=dict)
async def delete_user(
    user_id: UUID,
    current_user: Annotated[dict, Depends(require_permission("user.manage"))],
    db: Annotated[AsyncSession, Depends(get_db)]
):
    """Delete user (admin only)"""
    user_service = UserService(db)
    
    # Don't allow deleting own account
    if str(user_id) == current_user["id"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"code": "INVALID_OPERATION", "message": "Cannot delete your own account"}
        )
    
    success = await user_service.delete_user(str(user_id))
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "USER_NOT_FOUND", "message": "User not found"}
        )
    
    return {
        "status": "success",
        "message": "User deleted successfully"
    }

