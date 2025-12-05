"""
Pydantic schemas for Document Service
"""
from app.schemas.document import (
    DocumentResponse,
    DocumentUploadResponse,
    DocumentContentResponse,
    NoteCreate,
    NoteResponse
)

__all__ = [
    "DocumentResponse",
    "DocumentUploadResponse",
    "DocumentContentResponse",
    "NoteCreate",
    "NoteResponse"
]

