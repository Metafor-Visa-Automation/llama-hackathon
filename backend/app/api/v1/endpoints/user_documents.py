"""
User Document Management API Endpoints
Handles document upload, listing, updating, and deletion
"""

from fastapi import APIRouter, HTTPException, status, Depends, UploadFile, File, Query, BackgroundTasks
from fastapi.responses import FileResponse, Response
from app.core.firebase import db
from app.models.schemas import (
    UserDocumentUpload, UserDocumentUpdate, UserDocumentResponse, 
    DocumentType, DocumentStatus
)
from app.services.security import get_current_user, UserInDB
from app.services.groq_ocr_service import GroqOCRService
from datetime import datetime
from typing import List, Optional
import uuid
import logging
import os
from firebase_admin import storage

logger = logging.getLogger(__name__)
router = APIRouter()

# Initialize Groq OCR service
groq_ocr_service = GroqOCRService()


async def process_document_with_ocr(doc_id: str, file_content: bytes, mime_type: str, document_type: str, file_name: str, user_id: str):
    """
    Background task to process document with OCR and update user profile
    """
    try:
        logger.info(f"Starting OCR processing for document {doc_id}")
        
        # Extract data using Groq OCR
        ocr_result = groq_ocr_service.extract_document_data(
            file_data=file_content,
            mime_type=mime_type,
            document_type=document_type,
            file_name=file_name
        )
        
        # Update document with OCR results
        update_data = {
            "ocr_result": ocr_result,
            "updated_at": datetime.utcnow()
        }
        
        if ocr_result.get("success"):
            update_data["status"] = DocumentStatus.VALIDATED.value
            extracted_data = ocr_result.get("extracted_data", {})
            
            # Try to extract common fields for document
            if document_type == "passport":
                if "expiryDate" in extracted_data:
                    update_data["expiry_date"] = extracted_data["expiryDate"]
                if "issueDate" in extracted_data:
                    update_data["issued_date"] = extracted_data["issueDate"]
            elif document_type == "travel_insurance":
                if "coverageEndDate" in extracted_data:
                    update_data["expiry_date"] = extracted_data["coverageEndDate"]
            
            # Update user profile with extracted personal information
            await _update_user_profile_from_ocr(user_id, document_type, extracted_data)
            
            logger.info(f"OCR processing successful for document {doc_id}")
        else:
            update_data["status"] = DocumentStatus.REJECTED.value
            logger.warning(f"OCR processing failed for document {doc_id}: {ocr_result.get('error')}")
        
        db.collection("user_documents").document(doc_id).update(update_data)
        
    except Exception as e:
        logger.error(f"Error in OCR background task for document {doc_id}: {str(e)}")
        # Update document status to failed
        db.collection("user_documents").document(doc_id).update({
            "status": DocumentStatus.REJECTED.value,
            "ocr_result": {"error": str(e)},
            "updated_at": datetime.utcnow()
        })


