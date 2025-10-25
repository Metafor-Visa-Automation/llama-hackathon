from fastapi import APIRouter, HTTPException, status, Depends, File, UploadFile
from app.core.firebase import db
from app.models.schemas import (
    ApplicationCreate, ApplicationResponse, ApplicationInDB,
    TaskResponse, TaskInDB, ApplicationStatus, TaskStatus,
    ApplicationUpdate, ApplicationSubmit, ApplicationProgressUpdate,
    ApplicationGenerateLetter, ProfileType, PassportType
)
from app.services.security import get_current_user, UserInDB
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
import uuid
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


class VisaApplicationQuestionnaire(BaseModel):
    """Questionnaire for automatic visa application creation"""
    origin_country: str = Field(..., description="Country of origin (e.g., 'TR')")
    destination_country: str = Field(..., description="Destination country (e.g., 'DE')")
    passport_type: PassportType = Field(..., description="Type of passport")
    profile_type: ProfileType = Field(..., description="Type of traveler profile")
    travel_purpose: str = Field(..., description="Purpose of travel (tourism, business, study, etc.)")
    intended_arrival_date: str = Field(..., description="Intended arrival date (YYYY-MM-DD)")
    intended_departure_date: str = Field(..., description="Intended departure date (YYYY-MM-DD)")
    duration_of_stay: int = Field(..., description="Duration of stay in days")
    accommodation_type: str = Field(..., description="Type of accommodation (hotel, family, business)")
    has_invitation: bool = Field(False, description="Whether user has an invitation letter")
    has_travel_insurance: bool = Field(False, description="Whether user has travel insurance")
    has_financial_support: bool = Field(True, description="Whether user has financial support")
    additional_notes: Optional[str] = Field(None, description="Additional notes or special circumstances")


class AutoApplicationResponse(BaseModel):
    """Response for automatic application creation"""
    application_id: str
    user_id: str
    requirement_id: str
    status: ApplicationStatus
    travel_details: Dict[str, Any]
    required_documents: List[Dict[str, Any]]
    total_documents_required: int
    application_progress: Dict[str, Any]
    created_at: datetime
    updated_at: datetime


class ApplicationCreateRequest(BaseModel):
    """Request for creating application with questionnaire only (no documents yet)"""
    questionnaire: VisaApplicationQuestionnaire


class ApplicationUpdateDocumentsRequest(BaseModel):
    """Request for updating application with required documents from external source"""
    template_names: List[str] = Field(..., description="Array of checklist template names from external source")


@router.post("/applications/create", response_model=AutoApplicationResponse, status_code=status.HTTP_201_CREATED)
async def create_application_with_questionnaire(
    request: ApplicationCreateRequest,
    current_user: UserInDB = Depends(get_current_user)
):
    """
    Create a visa application with questionnaire only
    Documents will be added later via update request from external source
    """
    try:
        questionnaire = request.questionnaire
        
        # Step 1: Determine visa requirement ID based on origin/destination
        requirement_id = f"{questionnaire.origin_country.lower()}_{questionnaire.destination_country.lower()}_all"
        
        # Step 2: Create application ID and basic data
        app_id = str(uuid.uuid4())
        now = datetime.utcnow()
        
        # Step 3: Prepare travel details
        travel_details = {
            "origin_country": questionnaire.origin_country,
            "destination_country": questionnaire.destination_country,
            "passport_type": questionnaire.passport_type.value,
            "profile_type": questionnaire.profile_type.value,
            "travel_purpose": questionnaire.travel_purpose,
            "intended_arrival_date": questionnaire.intended_arrival_date,
            "intended_departure_date": questionnaire.intended_departure_date,
            "duration_of_stay": questionnaire.duration_of_stay,
            "accommodation_type": questionnaire.accommodation_type,
            "has_invitation": questionnaire.has_invitation,
            "has_travel_insurance": questionnaire.has_travel_insurance,
            "has_financial_support": questionnaire.has_financial_support,
            "additional_notes": questionnaire.additional_notes
        }
        
        # Step 4: Create application document (without documents yet)
        application_doc = {
            "app_id": app_id,
            "user_id": current_user.uid,
            "requirement_id": requirement_id,
            "status": ApplicationStatus.DRAFT.value,
            "travel_details": travel_details,
            "required_documents": [],  # Empty initially
            "total_documents_required": 0,  # Will be updated later
            "completed_documents": 0,
            "documents_pending": True,  # Flag to indicate documents are coming
            "external_source": True,  # Flag to indicate external document source
            "application_progress": {
                "total_tasks": 0,
                "completed_tasks": 0,
                "pending_tasks": 0,
                "completion_percentage": 0,
                "status": "waiting_for_documents"
            },
            "created_at": now,
            "updated_at": now
        }
        
        # Step 5: Save application to database
        db.collection('APPLICATION').document(app_id).set(application_doc)
        
        return AutoApplicationResponse(
            application_id=app_id,
            user_id=current_user.uid,
            requirement_id=requirement_id,
            status=ApplicationStatus.DRAFT,
            travel_details=travel_details,
            required_documents=[],  # Empty initially
            total_documents_required=0,  # Will be updated later
            application_progress=application_doc["application_progress"],
            created_at=now,
            updated_at=now
        )
        
    except Exception as e:
        logger.error(f"Error creating application: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create application: {str(e)}"
        )


