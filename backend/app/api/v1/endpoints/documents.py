"""
User Document Management API Endpoints
Handles document upload, listing, updating, and deletion
"""

from fastapi import APIRouter, HTTPException, status, Depends, UploadFile, File, Query
from fastapi.responses import Response
from app.core.firebase import db, bucket
from app.models.schemas import (
    UserDocumentUpdate, UserDocumentResponse, 
    DocumentType, DocumentStatus
)
from app.services.security import get_current_user, UserInDB
from datetime import datetime
from typing import List, Optional
import uuid
import os
import logging

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/", response_model=UserDocumentResponse, status_code=status.HTTP_201_CREATED)
async def upload_document(
    file: UploadFile = File(...),
    document_type: DocumentType = Query(...),
    document_title: str = Query(...),
    notes: Optional[str] = Query(None),
    tags: Optional[str] = Query(None),
    current_user: UserInDB = Depends(get_current_user)
):
    """
    Upload a new document for a user.
    Metadata is passed as query parameters.
    """
    try:
        if not file.filename:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No file provided")
        
        file_content = await file.read()
        if len(file_content) > 10 * 1024 * 1024:  # 10MB
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="File size exceeds 10MB limit")
        
        doc_id = str(uuid.uuid4())
        file_extension = os.path.splitext(file.filename)[1]
        storage_path = f"users/{current_user.uid}/documents/{doc_id}{file_extension}"
        
        blob = bucket.blob(storage_path)
        blob.upload_from_string(file_content, content_type=file.content_type)
        
        tag_list = [tag.strip() for tag in tags.split(",")] if tags else []
        
        now = datetime.utcnow()
        doc_data = {
            "doc_id": doc_id,
            "user_id": current_user.uid,
            "storage_path": storage_path,
            "document_title": document_title,
            "doc_type": document_type.value,
            "status": DocumentStatus.PENDING_VALIDATION.value,
            "file_name": file.filename,
            "file_size": len(file_content),
            "mime_type": file.content_type or "application/octet-stream",
            "notes": notes,
            "tags": tag_list,
            "created_at": now,
            "updated_at": now,
        }
        
        db.collection("documents").document(doc_id).set(doc_data)
        
        return UserDocumentResponse(**doc_data)
        
    except Exception as e:
        logger.error(f"Error uploading document: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to upload document")


@router.get("/", response_model=List[UserDocumentResponse])
async def get_user_documents(
    current_user: UserInDB = Depends(get_current_user),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0)
):
    """Get all documents for the current user."""
    try:
        docs_query = db.collection("documents").where("user_id", "==", current_user.uid)
        docs_stream = docs_query.order_by("created_at", direction="DESCENDING").offset(offset).limit(limit).stream()
        
        return [UserDocumentResponse(**doc.to_dict()) for doc in docs_stream]
        
    except Exception as e:
        logger.error(f"Error getting user documents: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to get documents")


@router.get("/{doc_id}", response_model=UserDocumentResponse)
async def get_document(doc_id: str, current_user: UserInDB = Depends(get_current_user)):
    """Get a specific document by ID."""
    try:
        doc_ref = db.collection("documents").document(doc_id)
        doc = doc_ref.get()
        
        if not doc.exists:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")
        
        doc_data = doc.to_dict()
        if doc_data.get("user_id") != current_user.uid:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
        
        return UserDocumentResponse(**doc_data)
        
    except Exception as e:
        logger.error(f"Error getting document: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to get document")


@router.put("/{doc_id}", response_model=UserDocumentResponse)
async def update_document(
    doc_id: str,
    doc_update: UserDocumentUpdate,
    current_user: UserInDB = Depends(get_current_user)
):
    """Update a document's metadata."""
    try:
        doc_ref = db.collection("documents").document(doc_id)
        doc = doc_ref.get()

        if not doc.exists:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")

        doc_data = doc.to_dict()
        if doc_data.get("user_id") != current_user.uid:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

        update_data = doc_update.dict(exclude_unset=True)
        update_data["updated_at"] = datetime.utcnow()
        
        doc_ref.update(update_data)
        updated_doc = doc_ref.get().to_dict()

        return UserDocumentResponse(**updated_doc)

    except Exception as e:
        logger.error(f"Error updating document: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to update document")


@router.delete("/{doc_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_document(doc_id: str, current_user: UserInDB = Depends(get_current_user)):
    """Delete a document."""
    try:
        doc_ref = db.collection("documents").document(doc_id)
        doc = doc_ref.get()
        
        if not doc.exists:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")
        
        doc_data = doc.to_dict()
        if doc_data.get("user_id") != current_user.uid:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
        
        storage_path = doc_data.get("storage_path")
        if storage_path:
            blob = bucket.blob(storage_path)
            if blob.exists():
                blob.delete()
        
        doc_ref.delete()
        
        return Response(status_code=status.HTTP_204_NO_CONTENT)
        
    except Exception as e:
        logger.error(f"Error deleting document: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to delete document")
