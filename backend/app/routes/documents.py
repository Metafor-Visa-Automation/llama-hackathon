from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, status
from app.models.schemas import Document, DocumentCreate, DocumentType
from app.routes.auth import get_current_user
from app.core.firebase import get_firestore_db
from app.core.config import settings
from datetime import datetime
import uuid
import os
import shutil
from typing import List

router = APIRouter()

# Create uploads directory if it doesn't exist
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/upload", response_model=Document)
async def upload_document(
    visa_application_id: str,
    document_type: DocumentType,
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user)
):
    """Upload a document for visa application"""
    try:
        # Validate file size
        if file.size > settings.max_file_size:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"File size exceeds maximum allowed size of {settings.max_file_size} bytes"
            )
        
        # Validate file type
        if file.content_type not in settings.allowed_file_types:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File type {file.content_type} not allowed"
            )
        
        # Generate unique filename
        file_extension = file.filename.split('.')[-1] if '.' in file.filename else ''
        unique_filename = f"{uuid.uuid4()}.{file_extension}"
        file_path = os.path.join(UPLOAD_DIR, unique_filename)
        
        # Save file
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Create document record
        db = get_firestore_db()
        document_id = str(uuid.uuid4())
        
        document_doc = {
            "id": document_id,
            "user_id": current_user["uid"],
            "visa_application_id": visa_application_id,
            "document_type": document_type.value,
            "filename": file.filename,
            "file_path": file_path,
            "file_size": file.size,
            "mime_type": file.content_type,
            "uploaded_at": datetime.utcnow(),
            "ocr_data": None,
            "validation_status": "pending",
            "validation_errors": None
        }
        
        db.collection("documents").document(document_id).set(document_doc)
        
        return Document(**document_doc)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to upload document: {str(e)}"
        )

@router.get("/", response_model=List[Document])
async def get_user_documents(current_user: dict = Depends(get_current_user)):
    """Get all documents for current user"""
    try:
        db = get_firestore_db()
        
        documents = db.collection("documents")\
            .where("user_id", "==", current_user["uid"])\
            .order_by("uploaded_at", direction="DESCENDING")\
            .stream()
        
        document_list = []
        for doc in documents:
            doc_data = doc.to_dict()
            document_list.append(Document(**doc_data))
        
        return document_list
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get documents: {str(e)}"
        )

@router.get("/application/{visa_application_id}", response_model=List[Document])
async def get_application_documents(
    visa_application_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get all documents for a specific visa application"""
    try:
        db = get_firestore_db()
        
        documents = db.collection("documents")\
            .where("user_id", "==", current_user["uid"])\
            .where("visa_application_id", "==", visa_application_id)\
            .order_by("uploaded_at", direction="DESCENDING")\
            .stream()
        
        document_list = []
        for doc in documents:
            doc_data = doc.to_dict()
            document_list.append(Document(**doc_data))
        
        return document_list
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get application documents: {str(e)}"
        )

@router.get("/{document_id}", response_model=Document)
async def get_document(
    document_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get specific document by ID"""
    try:
        db = get_firestore_db()
        
        doc_ref = db.collection("documents").document(document_id).get()
        
        if not doc_ref.exists:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Document not found"
            )
        
        doc_data = doc_ref.to_dict()
        
        # Check if user owns this document
        if doc_data["user_id"] != current_user["uid"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
        
        return Document(**doc_data)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get document: {str(e)}"
        )

@router.delete("/{document_id}")
async def delete_document(
    document_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Delete document"""
    try:
        db = get_firestore_db()
        
        # Check if document exists and user owns it
        doc_ref = db.collection("documents").document(document_id).get()
        if not doc_ref.exists:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Document not found"
            )
        
        doc_data = doc_ref.to_dict()
        if doc_data["user_id"] != current_user["uid"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
        
        # Delete file from filesystem
        file_path = doc_data["file_path"]
        if os.path.exists(file_path):
            os.remove(file_path)
        
        # Delete document record
        db.collection("documents").document(document_id).delete()
        
        return {"message": "Document deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete document: {str(e)}"
        )

@router.post("/{document_id}/validate")
async def validate_document(
    document_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Validate document using OCR and AI"""
    try:
        db = get_firestore_db()
        
        # Check if document exists and user owns it
        doc_ref = db.collection("documents").document(document_id).get()
        if not doc_ref.exists:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Document not found"
            )
        
        doc_data = doc_ref.to_dict()
        if doc_data["user_id"] != current_user["uid"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
        
        # This is a placeholder for OCR and validation functionality
        # In the actual implementation, this would:
        # 1. Extract text using OCR (Tesseract)
        # 2. Validate document content using AI
        # 3. Check for inconsistencies with visa application data
        
        validation_result = {
            "validation_status": "completed",
            "ocr_data": {
                "extracted_text": "Placeholder OCR text extraction",
                "confidence": 0.95
            },
            "validation_errors": [],
            "warnings": ["This is a placeholder validation result"]
        }
        
        # Update document with validation results
        db.collection("documents").document(document_id).update({
            "validation_status": validation_result["validation_status"],
            "ocr_data": validation_result["ocr_data"],
            "validation_errors": validation_result["validation_errors"]
        })
        
        return validation_result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to validate document: {str(e)}"
        )