@router.put("/applications/{app_id}/update-documents", response_model=AutoApplicationResponse)
async def update_application_with_documents(
    app_id: str,
    request: ApplicationUpdateDocumentsRequest,
    current_user: UserInDB = Depends(get_current_user)
):
    """
    Update application with required documents from external source
    This starts the document upload flow
    """
    try:
        # Step 1: Verify application exists and belongs to current user
        app_ref = db.collection('APPLICATION').document(app_id)
        app_doc = app_ref.get()
        
        if not app_doc.exists:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Application not found"
            )
        
        app_data = app_doc.to_dict()
        if app_data['user_id'] != current_user.uid:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied: Application does not belong to current user"
            )
        
        # Step 2: Fetch and process checklist templates based on template names
        required_documents = await _fetch_and_process_templates(request.template_names)
        
        # Step 3: Update application with documents
        now = datetime.utcnow()
        update_data = {
            "required_documents": required_documents,
            "total_documents_required": len(required_documents),
            "documents_pending": False,  # Documents received
            "application_progress": {
                "total_tasks": len(required_documents),
                "completed_tasks": 0,
                "pending_tasks": len(required_documents),
                "completion_percentage": 0,
                "status": "ready_for_upload"
            },
            "updated_at": now
        }
        
        app_ref.update(update_data)
        
        # Step 4: Create tasks for each required document
        tasks_to_create = []
        for i, doc_template in enumerate(required_documents):
            task_id = str(uuid.uuid4())
            task_doc = {
                "task_id": task_id,
                "application_id": app_id,
                "user_id": current_user.uid,
                "template_id": doc_template.get("checkId", f"doc_{i+1}"),
                "title": doc_template.get("docName", f"Document {i+1}"),
                "description": doc_template.get("docDescription", ""),
                "document_type": doc_template.get("documentType", "other"),
                "page_number": i + 1,  # Track page number for step-by-step upload
                "is_mandatory": doc_template.get("mandatory", True),
                "acceptance_criteria": doc_template.get("acceptanceCriteria", []),
                "external_source": True,  # Flag for external source
                "status": TaskStatus.PENDING.value,
                "notes": None,
                "created_at": now,
                "updated_at": now
            }
            tasks_to_create.append(task_doc)
        
        # Step 5: Create all tasks in batch
        batch = db.batch()
        for task_doc in tasks_to_create:
            batch.set(
                db.collection('TASK').document(task_doc['task_id']),
                task_doc
            )
        
        batch.commit()
        
        # Step 6: Get updated application data
        updated_doc = app_ref.get()
        updated_data = updated_doc.to_dict()
        
        return AutoApplicationResponse(
            application_id=app_id,
            user_id=current_user.uid,
            requirement_id=updated_data['requirement_id'],
            status=ApplicationStatus.DRAFT,
            travel_details=updated_data['travel_details'],
            required_documents=required_documents,
            total_documents_required=len(required_documents),
            application_progress=updated_data['application_progress'],
            created_at=updated_data['created_at'],
            updated_at=now
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating application with documents: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update application with documents: {str(e)}"
        )




async def _fetch_and_process_templates(template_names: List[str]) -> List[Dict[str, Any]]:
    """
    Fetch checklist templates based on template names and sort by priority
    This matches template names to actual checklist templates and sorts by priority
    """
    try:
        # Fetch all checklist templates
        templates_query = db.collection('CHECKLIST_TEMPLATE').stream()
        all_templates = {}
        
        for template_doc in templates_query:
            template_data = template_doc.to_dict()
            template_id = template_doc.id
            
            # Store templates by both ID and docName for flexible matching
            all_templates[template_id] = template_data
            all_templates[template_data.get('docName', '')] = template_data
        
        # Match template names to actual templates
        matched_templates = []
        unmatched_names = []
        
        for template_name in template_names:
            template_data = None
            
            # Try to find template by exact name match
            if template_name in all_templates:
                template_data = all_templates[template_name]
            else:
                # Try to find by partial name match
                for key, data in all_templates.items():
                    if isinstance(key, str) and template_name.lower() in key.lower():
                        template_data = data
                        break
            
            if template_data:
                # Create document object from template
                doc_object = {
                    "checkId": template_data.get('checkId', template_name),
                    "docName": template_data.get('docName', template_name),
                    "docDescription": template_data.get('docDescription', ''),
                    "documentType": template_data.get('documentType', 'other'),
                    "mandatory": template_data.get('mandatory', True),
                    "acceptanceCriteria": template_data.get('acceptanceCriteria', []),
                    "priority": template_data.get('priority', 1),
                    "category": template_data.get('category', 'general'),
                    "referenceUrl": template_data.get('referenceUrl'),
                    "validationRules": template_data.get('validationRules', {}),
                    "isDocumentNeeded": template_data.get('isDocumentNeeded', True),
                    "requiredFor": template_data.get('requiredFor', []),
                    "external_source": True,  # Flag to indicate external source
                    "template_id": template_data.get('checkId', template_name)
                }
                
                matched_templates.append(doc_object)
            else:
                unmatched_names.append(template_name)
                logger.warning(f"Template not found: {template_name}")
        
        # Log unmatched templates
        if unmatched_names:
            logger.warning(f"Unmatched template names: {unmatched_names}")
        
        # Sort templates by priority in increasing order
        matched_templates.sort(key=lambda x: x.get('priority', 1))
        
        # Add page numbers after sorting
        for i, template in enumerate(matched_templates):
            template['pageNumber'] = i + 1
        
        logger.info(f"Processed {len(matched_templates)} templates from {len(template_names)} names")
        return matched_templates
        
    except Exception as e:
        logger.error(f"Error fetching and processing templates: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process template names: {str(e)}"
        )




# Removed _generate_required_documents function - now using AI-generated documents


