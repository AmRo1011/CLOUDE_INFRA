"""
Note service
"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional, List
import logging
import httpx

from app.models.document import Note
from app.kafka_client import kafka_producer
from app.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class NoteService:
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create_note(
        self, 
        document_id: str, 
        user_id: str, 
        title: Optional[str], 
        content: str
    ) -> Note:
        """Create a note"""
        note = Note(
            document_id=document_id,
            user_id=user_id,
            title=title,
            content=content
        )
        self.db.add(note)
        await self.db.flush()
        await self.db.refresh(note)
        return note
    
    async def list_notes(self, document_id: str, user_id: str) -> List[Note]:
        """List notes for a document"""
        result = await self.db.execute(
            select(Note)
            .where(Note.document_id == document_id, Note.user_id == user_id)
            .order_by(Note.created_at.desc())
        )
        return list(result.scalars().all())
    
    async def generate_notes(self, document_id: str, user_id: str, content: str) -> Note:
        """Generate notes using AI"""
        generated_content = await self._call_ai(content)
        
        note = Note(
            document_id=document_id,
            user_id=user_id,
            title="AI Generated Notes",
            content=generated_content
        )
        self.db.add(note)
        await self.db.flush()
        await self.db.refresh(note)
        
        await kafka_producer.send_event(
            topic="notes.generated",
            payload={
                "note_id": str(note.id),
                "document_id": document_id,
                "user_id": user_id
            }
        )
        
        return note
    
    async def _call_ai(self, content: str) -> str:
        """Generate notes using OpenAI"""
        if not settings.OPENAI_API_KEY:
            return self._mock_notes(content)
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    "https://api.openai.com/v1/chat/completions",
                    headers={
                        "Authorization": f"Bearer {settings.OPENAI_API_KEY}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": "gpt-3.5-turbo",
                        "messages": [
                            {"role": "system", "content": "Generate concise study notes from the following document. Include a summary, key concepts, and important points."},
                            {"role": "user", "content": content[:8000]}
                        ],
                        "max_tokens": 1500
                    },
                    timeout=60.0
                )
                response.raise_for_status()
                return response.json()["choices"][0]["message"]["content"]
        except Exception as e:
            logger.error(f"AI note generation failed: {e}")
            return self._mock_notes(content)
    
    def _mock_notes(self, content: str) -> str:
        """Generate mock notes"""
        word_count = len(content.split())
        return f"""## Summary
This document contains approximately {word_count} words.

## Key Concepts
- Concept 1: Important topic from the document
- Concept 2: Another key area covered
- Concept 3: Additional information

## Important Points
1. First major point
2. Second major point
3. Third major point

## Study Tips
- Review these notes regularly
- Create flashcards for key terms
- Practice explaining concepts in your own words

*Note: These are auto-generated notes. The AI service is running in demo mode.*"""

