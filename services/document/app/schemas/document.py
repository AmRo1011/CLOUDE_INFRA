"""
Pydantic schemas for documents
"""
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
from datetime import datetime
from uuid import UUID


class DocumentResponse(BaseModel):
    id: UUID
    title: str
    description: Optional[str] = None
    file_name: str
    file_type: Optional[str] = None
    file_size: Optional[int] = None
    status: str
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class DocumentUploadResponse(BaseModel):
    id: UUID
    title: str
    file_name: str
    file_type: Optional[str] = None
    file_size: Optional[int] = None
    status: str
    created_at: datetime


class DocumentContentResponse(BaseModel):
    document_id: UUID
    content: str
    extracted_at: datetime


class DownloadUrlResponse(BaseModel):
    download_url: str
    expires_in: int


class NoteCreate(BaseModel):
    title: Optional[str] = Field(None, max_length=255)
    content: str = Field(..., min_length=1)


class NoteResponse(BaseModel):
    id: UUID
    document_id: UUID
    title: Optional[str] = None
    content: str
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class PaginatedDocuments(BaseModel):
    documents: List[DocumentResponse]
    pagination: dict