@router.post("/applications/{app_id}/upload-document-page/{page_number}", response_model=dict)
async def upload_document_for_page(
    app_id: str,
    page_number: int,
    file: UploadFile = File(...),
    current_user: UserInDB = Depends(get_current_user)
):
    """
    Upload a document for a specific page in the application workflow
    This enables step-by-step document upload based on the generated checklist
    After upload, document goes to OCR for checking
    """
    try:
        # Verify the application belongs to the current user
        app_doc = db.collection('APPLICATION').document(app_id).get()
        if not app_doc.exists:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Application not found"
            )
        
        app_data = app_doc.to_dict()
        if app_data['user_id'] != current_user.uid:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied: Application does not belong to current user"
            )
        
        # Check if application is ready for upload
        if app_data.get('application_progress', {}).get('status') != 'ready_for_upload':
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Application is not ready for document upload. Documents must be provided first."
            )
        
        # Find the task for this page number
        tasks_query = db.collection('TASK').where(
            'application_id', '==', app_id
        ).where('user_id', '==', current_user.uid).where(
            'page_number', '==', page_number
        ).stream()
        
        task_docs = list(tasks_query)
        if not task_docs:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No task found for page {page_number}"
            )
        
        task_doc = task_docs[0]
        task_data = task_doc.to_dict()
        task_id = task_data['task_id']
        
        # Validate file
        if not file.filename:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No file provided"
            )
        
        # Check file size (10MB limit)
        file_content = await file.read()
        if len(file_content) > 10 * 1024 * 1024:  # 10MB
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="File size exceeds 10MB limit"
            )
        
        # Check file type
        allowed_types = ['.pdf', '.jpg', '.jpeg', '.png', '.tiff', '.bmp']
        file_extension = '.' + file.filename.split('.')[-1].lower()
        if file_extension not in allowed_types:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File type {file_extension} not allowed. Allowed types: {', '.join(allowed_types)}"
            )
        
        # Upload to Firebase Storage
        storage_path = f"users/{current_user.uid}/applications/{app_id}/page_{page_number}_{file.filename}"
        
        # Create document record in USER_DOCUMENT collection
        doc_id = str(uuid.uuid4())
        now = datetime.utcnow()
        
        document_doc = {
            "doc_id": doc_id,
            "user_id": current_user.uid,
            "application_id": app_id,
            "task_id": task_id,
            "page_number": page_number,
            "storage_path": storage_path,
            "doc_type": task_data['document_type'],
            "status": "UPLOADED",  # Initial status
            "document_title": task_data['title'],
            "file_name": file.filename,
            "file_size": len(file_content),
            "mime_type": file.content_type,
            "uploaded_at": now,
            "updated_at": now,
            "notes": None,
            "tags": f"application,page_{page_number},{task_data['document_type']}",
            "acceptance_criteria": task_data.get('acceptance_criteria', []),
            "is_mandatory": task_data.get('is_mandatory', True),
            "ocr_status": "PENDING",  # OCR status
            "ocr_results": None,
            "ocr_errors": None,
            "validation_status": "PENDING"
        }
        
        # Save document record
        db.collection('USER_DOCUMENT').document(doc_id).set(document_doc)
        
        # Update task status to IN_PROGRESS
        task_ref = db.collection('TASK').document(task_id)
        task_ref.update({
            "status": TaskStatus.IN_PROGRESS.value,
            "updated_at": now,
            "document_uploaded": True,
            "document_id": doc_id,
            "ocr_status": "PENDING"
        })
        
        # Update application progress
        await _update_application_progress(app_id, current_user.uid)
        
        # Send document to OCR for checking (async)
        await _process_document_with_ocr(doc_id, task_data['document_type'], storage_path)
        
        return {
            "success": True,
            "message": f"Document uploaded successfully for page {page_number}",
            "document_id": doc_id,
            "task_id": task_id,
            "page_number": page_number,
            "document_type": task_data['document_type'],
            "file_name": file.filename,
            "file_size": len(file_content),
            "storage_path": storage_path,
            "ocr_status": "PENDING",
            "next_page": page_number + 1 if page_number < app_data['total_documents_required'] else None,
            "application_progress": await _get_application_progress(app_id, current_user.uid),
            "can_continue": True,  # User can continue with next document
            "ocr_processing": True  # OCR is processing
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error uploading document for page {page_number}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to upload document: {str(e)}"
        )


async def _process_document_with_ocr(doc_id: str, document_type: str, storage_path: str):
    """
    Process uploaded document with OCR for validation
    This runs asynchronously after document upload
    """
    try:
        # Import OCR service
        from app.services.ocr_service import OCRService
        
        # Initialize OCR service
        ocr_service = OCRService()
        
        # Get document record to fetch file data
        doc_ref = db.collection('USER_DOCUMENT').document(doc_id)
        doc_data = doc_ref.get().to_dict()
        
        # Get file data from storage (or use mock data for now)
        file_data = b""  # Placeholder - in production, fetch from Firebase Storage
        file_name = doc_data.get('file_name', 'document.pdf')
        
        # Process document with OCR
        ocr_result = ocr_service.process_document_from_file(
            document_type=document_type,
            file_data=file_data,
            file_name=file_name
        )
        
        # Convert OCR result to dictionary
        ocr_results = {
            'success': ocr_result.confidence_score > 0,
            'confidence': ocr_result.confidence_score,
            'analysis': ocr_result.validation_results,
            'validation_status': 'VALID' if len(ocr_result.issues) == 0 else 'INVALID',
            'errors': ocr_result.issues
        }
        
        # Update document with OCR results
        doc_ref = db.collection('USER_DOCUMENT').document(doc_id)
        
        if ocr_results.get('success', False):
            # OCR successful
            doc_ref.update({
                "ocr_status": "COMPLETED",
                "ocr_results": ocr_results.get('analysis', {}),
                "validation_status": ocr_results.get('validation_status', 'PENDING'),
                "ocr_confidence": ocr_results.get('confidence', 0),
                "updated_at": datetime.utcnow()
            })
            
            # Update task status based on OCR results
            task_id = doc_ref.get().to_dict().get('task_id')
            if task_id:
                task_ref = db.collection('TASK').document(task_id)
                task_ref.update({
                    "ocr_status": "COMPLETED",
                    "ocr_results": ocr_results.get('analysis', {}),
                    "validation_status": ocr_results.get('validation_status', 'PENDING'),
                    "updated_at": datetime.utcnow()
                })
            
            logger.info(f"OCR processing completed for document {doc_id}")
            
        else:
            # OCR failed
            doc_ref.update({
                "ocr_status": "FAILED",
                "ocr_errors": ocr_results.get('errors', ['OCR processing failed']),
                "validation_status": "FAILED",
                "updated_at": datetime.utcnow()
            })
            
            logger.error(f"OCR processing failed for document {doc_id}: {ocr_results.get('errors', [])}")
            
    except Exception as e:
        logger.error(f"Error processing document {doc_id} with OCR: {str(e)}")
        
        # Update document with error status
        try:
            doc_ref = db.collection('USER_DOCUMENT').document(doc_id)
            doc_ref.update({
                "ocr_status": "ERROR",
                "ocr_errors": [f"OCR processing error: {str(e)}"],
                "validation_status": "ERROR",
                "updated_at": datetime.utcnow()
            })
        except Exception as update_error:
            logger.error(f"Failed to update document {doc_id} with OCR error: {str(update_error)}")


