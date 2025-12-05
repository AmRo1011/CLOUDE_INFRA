"""
Pydantic schemas for conversations and messages
"""
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List, Any
from datetime import datetime
from uuid import UUID


class MessageBase(BaseModel):
    """Base message schema"""
    content: str = Field(..., min_length=1, max_length=10000)


class MessageCreate(MessageBase):
    """Schema for creating a message"""
    pass


class MessageResponse(BaseModel):
    """Message response schema"""
    id: UUID
    role: str
    content: str
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class ConversationBase(BaseModel):
    """Base conversation schema"""
    title: Optional[str] = Field(None, max_length=255)


class ConversationCreate(ConversationBase):
    """Schema for creating a conversation"""
    pass


class ContextResponse(BaseModel):
    """Context response schema"""
    type: str
    document_id: Optional[UUID] = None
    title: Optional[str] = None
    
    model_config = ConfigDict(from_attributes=True)


class ConversationResponse(BaseModel):
    """Conversation response schema"""
    id: UUID
    title: Optional[str]
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class ConversationWithMessages(ConversationResponse):
    """Conversation with messages"""
    messages: List[MessageResponse] = []
    context: List[ContextResponse] = []


class ConversationListItem(BaseModel):
    """Conversation list item"""
    id: UUID
    title: Optional[str]
    last_message: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class ContextCreate(BaseModel):
    """Schema for adding context"""
    document_id: UUID


class ChatResponse(BaseModel):
    """Response from chat AI"""
    user_message: MessageResponse
    assistant_message: MessageResponse

