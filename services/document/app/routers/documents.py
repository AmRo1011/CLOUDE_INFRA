"""
Document routes
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Annotated, Optional
from uuid import UUID
import logging

from app.database import get_db
from app.schemas.document import DocumentResponse, DocumentUploadResponse, DocumentContentResponse, DownloadUrlResponse
from app.services.document_service import DocumentService
from app.utils.auth import get_current_user, require_permission

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/upload", response_model=dict, status_code=status.HTTP_201_CREATED)
async def upload_document(
    file: Annotated[UploadFile, File(...)],
    title: Annotated[str, Form(...)],
    description: Annotated[Optional[str], Form()] = None,
    current_user: dict = Depends(require_permission("document.upload")),
    db: AsyncSession = Depends(get_db)
):
    """Upload a new document"""
    service = DocumentService(db)
    
    try:
        document = await service.upload_document(
            user_id=current_user["id"],
            file=file,
            title=title,
            description=description
        )
        
        return {
            "status": "success",
            "data": DocumentUploadResponse(
                id=document.id,
                title=document.title,
                file_name=document.file_name,
                file_type=document.file_type,
                file_size=document.file_size,
                status=document.status,
                created_at=document.created_at
            ).model_dump(),
            "message": "Document uploaded. Processing started."
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"code": "DOCUMENT_INVALID", "message": str(e)}
        )


@router.get("/", response_model=dict)
async def list_documents(
    current_user: Annotated[dict, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=20, ge=1, le=100),
    status_filter: Optional[str] = Query(default=None, alias="status")
):
    """List user's documents"""
    service = DocumentService(db)
    documents, total = await service.list_documents(
        user_id=current_user["id"],
        page=page,
        limit=limit,
        status=status_filter
    )
    
    return {
        "status": "success",
        "data": {
            "documents": [DocumentResponse.model_validate(d).model_dump() for d in documents],
            "pagination": {"page": page, "limit": limit, "total": total}
        }
    }


@router.get("/{document_id}", response_model=dict)
async def get_document(
    document_id: UUID,
    current_user: Annotated[dict, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)]
):
    """Get document details"""
    service = DocumentService(db)
    document = await service.get_document(str(document_id), current_user["id"])
    
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "DOCUMENT_NOT_FOUND", "message": "Document not found"}
        )
    
    response = DocumentResponse.model_validate(document).model_dump()
    if document.content:
        response["content_preview"] = document.content.content[:500] if document.content.content else None
    
    return {"status": "success", "data": response}


@router.get("/{document_id}/download", response_model=dict)
async def get_download_url(
    document_id: UUID,
    current_user: Annotated[dict, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)]
):
    """Get presigned URL for download"""
    service = DocumentService(db)
    document = await service.get_document(str(document_id), current_user["id"])
    
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "DOCUMENT_NOT_FOUND", "message": "Document not found"}
        )
    
    url = await service.get_download_url(document.s3_key)
    
    return {
        "status": "success",
        "data": {"download_url": url, "expires_in": 3600}
    }


@router.get("/{document_id}/content", response_model=dict)
async def get_document_content(
    document_id: UUID,
    current_user: Annotated[dict, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)]
):
    """Get extracted text content"""
    service = DocumentService(db)
    document = await service.get_document(str(document_id), current_user["id"])
    
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "DOCUMENT_NOT_FOUND", "message": "Document not found"}
        )
    
    if not document.content:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "CONTENT_NOT_AVAILABLE", "message": "Document content not yet extracted"}
        )
    
    return {
        "status": "success",
        "data": DocumentContentResponse(
            document_id=document.id,
            content=document.content.content,
            extracted_at=document.content.extracted_at
        ).model_dump()
    }


@router.delete("/{document_id}", response_model=dict)
async def delete_document(
    document_id: UUID,
    current_user: dict = Depends(require_permission("document.delete")),
    db: AsyncSession = Depends(get_db)
):
    """Delete a document"""
    service = DocumentService(db)
    success = await service.delete_document(str(document_id), current_user["id"])
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "DOCUMENT_NOT_FOUND", "message": "Document not found"}
        )
    
    return {"status": "success", "message": "Document deleted successfully"}

