"""
User Document Management API Endpoints
Handles document upload, listing, updating, and deletion
"""

from fastapi import APIRouter, HTTPException, status, Depends, UploadFile, File, Query
from app.core.firebase import db
from app.models.schemas import (
    UserDocumentUpload, UserDocumentUpdate, UserDocumentResponse, 
    UserDocumentInDB, DocumentType, DocumentStatus
)
from app.services.security import get_current_user, UserInDB
from datetime import datetime
from typing import List, Optional
import uuid
import logging
import os
from firebase_admin import storage

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/documents/upload", response_model=UserDocumentResponse, status_code=status.HTTP_201_CREATED)
async def upload_document(
    document_type: DocumentType,
    document_title: str,
    file: UploadFile = File(...),
    notes: Optional[str] = None,
    tags: Optional[str] = None,
    current_user: UserInDB = Depends(get_current_user)
):
    """
    Upload a new document
    """
    try:
        # Validate file
        if not file.filename:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No file provided"
            )
        
        # Check file size (max 10MB)
        file_content = await file.read()
        if len(file_content) > 10 * 1024 * 1024:  # 10MB
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="File size exceeds 10MB limit"
            )
        
        # Generate unique document ID
        doc_id = str(uuid.uuid4())
        
        # Upload to Firebase Storage
        bucket = storage.bucket()
        file_extension = os.path.splitext(file.filename)[1]
        storage_path = f"users/{current_user.uid}/documents/{doc_id}{file_extension}"
        
        blob = bucket.blob(storage_path)
        blob.upload_from_string(file_content, content_type=file.content_type)
        
        # Make blob publicly accessible (optional, depending on your security requirements)
        blob.make_public()
        
        # Parse tags if provided
        tag_list = []
        if tags:
            tag_list = [tag.strip() for tag in tags.split(",") if tag.strip()]
        
        # Create document record
        now = datetime.utcnow()
        doc_data = {
            "doc_id": doc_id,
            "user_id": current_user.uid,
            "storage_path": storage_path,
            "doc_type": document_type.value,
            "status": DocumentStatus.PENDING_VALIDATION.value,
            "ocr_result": None,
            "document_title": document_title,
            "file_name": file.filename,
            "file_size": len(file_content),
            "mime_type": file.content_type or "application/octet-stream",
            "uploaded_at": now,
            "updated_at": now,
            "expiry_date": None,
            "issued_date": None,
            "issuing_authority": None,
            "notes": notes,
            "tags": tag_list
        }
        
        # Save to Firestore
        db.collection("user_documents").document(doc_id).set(doc_data)
        
        return UserDocumentResponse(**doc_data)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error uploading document: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to upload document"
        )


@router.get("/documents", response_model=List[UserDocumentResponse])
async def get_user_documents(
    current_user: UserInDB = Depends(get_current_user),
    document_type: Optional[DocumentType] = Query(None, description="Filter by document type"),
    status_filter: Optional[DocumentStatus] = Query(None, description="Filter by document status"),
    limit: int = Query(50, ge=1, le=100, description="Number of results to return"),
    offset: int = Query(0, ge=0, description="Number of results to skip")
):
    """
    Get user's documents with optional filtering
    """
    try:
        # Build query
        query = db.collection("user_documents").where("user_id", "==", current_user.uid)
        
        if document_type:
            query = query.where("doc_type", "==", document_type.value)
        
        if status_filter:
            query = query.where("status", "==", status_filter.value)
        
        # Order by upload date (newest first)
        query = query.order_by("uploaded_at", direction="DESCENDING")
        
        # Apply pagination
        query = query.offset(offset).limit(limit)
        
        # Execute query
        docs = query.stream()
        
        documents = []
        for doc in docs:
            doc_data = doc.to_dict()
            documents.append(UserDocumentResponse(**doc_data))
        
        return documents
        
    except Exception as e:
        logger.error(f"Error getting user documents: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get documents"
        )


@router.get("/documents/{doc_id}", response_model=UserDocumentResponse)
async def get_document(
    doc_id: str,
    current_user: UserInDB = Depends(get_current_user)
):
    """
    Get a specific document by ID
    """
    try:
        # Get document
        doc_ref = db.collection("user_documents").document(doc_id)
        doc = doc_ref.get()
        
        if not doc.exists:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Document not found"
            )
        
        doc_data = doc.to_dict()
        
        # Check if user owns this document
        if doc_data.get("user_id") != current_user.uid:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to access this document"
            )
        
        return UserDocumentResponse(**doc_data)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting document: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get document"
        )


