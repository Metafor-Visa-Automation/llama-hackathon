from fastapi import APIRouter, HTTPException, status, Depends, UploadFile, File
from app.core.firebase import db, bucket
from app.models.schemas import DocumentResponse, DocumentInDB, DocumentStatus, TaskStatus
from app.services.security import get_current_user, UserInDB
from datetime import datetime
import uuid
import os

router = APIRouter()


@router.post("/docs/task/{task_id}/upload", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
async def upload_document(
    task_id: str,
    file: UploadFile = File(...),
    current_user: UserInDB = Depends(get_current_user)
):
    """
    Upload a document for a specific task
    """
    try:
        # Step 1: Verify Task exists and belongs to current user
        task_doc = db.collection('TASK').document(task_id).get()
        if not task_doc.exists:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found"
            )
        
        task_data = task_doc.to_dict()
        if task_data['user_id'] != current_user.uid:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied: Task does not belong to current user"
            )
        
        # Step 2: Validate file
        if not file.filename:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No file provided"
            )
        
        # Check file size (limit to 10MB)
        file_content = await file.read()
        if len(file_content) > 10 * 1024 * 1024:  # 10MB
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="File size exceeds 10MB limit"
            )
        
        # Check file type (allow common document types)
        allowed_extensions = {'.pdf', '.jpg', '.jpeg', '.png', '.doc', '.docx'}
        file_extension = os.path.splitext(file.filename)[1].lower()
        if file_extension not in allowed_extensions:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File type not allowed. Allowed types: {', '.join(allowed_extensions)}"
            )
        
        # Step 3: Generate unique filename and upload to Firebase Storage
        doc_id = str(uuid.uuid4())
        unique_filename = f"{doc_id}{file_extension}"
        storage_path = f"user_documents/{current_user.uid}/{task_data['application_id']}/{unique_filename}"
        
        # Upload to Firebase Storage
        blob = bucket.blob(storage_path)
        blob.upload_from_string(file_content, content_type=file.content_type)
        
        # Make the file publicly accessible (optional, depending on your security needs)
        # blob.make_public()
        
        # Step 4: Create Document record in Firestore
        now = datetime.utcnow()
        document_doc = {
            "doc_id": doc_id,
            "task_id": task_id,
            "user_id": current_user.uid,
            "storage_path": storage_path,
            "status": DocumentStatus.PENDING_VALIDATION.value,
            "created_at": now,
            "updated_at": now
        }
        
        db.collection('USER_DOCUMENT').document(doc_id).set(document_doc)
        
        # Step 5: Update Task status to DONE
        db.collection('TASK').document(task_id).update({
            "status": TaskStatus.DONE.value,
            "updated_at": now
        })
        
        return DocumentResponse(
            doc_id=doc_id,
            task_id=task_id,
            user_id=current_user.uid,
            storage_path=storage_path,
            status=DocumentStatus.PENDING_VALIDATION,
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


@router.get("/docs/task/{task_id}", response_model=list[DocumentResponse])
async def get_task_documents(
    task_id: str,
    current_user: UserInDB = Depends(get_current_user)
):
    """
    Get all documents for a specific task
    """
    try:
        # Verify Task exists and belongs to current user
        task_doc = db.collection('TASK').document(task_id).get()
        if not task_doc.exists:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found"
            )
        
        task_data = task_doc.to_dict()
        if task_data['user_id'] != current_user.uid:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied: Task does not belong to current user"
            )
        
        # Fetch all documents for this task
        docs_query = db.collection('USER_DOCUMENT').where(
            'task_id', '==', task_id
        ).where('user_id', '==', current_user.uid).stream()
        
        documents = []
        for doc in docs_query:
            doc_data = doc.to_dict()
            documents.append(DocumentResponse(
                doc_id=doc_data['doc_id'],
                task_id=doc_data['task_id'],
                user_id=doc_data['user_id'],
                storage_path=doc_data['storage_path'],
                status=doc_data['status'],
                created_at=doc_data['created_at'],
                updated_at=doc_data['updated_at']
            ))
        
        return documents
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch documents: {str(e)}"
        )


@router.delete("/docs/{doc_id}")
async def delete_document(
    doc_id: str,
    current_user: UserInDB = Depends(get_current_user)
):
    """
    Delete a document
    """
    try:
        # Verify document exists and belongs to current user
        doc_ref = db.collection('USER_DOCUMENT').document(doc_id)
        doc_doc = doc_ref.get()
        
        if not doc_doc.exists:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Document not found"
            )
        
        doc_data = doc_doc.to_dict()
        if doc_data['user_id'] != current_user.uid:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied: Document does not belong to current user"
            )
        
        # Delete from Firebase Storage
        try:
            blob = bucket.blob(doc_data['storage_path'])
            blob.delete()
        except Exception as e:
            # Log error but don't fail the operation if storage deletion fails
            print(f"Warning: Failed to delete file from storage: {str(e)}")
        
        # Delete from Firestore
        doc_ref.delete()
        
        return {"message": "Document deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete document: {str(e)}"
        )
