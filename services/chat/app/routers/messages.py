"""
Message routes
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Annotated
from uuid import UUID
import logging

from app.database import get_db
from app.schemas.conversation import MessageCreate, MessageResponse
from app.services.conversation_service import ConversationService
from app.services.chat_service import ChatService
from app.utils.auth import get_current_user

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/conversations/{conversation_id}/messages", response_model=dict)
async def send_message(
    conversation_id: UUID,
    message_data: MessageCreate,
    current_user: Annotated[dict, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)]
):
    """Send a message and get AI response"""
    conv_service = ConversationService(db)
    chat_service = ChatService(db)
    
    # Verify conversation exists and belongs to user
    conversation = await conv_service.get_conversation(
        conversation_id=str(conversation_id),
        user_id=current_user["id"]
    )
    
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "CONVERSATION_NOT_FOUND", "message": "Conversation not found"}
        )
    
    # Save user message
    user_message = await conv_service.add_message(
        conversation_id=str(conversation_id),
        role="user",
        content=message_data.content
    )
    
    # Get AI response
    ai_response = await chat_service.get_ai_response(
        conversation=conversation,
        user_message=message_data.content
    )
    
    # Save assistant message
    assistant_message = await conv_service.add_message(
        conversation_id=str(conversation_id),
        role="assistant",
        content=ai_response
    )
    
    return {
        "status": "success",
        "data": {
            "user_message": MessageResponse.model_validate(user_message).model_dump(),
            "assistant_message": MessageResponse.model_validate(assistant_message).model_dump()
        }
    }