@router.get("/applications/{app_id}/document-status/{doc_id}", response_model=dict)
async def get_document_status(
    app_id: str,
    doc_id: str,
    current_user: UserInDB = Depends(get_current_user)
):
    """
    Get the status of a specific document including OCR results
    This helps track document processing and validation
    """
    try:
        # Verify the application belongs to the current user
        app_doc = db.collection('APPLICATION').document(app_id).get()
        if not app_doc.exists:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Application not found"
            )
        
        app_data = app_doc.to_dict()
        if app_data['user_id'] != current_user.uid:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied: Application does not belong to current user"
            )
        
        # Get document details
        doc_ref = db.collection('USER_DOCUMENT').document(doc_id)
        doc_doc = doc_ref.get()
        
        if not doc_doc.exists:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Document not found"
            )
        
        doc_data = doc_doc.to_dict()
        
        # Verify document belongs to this application
        if doc_data.get('application_id') != app_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Document does not belong to this application"
            )
        
        return {
            "document_id": doc_id,
            "application_id": app_id,
            "page_number": doc_data.get('page_number'),
            "document_type": doc_data.get('doc_type'),
            "file_name": doc_data.get('file_name'),
            "upload_status": doc_data.get('status'),
            "ocr_status": doc_data.get('ocr_status', 'PENDING'),
            "validation_status": doc_data.get('validation_status', 'PENDING'),
            "ocr_results": doc_data.get('ocr_results'),
            "ocr_errors": doc_data.get('ocr_errors'),
            "ocr_confidence": doc_data.get('ocr_confidence'),
            "uploaded_at": doc_data.get('uploaded_at'),
            "updated_at": doc_data.get('updated_at'),
            "can_proceed": doc_data.get('ocr_status') in ['COMPLETED', 'FAILED', 'ERROR'],
            "is_valid": doc_data.get('validation_status') == 'VALID',
            "needs_reupload": doc_data.get('validation_status') in ['INVALID', 'FAILED', 'ERROR']
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting document status: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get document status: {str(e)}"
        )




async def _update_application_progress(app_id: str, user_id: str):
    """Update application progress based on completed tasks"""
    try:
        # Get all tasks for this application
        tasks_query = db.collection('TASK').where(
            'application_id', '==', app_id
        ).where('user_id', '==', user_id).stream()
        
        tasks = []
        for task_doc in tasks_query:
            task_data = task_doc.to_dict()
            tasks.append(task_data)
        
        # Calculate progress
        total_tasks = len(tasks)
        completed_tasks = len([t for t in tasks if t['status'] == TaskStatus.DONE.value])
        in_progress_tasks = len([t for t in tasks if t['status'] == TaskStatus.IN_PROGRESS.value])
        pending_tasks = len([t for t in tasks if t['status'] == TaskStatus.PENDING.value])
        
        completion_percentage = int((completed_tasks / total_tasks) * 100) if total_tasks > 0 else 0
        
        # Update application
        app_ref = db.collection('APPLICATION').document(app_id)
        app_ref.update({
            "application_progress": {
                "total_tasks": total_tasks,
                "completed_tasks": completed_tasks,
                "in_progress_tasks": in_progress_tasks,
                "pending_tasks": pending_tasks,
                "completion_percentage": completion_percentage
            },
            "completed_documents": completed_tasks,
            "updated_at": datetime.utcnow()
        })
        
    except Exception as e:
        logger.error(f"Error updating application progress: {str(e)}")


async def _get_application_progress(app_id: str, user_id: str) -> Dict[str, Any]:
    """Get current application progress"""
    try:
        app_doc = db.collection('APPLICATION').document(app_id).get()
        if app_doc.exists:
            app_data = app_doc.to_dict()
            return app_data.get('application_progress', {})
        return {}
    except Exception as e:
        logger.error(f"Error getting application progress: {str(e)}")
        return {}


@router.get("/applications/{app_id}/current-page", response_model=dict)
async def get_current_page_info(
    app_id: str,
    current_user: UserInDB = Depends(get_current_user)
):
    """
    Get information about the current page/task for the user to upload
    This helps the frontend show the right document requirements
    """
    try:
        # Verify the application belongs to the current user
        app_doc = db.collection('APPLICATION').document(app_id).get()
        if not app_doc.exists:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Application not found"
            )
        
        app_data = app_doc.to_dict()
        if app_data['user_id'] != current_user.uid:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied: Application does not belong to current user"
            )
        
        # Get all tasks for this application, ordered by page number
        tasks_query = db.collection('TASK').where(
            'application_id', '==', app_id
        ).where('user_id', '==', current_user.uid).order_by('page_number').stream()
        
        tasks = []
        for task_doc in tasks_query:
            task_data = task_doc.to_dict()
            tasks.append(task_data)
        
        if not tasks:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No tasks found for this application"
            )
        
        # Find the current page (first pending task)
        current_task = None
        current_page = 0
        
        for task in tasks:
            if task['status'] == TaskStatus.PENDING.value:
                current_task = task
                current_page = task['page_number']
                break
        
        # If all tasks are completed or in progress, find the next one
        if not current_task:
            # Find the first task that's not completed
            for task in tasks:
                if task['status'] != TaskStatus.DONE.value:
                    current_task = task
                    current_page = task['page_number']
                    break
        
        if not current_task:
            # All tasks completed
            return {
                "application_id": app_id,
                "current_page": None,
                "total_pages": len(tasks),
                "is_completed": True,
                "completion_percentage": 100,
                "message": "All documents have been uploaded successfully!",
                "next_action": "submit_application"
            }
        
        # Get application progress
        progress = app_data.get('application_progress', {})
        
        return {
            "application_id": app_id,
            "current_page": current_page,
            "total_pages": len(tasks),
            "is_completed": False,
            "completion_percentage": progress.get('completion_percentage', 0),
            "current_task": {
                "task_id": current_task['task_id'],
                "title": current_task['title'],
                "description": current_task['description'],
                "document_type": current_task['document_type'],
                "is_mandatory": current_task.get('is_mandatory', True),
                "acceptance_criteria": current_task.get('acceptance_criteria', []),
                "status": current_task['status']
            },
            "progress": {
                "completed_tasks": progress.get('completed_tasks', 0),
                "pending_tasks": progress.get('pending_tasks', 0),
                "in_progress_tasks": progress.get('in_progress_tasks', 0),
                "total_tasks": progress.get('total_tasks', len(tasks))
            },
            "next_action": "upload_document"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting current page info: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get current page info: {str(e)}"
        )


