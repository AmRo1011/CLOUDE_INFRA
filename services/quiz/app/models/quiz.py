"""
Quiz database models
"""
from sqlalchemy import Column, String, Text, DateTime, Integer, Boolean, Numeric, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

from app.database import Base


class Quiz(Base):
    __tablename__ = "quizzes"
    __table_args__ = {"schema": "quiz"}
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    document_id = Column(UUID(as_uuid=True), index=True)
    creator_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text)
    time_limit_minutes = Column(Integer, default=30)
    passing_score = Column(Numeric(5, 2), default=70.00)
    status = Column(String(50), default="draft", index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    questions = relationship("Question", back_populates="quiz", cascade="all, delete-orphan")
    attempts = relationship("QuizAttempt", back_populates="quiz", cascade="all, delete-orphan")


class Question(Base):
    __tablename__ = "questions"
    __table_args__ = {"schema": "quiz"}
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    quiz_id = Column(UUID(as_uuid=True), ForeignKey("quiz.quizzes.id", ondelete="CASCADE"), nullable=False)
    question_text = Column(Text, nullable=False)
    question_type = Column(String(50), default="multiple_choice")
    points = Column(Numeric(5, 2), default=1.00)
    order_index = Column(Integer)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    quiz = relationship("Quiz", back_populates="questions")
    options = relationship("QuestionOption", back_populates="question", cascade="all, delete-orphan")


class QuestionOption(Base):
    __tablename__ = "question_options"
    __table_args__ = {"schema": "quiz"}
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    question_id = Column(UUID(as_uuid=True), ForeignKey("quiz.questions.id", ondelete="CASCADE"), nullable=False)
    option_text = Column(Text, nullable=False)
    is_correct = Column(Boolean, default=False)
    order_index = Column(Integer)
    
    question = relationship("Question", back_populates="options")


class QuizAttempt(Base):
    __tablename__ = "quiz_attempts"
    __table_args__ = {"schema": "quiz"}
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    quiz_id = Column(UUID(as_uuid=True), ForeignKey("quiz.quizzes.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    started_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True))
    score = Column(Numeric(5, 2))
    status = Column(String(50), default="in_progress")
    
    quiz = relationship("Quiz", back_populates="attempts")
    answers = relationship("AttemptAnswer", back_populates="attempt", cascade="all, delete-orphan")


class AttemptAnswer(Base):
    __tablename__ = "attempt_answers"
    __table_args__ = {"schema": "quiz"}
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    attempt_id = Column(UUID(as_uuid=True), ForeignKey("quiz.quiz_attempts.id", ondelete="CASCADE"), nullable=False)
    question_id = Column(UUID(as_uuid=True), ForeignKey("quiz.questions.id", ondelete="CASCADE"), nullable=False)
    selected_option_id = Column(UUID(as_uuid=True), ForeignKey("quiz.question_options.id"))
    text_answer = Column(Text)
    is_correct = Column(Boolean)
    points_earned = Column(Numeric(5, 2), default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    attempt = relationship("QuizAttempt", back_populates="answers")

