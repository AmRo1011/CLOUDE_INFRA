"""
Document database models
"""
from sqlalchemy import Column, String, Text, DateTime, BigInteger, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

from app.database import Base


class Document(Base):
    __tablename__ = "documents"
    __table_args__ = {"schema": "document"}
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text)
    file_name = Column(String(255), nullable=False)
    file_type = Column(String(50))
    file_size = Column(BigInteger)
    s3_key = Column(String(512), nullable=False)
    status = Column(String(50), default="uploaded", index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    content = relationship("DocumentContent", back_populates="document", uselist=False, cascade="all, delete-orphan")
    notes = relationship("Note", back_populates="document", cascade="all, delete-orphan")


class DocumentContent(Base):
    __tablename__ = "document_content"
    __table_args__ = {"schema": "document"}
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    document_id = Column(UUID(as_uuid=True), ForeignKey("document.documents.id", ondelete="CASCADE"), nullable=False)
    content = Column(Text)
    extracted_at = Column(DateTime(timezone=True), server_default=func.now())
    
    document = relationship("Document", back_populates="content")


class Note(Base):
    __tablename__ = "notes"
    __table_args__ = {"schema": "document"}
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    document_id = Column(UUID(as_uuid=True), ForeignKey("document.documents.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    title = Column(String(255))
    content = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    document = relationship("Document", back_populates="notes")