async def _update_user_profile_from_ocr(user_id: str, document_type: str, extracted_data: dict):
    """
    Update user profile with information extracted from OCR
    
    Args:
        user_id: User ID
        document_type: Type of document processed
        extracted_data: Data extracted from OCR
    """
    try:
        user_ref = db.collection("users").document(user_id)
        user_doc = user_ref.get()
        
        if not user_doc.exists:
            logger.warning(f"User {user_id} not found, skipping profile update")
            return
        
        user_updates = {}
        
        # Extract info based on document type
        if document_type == "passport":
            # Update passport information
            if "passportNumber" in extracted_data:
                user_updates["passport_number"] = extracted_data["passportNumber"]
            if "surname" in extracted_data and "givenName" in extracted_data:
                user_updates["name"] = extracted_data["givenName"]
                user_updates["surname"] = extracted_data["surname"]
            if "dateOfBirth" in extracted_data:
                user_updates["date_of_birth"] = extracted_data["dateOfBirth"]
            if "countryCode" in extracted_data:
                user_updates["nationality"] = extracted_data["countryCode"]
            if "expiryDate" in extracted_data:
                user_updates["passport_expiry_date"] = extracted_data["expiryDate"]
            if "issueDate" in extracted_data:
                user_updates["passport_issue_date"] = extracted_data["issueDate"]
                
        elif document_type in ["id_card", "kimlikon"]:
            # Update ID card information
            if "idNumber" in extracted_data:
                user_updates["tc_kimlik_no"] = extracted_data["idNumber"]
            if "fullName" in extracted_data:
                # Split full name if needed
                parts = extracted_data["fullName"].split()
                if len(parts) >= 2:
                    user_updates["name"] = " ".join(parts[:-1])
                    user_updates["surname"] = parts[-1]
            if "dateOfBirth" in extracted_data:
                user_updates["date_of_birth"] = extracted_data["dateOfBirth"]
            if "placeOfBirth" in extracted_data:
                user_updates["place_of_birth"] = extracted_data["placeOfBirth"]
            if "nationality" in extracted_data:
                user_updates["nationality"] = extracted_data["nationality"]
                
        elif document_type == "birth_certificate" or document_type == "dogumsertifikasi":
            # Update birth certificate information
            if "fullName" in extracted_data:
                parts = extracted_data["fullName"].split()
                if len(parts) >= 2:
                    user_updates["name"] = " ".join(parts[:-1])
                    user_updates["surname"] = parts[-1]
            if "dateOfBirth" in extracted_data:
                user_updates["date_of_birth"] = extracted_data["dateOfBirth"]
            if "placeOfBirth" in extracted_data:
                user_updates["place_of_birth"] = extracted_data["placeOfBirth"]
            if "tcKimlikNo" in extracted_data:
                user_updates["tc_kimlik_no"] = extracted_data["tcKimlikNo"]
            if "fatherName" in extracted_data:
                user_updates["father_name"] = extracted_data["fatherName"]
            if "motherName" in extracted_data:
                user_updates["mother_name"] = extracted_data["motherName"]
                
        elif document_type in ["drivers_license", "surucuon"]:
            # Update driver's license information
            if "licenseNumber" in extracted_data:
                user_updates["drivers_license_number"] = extracted_data["licenseNumber"]
            if "fullName" in extracted_data:
                parts = extracted_data["fullName"].split()
                if len(parts) >= 2:
                    user_updates["name"] = " ".join(parts[:-1])
                    user_updates["surname"] = parts[-1]
            if "dateOfBirth" in extracted_data:
                user_updates["date_of_birth"] = extracted_data["dateOfBirth"]
                
        elif document_type == "diploma":
            # Update education information
            if "institutionName" in extracted_data:
                user_updates["last_education_institution"] = extracted_data["institutionName"]
            if "degreeType" in extracted_data and "major" in extracted_data:
                user_updates["last_degree"] = f"{extracted_data['degreeType']} in {extracted_data['major']}"
            if "graduationDate" in extracted_data:
                user_updates["graduation_date"] = extracted_data["graduationDate"]
            if "gpa" in extracted_data:
                user_updates["gpa"] = extracted_data["gpa"]
        
        # Only update if we have new data
        if user_updates:
            user_updates["updated_at"] = datetime.utcnow()
            user_ref.update(user_updates)
            logger.info(f"Updated user {user_id} profile with {len(user_updates)} fields from {document_type}")
        else:
            logger.info(f"No relevant user profile updates from {document_type}")
            
    except Exception as e:
        logger.error(f"Error updating user profile from OCR: {str(e)}")
        # Don't raise - profile update failure shouldn't fail the OCR process


