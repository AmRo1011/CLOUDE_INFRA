"""
Notes routes
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Annotated
from uuid import UUID
import logging

from app.database import get_db
from app.schemas.document import NoteCreate, NoteResponse
from app.services.document_service import DocumentService
from app.services.note_service import NoteService
from app.utils.auth import get_current_user

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/{document_id}/notes", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_note(
    document_id: UUID,
    note_data: NoteCreate,
    current_user: Annotated[dict, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)]
):
    """Create a note for a document"""
    doc_service = DocumentService(db)
    note_service = NoteService(db)
    
    # Verify document exists
    document = await doc_service.get_document(str(document_id), current_user["id"])
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "DOCUMENT_NOT_FOUND", "message": "Document not found"}
        )
    
    note = await note_service.create_note(
        document_id=str(document_id),
        user_id=current_user["id"],
        title=note_data.title,
        content=note_data.content
    )
    
    return {
        "status": "success",
        "data": NoteResponse.model_validate(note).model_dump()
    }


@router.get("/{document_id}/notes", response_model=dict)
async def list_notes(
    document_id: UUID,
    current_user: Annotated[dict, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)]
):
    """List notes for a document"""
    doc_service = DocumentService(db)
    note_service = NoteService(db)
    
    document = await doc_service.get_document(str(document_id), current_user["id"])
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "DOCUMENT_NOT_FOUND", "message": "Document not found"}
        )
    
    notes = await note_service.list_notes(str(document_id), current_user["id"])
    
    return {
        "status": "success",
        "data": {"notes": [NoteResponse.model_validate(n).model_dump() for n in notes]}
    }


@router.post("/{document_id}/generate-notes", response_model=dict)
async def generate_notes(
    document_id: UUID,
    current_user: Annotated[dict, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)]
):
    """Auto-generate notes using AI"""
    doc_service = DocumentService(db)
    note_service = NoteService(db)
    
    document = await doc_service.get_document(str(document_id), current_user["id"])
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "DOCUMENT_NOT_FOUND", "message": "Document not found"}
        )
    
    if not document.content or not document.content.content:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"code": "CONTENT_NOT_AVAILABLE", "message": "Document must be processed first"}
        )
    
    note = await note_service.generate_notes(
        document_id=str(document_id),
        user_id=current_user["id"],
        content=document.content.content
    )
    
    return {
        "status": "success",
        "data": NoteResponse.model_validate(note).model_dump(),
        "message": "Notes generated successfully"
    }

