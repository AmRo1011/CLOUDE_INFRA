"""
Quiz attempt service
"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from typing import Optional, List
from datetime import datetime, timezone
from decimal import Decimal
import logging

from app.models.quiz import Quiz, Question, QuestionOption, QuizAttempt, AttemptAnswer
from app.kafka_client import kafka_producer

logger = logging.getLogger(__name__)


class AttemptService:
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def start_attempt(self, quiz_id: str, user_id: str, time_limit: int) -> QuizAttempt:
        """Start a new quiz attempt"""
        attempt = QuizAttempt(
            quiz_id=quiz_id,
            user_id=user_id,
            status="in_progress"
        )
        self.db.add(attempt)
        await self.db.flush()
        await self.db.refresh(attempt)
        return attempt
    
    async def get_attempt(self, attempt_id: str, user_id: str) -> Optional[QuizAttempt]:
        """Get attempt by ID"""
        result = await self.db.execute(
            select(QuizAttempt)
            .options(selectinload(QuizAttempt.answers))
            .where(QuizAttempt.id == attempt_id, QuizAttempt.user_id == user_id)
        )
        return result.scalar_one_or_none()
    
    async def save_answer(
        self,
        attempt_id: str,
        question_id: str,
        selected_option_id: Optional[str],
        text_answer: Optional[str]
    ):
        """Save or update answer"""
        # Check if answer exists
        result = await self.db.execute(
            select(AttemptAnswer).where(
                AttemptAnswer.attempt_id == attempt_id,
                AttemptAnswer.question_id == question_id
            )
        )
        existing = result.scalar_one_or_none()
        
        if existing:
            existing.selected_option_id = selected_option_id
            existing.text_answer = text_answer
        else:
            answer = AttemptAnswer(
                attempt_id=attempt_id,
                question_id=question_id,
                selected_option_id=selected_option_id,
                text_answer=text_answer
            )
            self.db.add(answer)
        
        await self.db.flush()
    
    async def grade_attempt(self, attempt: QuizAttempt, quiz: Quiz) -> dict:
        """Grade quiz attempt"""
        total_points = Decimal(0)
        earned_points = Decimal(0)
        correct_count = 0
        results = []
        
        for question in quiz.questions:
            total_points += question.points
            
            # Find answer for this question
            answer = next(
                (a for a in attempt.answers if str(a.question_id) == str(question.id)),
                None
            )
            
            # Find correct option
            correct_option = next(
                (o for o in question.options if o.is_correct),
                None
            )
            
            is_correct = False
            user_answer = None
            
            if answer and answer.selected_option_id:
                selected = next(
                    (o for o in question.options if str(o.id) == str(answer.selected_option_id)),
                    None
                )
                if selected:
                    user_answer = selected.option_text
                    is_correct = selected.is_correct
            
            if is_correct:
                earned_points += question.points
                correct_count += 1
                if answer:
                    answer.is_correct = True
                    answer.points_earned = question.points
            elif answer:
                answer.is_correct = False
                answer.points_earned = Decimal(0)
            
            results.append({
                "question_id": str(question.id),
                "question_text": question.question_text,
                "your_answer": user_answer,
                "correct_answer": correct_option.option_text if correct_option else "N/A",
                "is_correct": is_correct,
                "points_earned": float(question.points if is_correct else 0)
            })
        
        # Calculate score
        score = (earned_points / total_points * 100) if total_points > 0 else Decimal(0)
        passed = score >= quiz.passing_score
        
        # Update attempt
        attempt.score = score
        attempt.status = "graded"
        attempt.completed_at = datetime.now(timezone.utc)
        
        await self.db.flush()
        
        # Publish event
        await kafka_producer.send_event(
            topic="quiz.graded",
            payload={
                "attempt_id": str(attempt.id),
                "quiz_id": str(quiz.id),
                "user_id": str(attempt.user_id),
                "score": float(score),
                "passed": passed
            }
        )
        
        return {
            "attempt_id": str(attempt.id),
            "status": "graded",
            "score": float(score),
            "passing_score": float(quiz.passing_score),
            "passed": passed,
            "correct_answers": correct_count,
            "total_questions": len(quiz.questions),
            "completed_at": attempt.completed_at.isoformat(),
            "results": results
        }
    
    async def list_attempts(self, quiz_id: str, user_id: str) -> List[QuizAttempt]:
        """List user's attempts"""
        result = await self.db.execute(
            select(QuizAttempt)
            .where(QuizAttempt.quiz_id == quiz_id, QuizAttempt.user_id == user_id)
            .order_by(QuizAttempt.started_at.desc())
        )
        return list(result.scalars().all())