@router.post("/applications", response_model=ApplicationResponse, status_code=status.HTTP_201_CREATED)
async def create_application(
    application_data: ApplicationCreate,
    current_user: UserInDB = Depends(get_current_user)
):
    """
    Create a new visa application
    This is the core logic that creates the application and generates tasks
    """
    try:
        # Step 1: Create Application
        app_id = str(uuid.uuid4())
        now = datetime.utcnow()
        
        application_doc = {
            "app_id": app_id,
            "user_id": current_user.uid,
            "requirement_id": application_data.requirement_id,
            "status": ApplicationStatus.DRAFT.value,
            "ai_filled_form_data": application_data.ai_filled_form_data,
            "created_at": now,
            "updated_at": now
        }
        
        # Step 2: Fetch Visa Requirement and Checklist Templates
        requirement_doc = db.collection('VISA_REQUIREMENT').document(
            application_data.requirement_id
        ).get()
        
        if not requirement_doc.exists:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Visa requirement '{application_data.requirement_id}' not found"
            )
        
        # Step 3: Fetch Checklist Templates
        checklist_templates = db.collection('VISA_REQUIREMENT').document(
            application_data.requirement_id
        ).collection('CHECKLIST_TEMPLATE').stream()
        
        templates = []
        for template in checklist_templates:
            template_data = template.to_dict()
            template_data['template_id'] = template.id
            templates.append(template_data)
        
        if not templates:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No checklist templates found for requirement '{application_data.requirement_id}'"
            )
        
        # Step 4: Generate Tasks based on user profile type
        tasks_to_create = []
        for template in templates:
            required_for = template.get('required_for', [])
            
            # Check if this template applies to the current user
            if (current_user.profile_type.value in required_for or 
                'ALL' in required_for or 
                not required_for):
                
                task_id = str(uuid.uuid4())
                task_doc = {
                    "task_id": task_id,
                    "application_id": app_id,
                    "user_id": current_user.uid,
                    "template_id": template['template_id'],
                    "title": template['title'],
                    "description": template['description'],
                    "status": TaskStatus.PENDING.value,
                    "notes": None,
                    "created_at": now,
                    "updated_at": now
                }
                tasks_to_create.append(task_doc)
        
        # Step 5: Use Firestore Batch to create application and all tasks atomically
        batch = db.batch()
        
        # Add application to batch
        batch.set(
            db.collection('APPLICATION').document(app_id),
            application_doc
        )
        
        # Add all tasks to batch
        for task_doc in tasks_to_create:
            batch.set(
                db.collection('TASK').document(task_doc['task_id']),
                task_doc
            )
        
        # Commit the batch
        batch.commit()
        
        return ApplicationResponse(
            app_id=app_id,
            user_id=current_user.uid,
            requirement_id=application_data.requirement_id,
            status=ApplicationStatus.DRAFT,
            ai_filled_form_data=application_data.ai_filled_form_data,
            created_at=now,
            updated_at=now
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create application: {str(e)}"
        )


@router.get("/applications/{app_id}/documents", response_model=dict)
async def get_application_documents(
    app_id: str,
    current_user: UserInDB = Depends(get_current_user)
):
    """
    Get all documents associated with an application
    Includes both general documents and task-specific documents
    """
    try:
        # Verify the application belongs to the current user
        app_doc = db.collection('APPLICATION').document(app_id).get()
        if not app_doc.exists:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Application not found"
            )
        
        app_data = app_doc.to_dict()
        if app_data['user_id'] != current_user.uid:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied: Application does not belong to current user"
            )
        
        # Get all tasks for this application
        tasks_query = db.collection('TASK').where(
            'application_id', '==', app_id
        ).where('user_id', '==', current_user.uid).stream()
        
        task_ids = []
        tasks_info = {}
        
        for task_doc in tasks_query:
            task_data = task_doc.to_dict()
            task_id = task_data['task_id']
            task_ids.append(task_id)
            tasks_info[task_id] = {
                'title': task_data['title'],
                'description': task_data['description'],
                'status': task_data['status'],
                'template_id': task_data['template_id']
            }
        
        # Get task-specific documents (USER_DOCUMENT collection)
        task_documents = []
        if task_ids:
            for task_id in task_ids:
                docs_query = db.collection('USER_DOCUMENT').where(
                    'task_id', '==', task_id
                ).where('user_id', '==', current_user.uid).stream()
                
                for doc in docs_query:
                    doc_data = doc.to_dict()
                    doc_data['task_info'] = tasks_info.get(task_id, {})
                    doc_data['document_source'] = 'task_specific'
                    task_documents.append(doc_data)
        
        # Get general documents uploaded by the user (user_documents collection)
        general_docs_query = db.collection('user_documents').where(
            'user_id', '==', current_user.uid
        ).stream()
        
        general_documents = []
        for doc in general_docs_query:
            doc_data = doc.to_dict()
            doc_data['document_source'] = 'general'
            doc_data['task_info'] = None
            general_documents.append(doc_data)
        
        # Calculate document statistics
        total_documents = len(task_documents) + len(general_documents)
        task_doc_count = len(task_documents)
        general_doc_count = len(general_documents)
        
        # Group documents by type
        documents_by_type = {}
        for doc in task_documents + general_documents:
            doc_type = doc.get('doc_type', 'unknown')
            if doc_type not in documents_by_type:
                documents_by_type[doc_type] = []
            documents_by_type[doc_type].append(doc)
        
        return {
            'application_id': app_id,
            'total_documents': total_documents,
            'task_specific_documents': task_doc_count,
            'general_documents': general_doc_count,
            'documents_by_type': documents_by_type,
            'task_documents': task_documents,
            'general_documents': general_documents,
            'tasks_count': len(task_ids),
            'completed_tasks': len([t for t in tasks_info.values() if t['status'] == 'DONE']),
            'pending_tasks': len([t for t in tasks_info.values() if t['status'] == 'PENDING'])
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch application documents: {str(e)}"
        )


