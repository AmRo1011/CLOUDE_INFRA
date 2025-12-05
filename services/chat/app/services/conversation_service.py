"""
Conversation service
"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload
from typing import Optional, List, Tuple
import logging

from app.models.conversation import Conversation, Message, ConversationContext

logger = logging.getLogger(__name__)


class ConversationService:
    """Service for conversation operations"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create_conversation(self, user_id: str, title: Optional[str] = None) -> Conversation:
        """Create a new conversation"""
        conversation = Conversation(
            user_id=user_id,
            title=title or "New Conversation"
        )
        self.db.add(conversation)
        await self.db.flush()
        await self.db.refresh(conversation)
        
        logger.info(f"Created conversation {conversation.id} for user {user_id}")
        return conversation
    
    async def get_conversation(self, conversation_id: str, user_id: str) -> Optional[Conversation]:
        """Get conversation with messages"""
        result = await self.db.execute(
            select(Conversation)
            .options(selectinload(Conversation.messages), selectinload(Conversation.contexts))
            .where(Conversation.id == conversation_id, Conversation.user_id == user_id)
        )
        return result.scalar_one_or_none()
    
    async def list_conversations(
        self, 
        user_id: str, 
        page: int = 1, 
        limit: int = 20
    ) -> Tuple[List[Conversation], int]:
        """List user's conversations"""
        # Get total count
        count_result = await self.db.execute(
            select(func.count(Conversation.id)).where(Conversation.user_id == user_id)
        )
        total = count_result.scalar() or 0
        
        # Get conversations
        offset = (page - 1) * limit
        result = await self.db.execute(
            select(Conversation)
            .options(selectinload(Conversation.messages))
            .where(Conversation.user_id == user_id)
            .order_by(Conversation.updated_at.desc())
            .offset(offset)
            .limit(limit)
        )
        conversations = result.scalars().all()
        
        return list(conversations), total
    
    async def delete_conversation(self, conversation_id: str, user_id: str) -> bool:
        """Delete a conversation"""
        conversation = await self.get_conversation(conversation_id, user_id)
        if not conversation:
            return False
        
        await self.db.delete(conversation)
        await self.db.flush()
        
        logger.info(f"Deleted conversation {conversation_id}")
        return True
    
    async def add_message(self, conversation_id: str, role: str, content: str) -> Message:
        """Add message to conversation"""
        message = Message(
            conversation_id=conversation_id,
            role=role,
            content=content
        )
        self.db.add(message)
        await self.db.flush()
        await self.db.refresh(message)
        
        return message
    
    async def add_context(self, conversation_id: str, document_id: str) -> ConversationContext:
        """Add document context to conversation"""
        context = ConversationContext(
            conversation_id=conversation_id,
            document_id=document_id,
            context_type="document"
        )
        self.db.add(context)
        await self.db.flush()
        await self.db.refresh(context)
        
        logger.info(f"Added document context {document_id} to conversation {conversation_id}")
        return context

