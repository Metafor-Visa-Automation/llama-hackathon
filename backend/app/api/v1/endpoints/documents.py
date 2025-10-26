from fastapi import APIRouter, HTTPException, status, Depends, UploadFile, File
from firebase_admin import storage
from app.core.firebase import db
from app.models.schemas import DocumentResponse
from app.services.security import get_current_user, UserInDB
from datetime import datetime
from typing import List
import uuid
import os

router = APIRouter()


@router.post("/documents", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
async def upload_document(
    file: UploadFile = File(...),
    current_user: UserInDB = Depends(get_current_user)
):
    """
    Upload a document file to Firebase Storage
    
    Accepts: PNG, JPEG, or PDF files
    Max size: 10MB
    
    This endpoint:
    1. Validates file type (PNG, JPEG, PDF only)
    2. Validates file size (10MB max)
    3. Uploads to Firebase Storage
    4. Creates document record in Firestore
    5. Returns document information
    """
    try:
        # Validate file
        if not file.filename:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No file provided"
            )
        
        # Read file content
        file_content = await file.read()
        
        # Validate file size (10MB limit)
        if len(file_content) > 10 * 1024 * 1024:  # 10MB
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="File size exceeds 10MB limit"
            )
        
        # Validate file type (PNG, JPEG, PDF only)
        allowed_types = {
            'image/png': '.png',
            'image/jpeg': '.jpg',
            'image/jpg': '.jpg',
            'application/pdf': '.pdf'
        }
        
        file_type = file.content_type
        if file_type not in allowed_types:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File type not allowed. Allowed types: PNG, JPEG, PDF"
            )
        
        # Generate document ID
        doc_id = str(uuid.uuid4())
        now = datetime.utcnow()
        
        # Get file extension
        file_extension = allowed_types[file_type]
        original_filename = file.filename
        filename_without_ext = os.path.splitext(original_filename)[0]
        
        # Create storage path
        storage_path = f"users/{current_user.uid}/documents/{doc_id}{file_extension}"
        
        # Upload to Firebase Storage
        bucket = storage.bucket()
        blob = bucket.blob(storage_path)
        blob.upload_from_string(file_content, content_type=file_type)
        
        # Make file publicly accessible (or use signed URLs for production)
        blob.make_public()
        
        # Get download URL
        download_url = blob.public_url
        
        # Create document record in Firestore
        document_doc = {
            "doc_id": doc_id,
            "user_id": current_user.uid,
            "storage_path": storage_path,
            "file_name": original_filename,
            "file_size": len(file_content),
            "mime_type": file_type,
            "download_url": download_url,
            "status": "PENDING_VALIDATION",
            "created_at": now,
            "updated_at": now
        }
        
        db.collection('documents').document(doc_id).set(document_doc)
        
        return DocumentResponse(
            doc_id=doc_id,
            user_id=current_user.uid,
            storage_path=storage_path,
            file_name=original_filename,
            file_size=len(file_content),
            mime_type=file_type,
            download_url=download_url,
            status="PENDING_VALIDATION",
            created_at=now,
            updated_at=now
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to upload document: {str(e)}"
        )


@router.get("/documents", response_model=List[DocumentResponse])
async def get_user_documents(current_user: UserInDB = Depends(get_current_user)):
    """
    Get all documents for the current user
    """
    try:
        documents_query = db.collection('documents').where(
            'user_id', '==', current_user.uid
        ).stream()
        
        documents = []
        for doc in documents_query:
            doc_data = doc.to_dict()
            documents.append(DocumentResponse(
                doc_id=doc_data['doc_id'],
                user_id=doc_data['user_id'],
                storage_path=doc_data['storage_path'],
                file_name=doc_data.get('file_name'),
                file_size=doc_data.get('file_size'),
                mime_type=doc_data.get('mime_type'),
                download_url=doc_data.get('download_url'),
                status=doc_data['status'],
                created_at=doc_data['created_at'],
                updated_at=doc_data['updated_at']
            ))
        
        return documents
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch documents: {str(e)}"
        )


@router.get("/documents/{doc_id}", response_model=DocumentResponse)
async def get_document(
    doc_id: str,
    current_user: UserInDB = Depends(get_current_user)
):
    """
    Get a specific document
    """
    try:
        doc = db.collection('documents').document(doc_id).get()
        
        if not doc.exists:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Document not found"
            )
        
        doc_data = doc.to_dict()
        
        # Verify ownership
        if doc_data['user_id'] != current_user.uid:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
        
        return DocumentResponse(
            doc_id=doc_data['doc_id'],
            user_id=doc_data['user_id'],
            storage_path=doc_data['storage_path'],
            file_name=doc_data.get('file_name'),
            file_size=doc_data.get('file_size'),
            mime_type=doc_data.get('mime_type'),
            download_url=doc_data.get('download_url'),
            status=doc_data['status'],
            created_at=doc_data['created_at'],
            updated_at=doc_data['updated_at']
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get document: {str(e)}"
        )


@router.put("/documents/{doc_id}")
async def update_document_status(
    doc_id: str,
    status: str,
    current_user: UserInDB = Depends(get_current_user)
):
    """
    Update document status (e.g., "APPROVED", "REJECTED")
    """
    try:
        doc = db.collection('documents').document(doc_id).get()
        
        if not doc.exists:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Document not found"
            )
        
        doc_data = doc.to_dict()
        
        # Verify ownership
        if doc_data['user_id'] != current_user.uid:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
        
        # Update status
        db.collection('documents').document(doc_id).update({
            "status": status,
            "updated_at": datetime.utcnow()
        })
        
        return {"message": "Document status updated successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update document: {str(e)}"
        )


@router.delete("/documents/{doc_id}")
async def delete_document(
    doc_id: str,
    current_user: UserInDB = Depends(get_current_user)
):
    """
    Delete a document
    Removes both Firestore record and file from Firebase Storage
    """
    try:
        doc = db.collection('documents').document(doc_id).get()
        
        if not doc.exists:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Document not found"
            )
        
        doc_data = doc.to_dict()
        
        # Verify ownership
        if doc_data['user_id'] != current_user.uid:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
        
        # Delete from Firebase Storage
        storage_path = doc_data.get('storage_path')
        if storage_path:
            try:
                bucket = storage.bucket()
                blob = bucket.blob(storage_path)
                blob.delete()
            except Exception as e:
                print(f"Warning: Could not delete file from storage: {e}")
        
        # Delete document record from Firestore
        db.collection('documents').document(doc_id).delete()
        
        return {"message": "Document deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete document: {str(e)}"
        )