@router.get("/applications/{app_id}/documents-summary", response_model=dict)
async def get_application_documents_summary(
    app_id: str,
    current_user: UserInDB = Depends(get_current_user)
):
    """
    Get a summary of all documents associated with an application
    Returns counts and basic info without full document details
    """
    try:
        # Verify the application belongs to the current user
        app_doc = db.collection('APPLICATION').document(app_id).get()
        if not app_doc.exists:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Application not found"
            )
        
        app_data = app_doc.to_dict()
        if app_data['user_id'] != current_user.uid:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied: Application does not belong to current user"
            )
        
        # Get all tasks for this application
        tasks_query = db.collection('TASK').where(
            'application_id', '==', app_id
        ).where('user_id', '==', current_user.uid).stream()
        
        task_ids = []
        tasks_info = {}
        
        for task_doc in tasks_query:
            task_data = task_doc.to_dict()
            task_id = task_data['task_id']
            task_ids.append(task_id)
            tasks_info[task_id] = {
                'title': task_data['title'],
                'status': task_data['status'],
                'template_id': task_data['template_id']
            }
        
        # Count task-specific documents
        task_doc_count = 0
        task_docs_by_type = {}
        
        if task_ids:
            for task_id in task_ids:
                docs_query = db.collection('USER_DOCUMENT').where(
                    'task_id', '==', task_id
                ).where('user_id', '==', current_user.uid).stream()
                
                for doc in docs_query:
                    doc_data = doc.to_dict()
                    task_doc_count += 1
                    doc_type = doc_data.get('doc_type', 'unknown')
                    task_docs_by_type[doc_type] = task_docs_by_type.get(doc_type, 0) + 1
        
        # Count general documents
        general_docs_query = db.collection('user_documents').where(
            'user_id', '==', current_user.uid
        ).stream()
        
        general_doc_count = 0
        general_docs_by_type = {}
        
        for doc in general_docs_query:
            doc_data = doc.to_dict()
            general_doc_count += 1
            doc_type = doc_data.get('doc_type', 'unknown')
            general_docs_by_type[doc_type] = general_docs_by_type.get(doc_type, 0) + 1
        
        # Calculate task statistics
        completed_tasks = len([t for t in tasks_info.values() if t['status'] == 'DONE'])
        pending_tasks = len([t for t in tasks_info.values() if t['status'] == 'PENDING'])
        in_progress_tasks = len([t for t in tasks_info.values() if t['status'] == 'IN_PROGRESS'])
        
        return {
            'application_id': app_id,
            'summary': {
                'total_documents': task_doc_count + general_doc_count,
                'task_specific_documents': task_doc_count,
                'general_documents': general_doc_count,
                'total_tasks': len(task_ids),
                'completed_tasks': completed_tasks,
                'pending_tasks': pending_tasks,
                'in_progress_tasks': in_progress_tasks,
                'completion_percentage': int((completed_tasks / len(task_ids)) * 100) if task_ids else 0
            },
            'documents_by_type': {
                'task_specific': task_docs_by_type,
                'general': general_docs_by_type
            },
            'tasks_summary': [
                {
                    'task_id': task_id,
                    'title': info['title'],
                    'status': info['status'],
                    'template_id': info['template_id']
                }
                for task_id, info in tasks_info.items()
            ]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch application documents summary: {str(e)}"
        )


@router.get("/applications/{app_id}/tasks", response_model=list[TaskResponse])
async def get_application_tasks(
    app_id: str,
    current_user: UserInDB = Depends(get_current_user)
):
    """
    Get all tasks for a specific application
    """
    try:
        # Verify the application belongs to the current user
        app_doc = db.collection('APPLICATION').document(app_id).get()
        if not app_doc.exists:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Application not found"
            )
        
        app_data = app_doc.to_dict()
        if app_data['user_id'] != current_user.uid:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied: Application does not belong to current user"
            )
        
        # Fetch all tasks for this application
        tasks_query = db.collection('TASK').where(
            'application_id', '==', app_id
        ).where('user_id', '==', current_user.uid).stream()
        
        tasks = []
        for task_doc in tasks_query:
            task_data = task_doc.to_dict()
            tasks.append(TaskResponse(
                task_id=task_data['task_id'],
                application_id=task_data['application_id'],
                user_id=task_data['user_id'],
                template_id=task_data['template_id'],
                title=task_data['title'],
                description=task_data['description'],
                status=task_data['status'],
                notes=task_data.get('notes'),
                created_at=task_data['created_at'],
                updated_at=task_data['updated_at']
            ))
        
        return tasks
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch tasks: {str(e)}"
        )


@router.get("/applications", response_model=list[ApplicationResponse])
async def get_user_applications(current_user: UserInDB = Depends(get_current_user)):
    """
    Get all applications for the current user
    """
    try:
        applications_query = db.collection('APPLICATION').where(
            'user_id', '==', current_user.uid
        ).stream()
        
        applications = []
        for app_doc in applications_query:
            app_data = app_doc.to_dict()
            applications.append(ApplicationResponse(
                app_id=app_data['app_id'],
                user_id=app_data['user_id'],
                requirement_id=app_data['requirement_id'],
                status=app_data['status'],
                ai_filled_form_data=app_data['ai_filled_form_data'],
                created_at=app_data['created_at'],
                updated_at=app_data['updated_at']
            ))
        
        # Sort by created_at in Python (descending)
        applications.sort(key=lambda x: x.created_at, reverse=True)
        
        return applications
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch applications: {str(e)}"
        )


