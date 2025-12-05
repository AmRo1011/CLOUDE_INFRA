"""
Quiz attempt routes
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Annotated
from uuid import UUID
import logging

from app.database import get_db
from app.schemas.quiz import AttemptResponse, AnswerCreate, AttemptResultResponse
from app.services.quiz_service import QuizService
from app.services.attempt_service import AttemptService
from app.utils.auth import get_current_user, require_permission

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/{quiz_id}/start", response_model=dict, status_code=status.HTTP_201_CREATED)
async def start_quiz(
    quiz_id: UUID,
    current_user: dict = Depends(require_permission("quiz.take")),
    db: AsyncSession = Depends(get_db)
):
    """Start a quiz attempt"""
    quiz_service = QuizService(db)
    attempt_service = AttemptService(db)
    
    quiz = await quiz_service.get_quiz(str(quiz_id))
    if not quiz:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "QUIZ_NOT_FOUND", "message": "Quiz not found"}
        )
    
    if quiz.status != "published":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"code": "QUIZ_NOT_PUBLISHED", "message": "Quiz is not available"}
        )
    
    attempt = await attempt_service.start_attempt(str(quiz_id), current_user["id"], quiz.time_limit_minutes)
    
    from datetime import timedelta
    expires_at = attempt.started_at + timedelta(minutes=quiz.time_limit_minutes)
    remaining = int((expires_at - attempt.started_at).total_seconds())
    
    return {
        "status": "success",
        "data": {
            "attempt_id": str(attempt.id),
            "quiz_id": str(quiz_id),
            "started_at": attempt.started_at.isoformat(),
            "expires_at": expires_at.isoformat(),
            "time_remaining_seconds": remaining
        }
    }


@router.post("/{quiz_id}/attempts/{attempt_id}/answer", response_model=dict)
async def submit_answer(
    quiz_id: UUID,
    attempt_id: UUID,
    answer_data: AnswerCreate,
    current_user: Annotated[dict, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)]
):
    """Submit answer for a question"""
    attempt_service = AttemptService(db)
    
    attempt = await attempt_service.get_attempt(str(attempt_id), current_user["id"])
    if not attempt:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "ATTEMPT_NOT_FOUND", "message": "Attempt not found"}
        )
    
    if attempt.status != "in_progress":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"code": "QUIZ_ALREADY_SUBMITTED", "message": "Quiz already submitted"}
        )
    
    await attempt_service.save_answer(
        attempt_id=str(attempt_id),
        question_id=str(answer_data.question_id),
        selected_option_id=str(answer_data.selected_option_id) if answer_data.selected_option_id else None,
        text_answer=answer_data.text_answer
    )
    
    return {
        "status": "success",
        "data": {"question_id": str(answer_data.question_id), "answered": True}
    }


@router.post("/{quiz_id}/attempts/{attempt_id}/submit", response_model=dict)
async def submit_quiz(
    quiz_id: UUID,
    attempt_id: UUID,
    current_user: Annotated[dict, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)]
):
    """Submit quiz for grading"""
    attempt_service = AttemptService(db)
    quiz_service = QuizService(db)
    
    attempt = await attempt_service.get_attempt(str(attempt_id), current_user["id"])
    if not attempt:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "ATTEMPT_NOT_FOUND", "message": "Attempt not found"}
        )
    
    if attempt.status != "in_progress":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"code": "QUIZ_ALREADY_SUBMITTED", "message": "Quiz already submitted"}
        )
    
    quiz = await quiz_service.get_quiz(str(quiz_id))
    result = await attempt_service.grade_attempt(attempt, quiz)
    
    return {"status": "success", "data": result}


@router.get("/{quiz_id}/attempts", response_model=dict)
async def list_attempts(
    quiz_id: UUID,
    current_user: Annotated[dict, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)]
):
    """List user's attempts for a quiz"""
    attempt_service = AttemptService(db)
    attempts = await attempt_service.list_attempts(str(quiz_id), current_user["id"])
    
    return {
        "status": "success",
        "data": {
            "attempts": [
                {
                    "id": str(a.id),
                    "started_at": a.started_at.isoformat(),
                    "completed_at": a.completed_at.isoformat() if a.completed_at else None,
                    "score": float(a.score) if a.score else None,
                    "status": a.status
                }
                for a in attempts
            ]
        }
    }

