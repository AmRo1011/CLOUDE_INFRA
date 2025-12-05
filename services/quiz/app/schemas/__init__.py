"""
Pydantic schemas for Quiz Service
"""
from app.schemas.quiz import (
    QuizCreate,
    QuizResponse,
    QuizWithQuestions,
    QuestionResponse,
    AttemptResponse,
    AnswerCreate,
    AttemptResultResponse
)

__all__ = [
    "QuizCreate",
    "QuizResponse",
    "QuizWithQuestions",
    "QuestionResponse",
    "AttemptResponse",
    "AnswerCreate",
    "AttemptResultResponse"
]

