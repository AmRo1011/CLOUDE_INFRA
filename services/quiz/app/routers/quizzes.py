"""
Quiz routes
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Annotated, Optional
from uuid import UUID
import logging

from app.database import get_db
from app.schemas.quiz import QuizCreate, QuizResponse, QuizWithQuestions
from app.services.quiz_service import QuizService
from app.utils.auth import get_current_user, require_permission

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/generate", response_model=dict, status_code=status.HTTP_202_ACCEPTED)
async def generate_quiz(
    quiz_data: QuizCreate,
    current_user: dict = Depends(require_permission("quiz.create")),
    db: AsyncSession = Depends(get_db)
):
    """Generate quiz from document"""
    service = QuizService(db)
    
    quiz = await service.generate_quiz(
        creator_id=current_user["id"],
        document_id=str(quiz_data.document_id),
        title=quiz_data.title,
        num_questions=quiz_data.num_questions,
        question_types=quiz_data.question_types,
        time_limit=quiz_data.time_limit_minutes
    )
    
    return {
        "status": "success",
        "data": {
            "quiz_id": str(quiz.id),
            "status": quiz.status,
            "estimated_time": 30
        },
        "message": "Quiz generation started"
    }


@router.get("/", response_model=dict)
async def list_quizzes(
    current_user: Annotated[dict, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=20, ge=1, le=100),
    status_filter: Optional[str] = Query(default=None, alias="status")
):
    """List available quizzes"""
    service = QuizService(db)
    quizzes, total = await service.list_quizzes(
        user_id=current_user["id"],
        role=current_user["role"],
        page=page,
        limit=limit,
        status=status_filter
    )
    
    quiz_responses = []
    for q in quizzes:
        resp = QuizResponse.model_validate(q).model_dump()
        resp["num_questions"] = len(q.questions)
        quiz_responses.append(resp)
    
    return {
        "status": "success",
        "data": {
            "quizzes": quiz_responses,
            "pagination": {"page": page, "limit": limit, "total": total}
        }
    }


@router.get("/{quiz_id}", response_model=dict)
async def get_quiz(
    quiz_id: UUID,
    current_user: Annotated[dict, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)]
):
    """Get quiz details"""
    service = QuizService(db)
    quiz = await service.get_quiz(str(quiz_id))
    
    if not quiz:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "QUIZ_NOT_FOUND", "message": "Quiz not found"}
        )
    
    # Hide correct answers for students
    is_creator = str(quiz.creator_id) == current_user["id"]
    is_admin = current_user["role"] == "admin"
    
    quiz_response = QuizWithQuestions.model_validate(quiz).model_dump()
    quiz_response["num_questions"] = len(quiz.questions)
    
    if not (is_creator or is_admin):
        for question in quiz_response["questions"]:
            for option in question["options"]:
                option.pop("is_correct", None)
    
    return {"status": "success", "data": quiz_response}


@router.put("/{quiz_id}", response_model=dict)
async def update_quiz(
    quiz_id: UUID,
    current_user: dict = Depends(require_permission("quiz.create")),
    db: AsyncSession = Depends(get_db)
):
    """Update quiz settings"""
    # Implementation for updating quiz
    return {"status": "success", "message": "Quiz updated"}


@router.delete("/{quiz_id}", response_model=dict)
async def delete_quiz(
    quiz_id: UUID,
    current_user: dict = Depends(require_permission("quiz.create")),
    db: AsyncSession = Depends(get_db)
):
    """Delete a quiz"""
    service = QuizService(db)
    success = await service.delete_quiz(str(quiz_id), current_user["id"])
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "QUIZ_NOT_FOUND", "message": "Quiz not found"}
        )
    
    return {"status": "success", "message": "Quiz deleted successfully"}