@router.post("/upload", response_model=UserDocumentResponse, status_code=status.HTTP_201_CREATED)
async def upload_document(
    background_tasks: BackgroundTasks,
    document_type: DocumentType,
    document_title: str,
    file: UploadFile = File(...),
    notes: Optional[str] = None,
    tags: Optional[str] = None,
    auto_ocr: bool = True,
    current_user: UserInDB = Depends(get_current_user)
):
    """
    Upload a new document with automatic OCR processing
    
    Args:
        background_tasks: FastAPI background tasks
        document_type: Type of document being uploaded
        document_title: Title/description of the document
        file: The document file
        notes: Optional notes about the document
        tags: Comma-separated tags
        auto_ocr: Whether to automatically process with OCR (default: True)
        current_user: Current authenticated user
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
        
        # Trigger OCR processing in background if enabled
        if auto_ocr:
            logger.info(f"Scheduling OCR processing for document {doc_id}")
            background_tasks.add_task(
                process_document_with_ocr,
                doc_id=doc_id,
                file_content=file_content,
                mime_type=file.content_type or "application/octet-stream",
                document_type=document_type.value,
                file_name=file.filename,
                user_id=current_user.uid
            )
        
        return UserDocumentResponse(**doc_data)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error uploading document: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to upload document"
        )


@router.post("/{doc_id}/process-ocr", response_model=dict)
async def trigger_ocr_processing(
    doc_id: str,
    background_tasks: BackgroundTasks,
    current_user: UserInDB = Depends(get_current_user)
):
    """
    Manually trigger OCR processing for an existing document
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
                detail="You don't have permission to process this document"
            )
        
        # Download file from storage
        bucket = storage.bucket()
        storage_path = doc_data.get("storage_path")
        
        if not storage_path:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Document storage path not found"
            )
        
        blob = bucket.blob(storage_path)
        
        if not blob.exists():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Document file not found in storage"
            )
        
        # Download file content
        file_content = blob.download_as_bytes()
        
        # Update status to processing
        doc_ref.update({
            "status": DocumentStatus.PENDING_VALIDATION.value,
            "updated_at": datetime.utcnow()
        })
        
        # Schedule OCR processing
        background_tasks.add_task(
            process_document_with_ocr,
            doc_id=doc_id,
            file_content=file_content,
            mime_type=doc_data.get("mime_type", "application/octet-stream"),
            document_type=doc_data.get("doc_type"),
            file_name=doc_data.get("file_name"),
            user_id=current_user.uid
        )
        
        return {
            "message": "OCR processing started",
            "doc_id": doc_id,
            "status": "processing"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error triggering OCR processing: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to trigger OCR processing: {str(e)}"
        )


@router.get("", response_model=List[UserDocumentResponse])
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
        # Build query - using filter parameter to avoid deprecation warning
        query = db.collection("user_documents").where(filter=("user_id", "==", current_user.uid))
        
        if document_type:
            query = query.where(filter=("doc_type", "==", document_type.value))
        
        if status_filter:
            query = query.where(filter=("status", "==", status_filter.value))
        
        # Get all documents for the user
        docs = query.stream()
        
        # Convert to list and sort in Python to avoid index requirement
        documents = []
        for doc in docs:
            doc_data = doc.to_dict()
            documents.append(UserDocumentResponse(**doc_data))
        
        # Sort by upload date (newest first) in Python
        documents.sort(key=lambda x: x.uploaded_at if x.uploaded_at else datetime.min, reverse=True)
        
        # Apply pagination in Python
        start_idx = offset
        end_idx = offset + limit
        paginated_documents = documents[start_idx:end_idx]
        
        return paginated_documents
        
    except Exception as e:
        logger.error(f"Error getting user documents: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get documents"
        )


@router.get("/{doc_id}", response_model=UserDocumentResponse)
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


@router.put("/{doc_id}", response_model=UserDocumentResponse)
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


@router.delete("/{doc_id}", response_model=dict)
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


@router.get("/{doc_id}/download", response_class=FileResponse)
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


@router.get("/stats", response_model=dict)
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


@router.get("/{doc_id}/ocr-analysis", response_model=dict)
async def get_document_ocr_analysis(
    doc_id: str,
    current_user: UserInDB = Depends(get_current_user)
):
    """
    Get OCR analysis results for a specific document
    
    Returns the extracted data, confidence score, and validation details from OCR processing
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
                detail="You don't have permission to access this document"
            )
        
        # Get OCR result
        ocr_result = doc_data.get("ocr_result")
        
        if ocr_result is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="OCR analysis not available for this document. The document may still be processing or OCR was not enabled during upload."
            )
        
        # Return OCR analysis with document context
        return {
            "doc_id": doc_id,
            "document_title": doc_data.get("document_title"),
            "doc_type": doc_data.get("doc_type"),
            "status": doc_data.get("status"),
            "file_name": doc_data.get("file_name"),
            "ocr_result": ocr_result,
            "uploaded_at": doc_data.get("uploaded_at"),
            "updated_at": doc_data.get("updated_at")
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting OCR analysis: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get OCR analysis"
        )
