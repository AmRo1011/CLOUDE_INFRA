"""
Pydantic schemas for quizzes
"""
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
from datetime import datetime
from uuid import UUID
from decimal import Decimal


class QuizCreate(BaseModel):
    document_id: UUID
    title: str = Field(..., max_length=255)
    num_questions: int = Field(default=10, ge=1, le=50)
    question_types: List[str] = ["multiple_choice"]
    time_limit_minutes: int = Field(default=30, ge=5, le=180)


class OptionResponse(BaseModel):
    id: UUID
    text: str
    
    model_config = ConfigDict(from_attributes=True)


class QuestionResponse(BaseModel):
    id: UUID
    question_text: str
    question_type: str
    points: Decimal
    options: List[OptionResponse] = []
    
    model_config = ConfigDict(from_attributes=True)


class QuizResponse(BaseModel):
    id: UUID
    title: str
    description: Optional[str] = None
    time_limit_minutes: int
    num_questions: int = 0
    passing_score: Decimal
    status: str
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class QuizWithQuestions(QuizResponse):
    questions: List[QuestionResponse] = []


class AttemptCreate(BaseModel):
    pass


class AttemptResponse(BaseModel):
    id: UUID
    quiz_id: UUID
    started_at: datetime
    expires_at: Optional[datetime] = None
    time_remaining_seconds: Optional[int] = None
    
    model_config = ConfigDict(from_attributes=True)


class AnswerCreate(BaseModel):
    question_id: UUID
    selected_option_id: Optional[UUID] = None
    text_answer: Optional[str] = None


class AnswerResult(BaseModel):
    question_id: UUID
    question_text: str
    your_answer: Optional[str] = None
    correct_answer: str
    is_correct: bool
    points_earned: Decimal


class AttemptResultResponse(BaseModel):
    attempt_id: UUID
    status: str
    score: Decimal
    passing_score: Decimal
    passed: bool
    correct_answers: int
    total_questions: int
    completed_at: datetime
    results: List[AnswerResult] = []