@router.put("/documents/{doc_id}", response_model=UserDocumentResponse)
async def update_document(
    doc_id: str,
    document_update: UserDocumentUpdate,
    current_user: UserInDB = Depends(get_current_user)
):
    """
    Update document metadata
    """
    try:
        # Check if document exists
        doc_ref = db.collection("user_documents").document(doc_id)
        doc = doc_ref.get()
        
        if not doc.exists:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Document not found"
            )
        
        doc_data = doc.to_dict()
        
        # Check if user owns this document
        if doc_data.get("user_id") != current_user.uid:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to update this document"
            )
        
        # Prepare update data
        update_data = {"updated_at": datetime.utcnow()}
        
        if document_update.document_title is not None:
            update_data["document_title"] = document_update.document_title
        
        if document_update.notes is not None:
            update_data["notes"] = document_update.notes
        
        if document_update.tags is not None:
            update_data["tags"] = document_update.tags
        
        # Update document
        doc_ref.update(update_data)
        
        # Get updated document data
        updated_doc = doc_ref.get()
        updated_doc_data = updated_doc.to_dict()
        
        return UserDocumentResponse(**updated_doc_data)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating document: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update document"
        )


@router.delete("/documents/{doc_id}", response_model=dict)
async def delete_document(
    doc_id: str,
    current_user: UserInDB = Depends(get_current_user)
):
    """
    Delete a document
    """
    try:
        # Check if document exists
        doc_ref = db.collection("user_documents").document(doc_id)
        doc = doc_ref.get()
        
        if not doc.exists:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Document not found"
            )
        
        doc_data = doc.to_dict()
        
        # Check if user owns this document
        if doc_data.get("user_id") != current_user.uid:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to delete this document"
            )
        
        # Delete from Firebase Storage
        try:
            bucket = storage.bucket()
            storage_path = doc_data.get("storage_path")
            if storage_path:
                blob = bucket.blob(storage_path)
                if blob.exists():
                    blob.delete()
        except Exception as e:
            logger.warning(f"Failed to delete file from storage: {str(e)}")
        
        # Delete from Firestore
        doc_ref.delete()
        
        return {"message": "Document deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting document: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete document"
        )


@router.get("/documents/{doc_id}/download", response_class=FileResponse)
async def download_document(
    doc_id: str,
    current_user: UserInDB = Depends(get_current_user)
):
    """
    Download a document file
    """
    try:
        # Check if document exists
        doc_ref = db.collection("user_documents").document(doc_id)
        doc = doc_ref.get()
        
        if not doc.exists:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Document not found"
            )
        
        doc_data = doc.to_dict()
        
        # Check if user owns this document
        if doc_data.get("user_id") != current_user.uid:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to download this document"
            )
        
        # Get file from Firebase Storage
        bucket = storage.bucket()
        storage_path = doc_data.get("storage_path")
        
        if not storage_path:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="File not found in storage"
            )
        
        blob = bucket.blob(storage_path)
        
        if not blob.exists():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="File not found in storage"
            )
        
        # Download file content
        file_content = blob.download_as_bytes()
        
        # Return file response
        return Response(
            content=file_content,
            media_type=doc_data.get("mime_type", "application/octet-stream"),
            headers={
                "Content-Disposition": f"attachment; filename={doc_data.get('file_name', 'document')}"
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error downloading document: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to download document"
        )


@router.get("/documents/stats", response_model=dict)
async def get_document_stats(
    current_user: UserInDB = Depends(get_current_user)
):
    """
    Get document statistics for the user
    """
    try:
        # Get all user documents
        docs_query = db.collection("user_documents").where("user_id", "==", current_user.uid)
        docs = docs_query.stream()
        
        stats = {
            "total_documents": 0,
            "by_type": {},
            "by_status": {},
            "total_size_bytes": 0,
            "recent_uploads": 0
        }
        
        now = datetime.utcnow()
        seven_days_ago = datetime(now.year, now.month, now.day - 7)
        
        for doc in docs:
            doc_data = doc.to_dict()
            stats["total_documents"] += 1
            
            # Count by type
            doc_type = doc_data.get("doc_type", "unknown")
            stats["by_type"][doc_type] = stats["by_type"].get(doc_type, 0) + 1
            
            # Count by status
            doc_status = doc_data.get("status", "unknown")
            stats["by_status"][doc_status] = stats["by_status"].get(doc_status, 0) + 1
            
            # Sum file sizes
            file_size = doc_data.get("file_size", 0)
            stats["total_size_bytes"] += file_size
            
            # Count recent uploads
            uploaded_at = doc_data.get("uploaded_at")
            if uploaded_at and uploaded_at >= seven_days_ago:
                stats["recent_uploads"] += 1
        
        # Convert bytes to MB
        stats["total_size_mb"] = round(stats["total_size_bytes"] / (1024 * 1024), 2)
        
        return stats
        
    except Exception as e:
        logger.error(f"Error getting document stats: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get document statistics"
        )