@router.put("/applications/{app_id}", response_model=ApplicationResponse)
async def update_application(
    app_id: str,
    application_update: ApplicationUpdate,
    current_user: UserInDB = Depends(get_current_user)
):
    """
    Update an existing visa application
    """
    try:
        # Verify application exists and belongs to current user
        app_ref = db.collection('APPLICATION').document(app_id)
        app_doc = app_ref.get()
        
        if not app_doc.exists:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Application not found"
            )
        
        app_data = app_doc.to_dict()
        if app_data['user_id'] != current_user.uid:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied: Application does not belong to current user"
            )
        
        # Prepare update data
        update_data = {"updated_at": datetime.utcnow()}
        if application_update.status is not None:
            update_data["status"] = application_update.status.value
        if application_update.ai_filled_form_data is not None:
            update_data["ai_filled_form_data"] = application_update.ai_filled_form_data
        
        # Update application
        app_ref.update(update_data)
        
        # Fetch updated data
        updated_doc = app_ref.get()
        updated_data = updated_doc.to_dict()
        
        return ApplicationResponse(
            app_id=updated_data['app_id'],
            user_id=updated_data['user_id'],
            requirement_id=updated_data['requirement_id'],
            status=updated_data['status'],
            ai_filled_form_data=updated_data['ai_filled_form_data'],
            created_at=updated_data['created_at'],
            updated_at=updated_data['updated_at']
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update application: {str(e)}"
        )


@router.post("/applications/{app_id}/submit", response_model=ApplicationResponse)
async def submit_application(
    app_id: str,
    submit_data: ApplicationSubmit,
    current_user: UserInDB = Depends(get_current_user)
):
    """
    Submit a visa application for review
    """
    try:
        # Verify application exists and belongs to current user
        app_ref = db.collection('APPLICATION').document(app_id)
        app_doc = app_ref.get()
        
        if not app_doc.exists:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Application not found"
            )
        
        app_data = app_doc.to_dict()
        if app_data['user_id'] != current_user.uid:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied: Application does not belong to current user"
            )
        
        # Check if application is in DRAFT status
        if app_data['status'] != ApplicationStatus.DRAFT.value:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Application must be in DRAFT status to submit. Current status: {app_data['status']}"
            )
        
        # Check if all required tasks are completed
        tasks_query = db.collection('TASK').where(
            'application_id', '==', app_id
        ).where('user_id', '==', current_user.uid).stream()
        
        incomplete_tasks = []
        for task_doc in tasks_query:
            task_data = task_doc.to_dict()
            if task_data['status'] != TaskStatus.DONE.value:
                incomplete_tasks.append(task_data['title'])
        
        if incomplete_tasks:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot submit application. Incomplete tasks: {', '.join(incomplete_tasks)}"
            )
        
        # Update application status to SUBMITTED
        update_data = {
            "status": ApplicationStatus.SUBMITTED.value,
            "updated_at": datetime.utcnow(),
            "submitted_at": datetime.utcnow(),
            "submit_notes": submit_data.submit_notes
        }
        
        app_ref.update(update_data)
        
        # Fetch updated data
        updated_doc = app_ref.get()
        updated_data = updated_doc.to_dict()
        
        return ApplicationResponse(
            app_id=updated_data['app_id'],
            user_id=updated_data['user_id'],
            requirement_id=updated_data['requirement_id'],
            status=updated_data['status'],
            ai_filled_form_data=updated_data['ai_filled_form_data'],
            created_at=updated_data['created_at'],
            updated_at=updated_data['updated_at']
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to submit application: {str(e)}"
        )


@router.put("/applications/{app_id}/progress", response_model=ApplicationResponse)
async def update_application_progress(
    app_id: str,
    progress_update: ApplicationProgressUpdate,
    current_user: UserInDB = Depends(get_current_user)
):
    """
    Update application progress (completed items, selected templates)
    """
    try:
        # Verify application exists and belongs to current user
        app_ref = db.collection('APPLICATION').document(app_id)
        app_doc = app_ref.get()
        
        if not app_doc.exists:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Application not found"
            )
        
        app_data = app_doc.to_dict()
        if app_data['user_id'] != current_user.uid:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied: Application does not belong to current user"
            )
        
        # Prepare update data
        update_data = {"updated_at": datetime.utcnow()}
        
        if progress_update.completed_items is not None:
            update_data["completed_items"] = progress_update.completed_items
            
            # Calculate progress percentage
            total_items = app_data.get("total_items", 1)
            progress_percentage = int((progress_update.completed_items / total_items) * 100)
            update_data["progress_percentage"] = progress_percentage
        
        if progress_update.selected_templates is not None:
            update_data["selected_templates"] = progress_update.selected_templates
        
        # Update application
        app_ref.update(update_data)
        
        # Fetch updated data
        updated_doc = app_ref.get()
        updated_data = updated_doc.to_dict()
        
        return ApplicationResponse(
            app_id=updated_data['app_id'],
            user_id=updated_data['user_id'],
            team_id=updated_data.get('team_id'),
            requirement_id=updated_data['requirement_id'],
            status=updated_data['status'],
            generated_letter_url=updated_data.get('generated_letter_url'),
            generated_letter_file_name=updated_data.get('generated_letter_file_name'),
            generated_letter_file_size=updated_data.get('generated_letter_file_size'),
            generated_letter_mime_type=updated_data.get('generated_letter_mime_type'),
            generated_letter_created_at=updated_data.get('generated_letter_created_at'),
            total_items=updated_data.get('total_items', 0),
            completed_items=updated_data.get('completed_items', 0),
            progress_percentage=updated_data.get('progress_percentage', 0),
            selected_templates=updated_data.get('selected_templates', []),
            travel_purpose=updated_data.get('travel_purpose'),
            destination_country=updated_data.get('destination_country'),
            company_info=updated_data.get('company_info'),
            travel_dates=updated_data.get('travel_dates'),
            travel_insurance=updated_data.get('travel_insurance'),
            created_at=updated_data['created_at'],
            updated_at=updated_data['updated_at'],
            submitted_at=updated_data.get('submitted_at'),
            approved_at=updated_data.get('approved_at')
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update application progress: {str(e)}"
        )


