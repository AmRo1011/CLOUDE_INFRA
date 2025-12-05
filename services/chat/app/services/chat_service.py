"""
Chat AI service
"""
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
import logging
import httpx

from app.config import get_settings
from app.models.conversation import Conversation
from app.kafka_client import kafka_producer

logger = logging.getLogger(__name__)
settings = get_settings()


class ChatService:
    """Service for AI chat operations"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_ai_response(self, conversation: Conversation, user_message: str) -> str:
        """Get AI response for user message"""
        try:
            # Build conversation history
            messages = self._build_messages(conversation, user_message)
            
            # Call OpenAI API
            response = await self._call_openai(messages)
            
            # Publish event
            await self._publish_message_event(conversation, user_message)
            
            return response
            
        except Exception as e:
            logger.error(f"Error getting AI response: {e}")
            return "I apologize, but I'm having trouble processing your request right now. Please try again later."
    
    def _build_messages(self, conversation: Conversation, user_message: str) -> list:
        """Build message list for OpenAI API"""
        messages = [
            {
                "role": "system",
                "content": """You are a helpful AI tutor for a cloud-based learning platform. 
                You help students understand their study materials, answer questions, and explain concepts clearly.
                Be encouraging, patient, and provide detailed explanations when needed."""
            }
        ]
        
        # Add context if available
        if conversation.contexts:
            context_info = "The student has the following documents for reference:\n"
            for ctx in conversation.contexts:
                if ctx.context_data:
                    context_info += f"- {ctx.context_data.get('title', 'Document')}\n"
            messages.append({
                "role": "system",
                "content": context_info
            })
        
        # Add conversation history (last 10 messages)
        for msg in conversation.messages[-10:]:
            messages.append({
                "role": msg.role,
                "content": msg.content
            })
        
        # Add current user message
        messages.append({
            "role": "user",
            "content": user_message
        })
        
        return messages
    
    async def _call_openai(self, messages: list) -> str:
        """Call OpenAI API"""
        if not settings.OPENAI_API_KEY:
            logger.warning("OpenAI API key not configured, using mock response")
            return self._mock_response(messages[-1]["content"])
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    "https://api.openai.com/v1/chat/completions",
                    headers={
                        "Authorization": f"Bearer {settings.OPENAI_API_KEY}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": settings.OPENAI_MODEL,
                        "messages": messages,
                        "max_tokens": 1000,
                        "temperature": 0.7
                    },
                    timeout=60.0
                )
                response.raise_for_status()
                data = response.json()
                return data["choices"][0]["message"]["content"]
        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            return self._mock_response(messages[-1]["content"])
    
    def _mock_response(self, user_message: str) -> str:
        """Generate mock response for testing without OpenAI"""
        return f"""I understand you're asking about "{user_message[:50]}..."

As your AI tutor, I'm here to help you learn. However, the AI service is currently running in demo mode.

Here are some general tips:
1. Break down complex topics into smaller parts
2. Try to relate new concepts to things you already know
3. Practice with examples and exercises
4. Don't hesitate to ask follow-up questions

Is there a specific aspect of this topic you'd like me to explain further?"""
    
    async def _publish_message_event(self, conversation: Conversation, message: str):
        """Publish chat message event to Kafka"""
        await kafka_producer.send_event(
            topic="chat.message",
            payload={
                "conversation_id": str(conversation.id),
                "user_id": str(conversation.user_id),
                "content_length": len(message),
                "has_context": len(conversation.contexts) > 0
            }
        )

