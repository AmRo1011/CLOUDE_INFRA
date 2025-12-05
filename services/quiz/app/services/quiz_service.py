"""
Quiz service
"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_
from sqlalchemy.orm import selectinload
from typing import Optional, List, Tuple
import logging
import httpx
import json

from app.models.quiz import Quiz, Question, QuestionOption
from app.kafka_client import kafka_producer
from app.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class QuizService:
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def generate_quiz(
        self,
        creator_id: str,
        document_id: str,
        title: str,
        num_questions: int,
        question_types: List[str],
        time_limit: int
    ) -> Quiz:
        """Generate a quiz from document content"""
        quiz = Quiz(
            document_id=document_id,
            creator_id=creator_id,
            title=title,
            time_limit_minutes=time_limit,
            status="generating"
        )
        self.db.add(quiz)
        await self.db.flush()
        
        # Generate questions
        questions = await self._generate_questions(num_questions, question_types)
        
        for i, q_data in enumerate(questions):
            question = Question(
                quiz_id=quiz.id,
                question_text=q_data["question"],
                question_type=q_data["type"],
                points=1.0,
                order_index=i
            )
            self.db.add(question)
            await self.db.flush()
            
            for j, opt in enumerate(q_data["options"]):
                option = QuestionOption(
                    question_id=question.id,
                    option_text=opt["text"],
                    is_correct=opt["is_correct"],
                    order_index=j
                )
                self.db.add(option)
        
        quiz.status = "draft"
        await self.db.flush()
        await self.db.refresh(quiz)
        
        await kafka_producer.send_event(
            topic="quiz.generated",
            payload={
                "quiz_id": str(quiz.id),
                "document_id": document_id,
                "creator_id": creator_id,
                "num_questions": num_questions
            }
        )
        
        return quiz
    
    async def _generate_questions(self, num_questions: int, question_types: List[str]) -> List[dict]:
        """Generate questions using AI or mock"""
        if not settings.OPENAI_API_KEY:
            return self._mock_questions(num_questions, question_types)
        
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
                            {"role": "system", "content": f"""Generate {num_questions} quiz questions in JSON format.
Each question should have: question, type (multiple_choice or true_false), and options array.
Each option has: text, is_correct (boolean).
Multiple choice should have 4 options with 1 correct. True/false should have 2 options."""},
                            {"role": "user", "content": "Generate educational quiz questions about general knowledge."}
                        ],
                        "max_tokens": 2000
                    },
                    timeout=60.0
                )
                response.raise_for_status()
                content = response.json()["choices"][0]["message"]["content"]
                return json.loads(content)
        except Exception as e:
            logger.error(f"AI question generation failed: {e}")
            return self._mock_questions(num_questions, question_types)
    
    def _mock_questions(self, num_questions: int, question_types: List[str]) -> List[dict]:
        """Generate mock questions"""
        questions = []
        for i in range(num_questions):
            q_type = question_types[i % len(question_types)]
            if q_type == "true_false":
                questions.append({
                    "question": f"Sample True/False Question {i+1}?",
                    "type": "true_false",
                    "options": [
                        {"text": "True", "is_correct": True},
                        {"text": "False", "is_correct": False}
                    ]
                })
            else:
                questions.append({
                    "question": f"Sample Multiple Choice Question {i+1}?",
                    "type": "multiple_choice",
                    "options": [
                        {"text": "Option A (Correct)", "is_correct": True},
                        {"text": "Option B", "is_correct": False},
                        {"text": "Option C", "is_correct": False},
                        {"text": "Option D", "is_correct": False}
                    ]
                })
        return questions
    
    async def get_quiz(self, quiz_id: str) -> Optional[Quiz]:
        """Get quiz by ID"""
        result = await self.db.execute(
            select(Quiz)
            .options(
                selectinload(Quiz.questions).selectinload(Question.options)
            )
            .where(Quiz.id == quiz_id)
        )
        return result.scalar_one_or_none()
    
    async def list_quizzes(
        self,
        user_id: str,
        role: str,
        page: int = 1,
        limit: int = 20,
        status: Optional[str] = None
    ) -> Tuple[List[Quiz], int]:
        """List quizzes"""
        query = select(Quiz).options(selectinload(Quiz.questions))
        count_query = select(func.count(Quiz.id))
        
        # Students see only published, instructors/admins see their own + published
        if role == "student":
            query = query.where(Quiz.status == "published")
            count_query = count_query.where(Quiz.status == "published")
        else:
            query = query.where(or_(Quiz.creator_id == user_id, Quiz.status == "published"))
            count_query = count_query.where(or_(Quiz.creator_id == user_id, Quiz.status == "published"))
        
        if status:
            query = query.where(Quiz.status == status)
            count_query = count_query.where(Quiz.status == status)
        
        total_result = await self.db.execute(count_query)
        total = total_result.scalar() or 0
        
        offset = (page - 1) * limit
        query = query.offset(offset).limit(limit).order_by(Quiz.created_at.desc())
        
        result = await self.db.execute(query)
        return list(result.scalars().all()), total
    
    async def delete_quiz(self, quiz_id: str, user_id: str) -> bool:
        """Delete quiz"""
        result = await self.db.execute(
            select(Quiz).where(Quiz.id == quiz_id, Quiz.creator_id == user_id)
        )
        quiz = result.scalar_one_or_none()
        if not quiz:
            return False
        
        await self.db.delete(quiz)
        await self.db.flush()
        return True