@router.post("/applications/{app_id}/generate-letter", response_model=ApplicationResponse)
async def generate_application_letter(
    app_id: str,
    letter_data: ApplicationGenerateLetter,
    current_user: UserInDB = Depends(get_current_user)
):
    """
    Generate a letter for the visa application
    """
    try:
        # Verify application exists and belongs to current user
        app_ref = db.collection('APPLICATION').document(app_id)
        app_doc = app_ref.get()
        
        if not app_doc.exists:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Application not found"
            )
        
        app_data = app_doc.to_dict()
        if app_data['user_id'] != current_user.uid:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied: Application does not belong to current user"
            )
        
        # Get visa requirement for letter template
        requirement_doc = db.collection('VISA_REQUIREMENT').document(
            app_data['requirement_id']
        ).get()
        
        if not requirement_doc.exists:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Visa requirement not found"
            )
        
        requirement_data = requirement_doc.to_dict()
        letter_templates = requirement_data.get('letter_template', [])
        
        if not letter_templates and not letter_data.letter_template:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No letter template available for this visa requirement"
            )
        
        # Use provided template or default template
        template_to_use = letter_data.letter_template or letter_templates[0]
        
        # Generate letter content (simplified - in production, use AI service)
        letter_content = template_to_use
        
        if letter_data.custom_content:
            # Replace placeholders with custom content
            for key, value in letter_data.custom_content.items():
                letter_content = letter_content.replace(f"{{{key}}}", str(value))
        
        # Generate unique filename
        letter_filename = f"visa_letter_{app_id}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.txt"
        
        # In production, save to cloud storage and get URL
        letter_url = f"https://storage.example.com/letters/{letter_filename}"
        
        # Update application with letter information
        update_data = {
            "generated_letter_url": letter_url,
            "generated_letter_file_name": letter_filename,
            "generated_letter_file_size": len(letter_content.encode('utf-8')),
            "generated_letter_mime_type": "text/plain",
            "generated_letter_created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        app_ref.update(update_data)
        
        # Fetch updated data
        updated_doc = app_ref.get()
        updated_data = updated_doc.to_dict()
        
        return ApplicationResponse(
            app_id=updated_data['app_id'],
            user_id=updated_data['user_id'],
            team_id=updated_data.get('team_id'),
            requirement_id=updated_data['requirement_id'],
            status=updated_data['status'],
            generated_letter_url=updated_data.get('generated_letter_url'),
            generated_letter_file_name=updated_data.get('generated_letter_file_name'),
            generated_letter_file_size=updated_data.get('generated_letter_file_size'),
            generated_letter_mime_type=updated_data.get('generated_letter_mime_type'),
            generated_letter_created_at=updated_data.get('generated_letter_created_at'),
            total_items=updated_data.get('total_items', 0),
            completed_items=updated_data.get('completed_items', 0),
            progress_percentage=updated_data.get('progress_percentage', 0),
            selected_templates=updated_data.get('selected_templates', []),
            travel_purpose=updated_data.get('travel_purpose'),
            destination_country=updated_data.get('destination_country'),
            company_info=updated_data.get('company_info'),
            travel_dates=updated_data.get('travel_dates'),
            travel_insurance=updated_data.get('travel_insurance'),
            created_at=updated_data['created_at'],
            updated_at=updated_data['updated_at'],
            submitted_at=updated_data.get('submitted_at'),
            approved_at=updated_data.get('approved_at')
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate application letter: {str(e)}"
        )


@router.get("/applications/{app_id}/progress", response_model=dict)
async def get_application_progress(
    app_id: str,
    current_user: UserInDB = Depends(get_current_user)
):
    """
    Get detailed progress information for an application
    """
    try:
        # Verify application exists and belongs to current user
        app_doc = db.collection('APPLICATION').document(app_id).get()
        
        if not app_doc.exists:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Application not found"
            )
        
        app_data = app_doc.to_dict()
        if app_data['user_id'] != current_user.uid:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied: Application does not belong to current user"
            )
        
        # Get all tasks for this application
        tasks_query = db.collection('TASK').where(
            'application_id', '==', app_id
        ).where('user_id', '==', current_user.uid).stream()
        
        tasks = []
        for task_doc in tasks_query:
            task_data = task_doc.to_dict()
            tasks.append(task_data)
        
        # Calculate progress statistics
        total_tasks = len(tasks)
        completed_tasks = len([t for t in tasks if t['status'] == TaskStatus.DONE.value])
        pending_tasks = len([t for t in tasks if t['status'] == TaskStatus.PENDING.value])
        in_progress_tasks = len([t for t in tasks if t['status'] == TaskStatus.IN_PROGRESS.value])
        
        progress_percentage = int((completed_tasks / total_tasks) * 100) if total_tasks > 0 else 0
        
        # Get task details by status
        tasks_by_status = {
            "pending": [t for t in tasks if t['status'] == TaskStatus.PENDING.value],
            "in_progress": [t for t in tasks if t['status'] == TaskStatus.IN_PROGRESS.value],
            "completed": [t for t in tasks if t['status'] == TaskStatus.DONE.value],
            "rejected": [t for t in tasks if t['status'] == TaskStatus.REJECTED.value]
        }
        
        return {
            "application_id": app_id,
            "status": app_data['status'],
            "total_tasks": total_tasks,
            "completed_tasks": completed_tasks,
            "pending_tasks": pending_tasks,
            "in_progress_tasks": in_progress_tasks,
            "progress_percentage": progress_percentage,
            "tasks_by_status": tasks_by_status,
            "created_at": app_data['created_at'],
            "updated_at": app_data['updated_at'],
            "submitted_at": app_data.get('submitted_at'),
            "approved_at": app_data.get('approved_at')
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get application progress: {str(e)}"
        )
