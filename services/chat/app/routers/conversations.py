"""
Conversation routes
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Annotated
from uuid import UUID
import logging

from app.database import get_db
from app.schemas.conversation import (
    ConversationCreate, 
    ConversationResponse, 
    ConversationWithMessages,
    ContextCreate
)
from app.services.conversation_service import ConversationService
from app.utils.auth import get_current_user

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/conversations", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_conversation(
    conversation_data: ConversationCreate,
    current_user: Annotated[dict, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)]
):
    """Create a new conversation"""
    service = ConversationService(db)
    conversation = await service.create_conversation(
        user_id=current_user["id"],
        title=conversation_data.title
    )
    
    return {
        "status": "success",
        "data": ConversationResponse.model_validate(conversation).model_dump()
    }


@router.get("/conversations", response_model=dict)
async def list_conversations(
    current_user: Annotated[dict, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=20, ge=1, le=100)
):
    """List user's conversations"""
    service = ConversationService(db)
    conversations, total = await service.list_conversations(
        user_id=current_user["id"],
        page=page,
        limit=limit
    )
    
    return {
        "status": "success",
        "data": {
            "conversations": [
                {
                    **ConversationResponse.model_validate(c).model_dump(),
                    "last_message": c.messages[-1].content[:100] if c.messages else None
                }
                for c in conversations
            ],
            "pagination": {
                "page": page,
                "limit": limit,
                "total": total
            }
        }
    }


@router.get("/conversations/{conversation_id}", response_model=dict)
async def get_conversation(
    conversation_id: UUID,
    current_user: Annotated[dict, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)]
):
    """Get conversation with messages"""
    service = ConversationService(db)
    conversation = await service.get_conversation(
        conversation_id=str(conversation_id),
        user_id=current_user["id"]
    )
    
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "CONVERSATION_NOT_FOUND", "message": "Conversation not found"}
        )
    
    return {
        "status": "success",
        "data": ConversationWithMessages.model_validate(conversation).model_dump()
    }


@router.delete("/conversations/{conversation_id}", response_model=dict)
async def delete_conversation(
    conversation_id: UUID,
    current_user: Annotated[dict, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)]
):
    """Delete a conversation"""
    service = ConversationService(db)
    success = await service.delete_conversation(
        conversation_id=str(conversation_id),
        user_id=current_user["id"]
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "CONVERSATION_NOT_FOUND", "message": "Conversation not found"}
        )
    
    return {
        "status": "success",
        "message": "Conversation deleted successfully"
    }


@router.post("/conversations/{conversation_id}/context", response_model=dict)
async def add_context(
    conversation_id: UUID,
    context_data: ContextCreate,
    current_user: Annotated[dict, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)]
):
    """Add document context to conversation"""
    service = ConversationService(db)
    
    # Verify conversation exists and belongs to user
    conversation = await service.get_conversation(
        conversation_id=str(conversation_id),
        user_id=current_user["id"]
    )
    
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "CONVERSATION_NOT_FOUND", "message": "Conversation not found"}
        )
    
    await service.add_context(
        conversation_id=str(conversation_id),
        document_id=str(context_data.document_id)
    )
    
    return {
        "status": "success",
        "message": "Document context added to conversation"
    }

