from typing import List
from fastapi import APIRouter, HTTPException, status, Depends, UploadFile, File
from app.core.firebase import db
from app.models.schemas import (
    OCRDocumentAnalysisRequest, OCRDocumentAnalysisResponse,
    OCRProcessRequest, OCRProcessResponse, DocumentTypeConfig
)
from app.services.security import get_current_user, UserInDB
from app.services.ocr_service import OCRService
from datetime import datetime
import uuid
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

# Initialize OCR service
ocr_service = OCRService()


@router.post("/ocr/upload-and-analyze", response_model=OCRDocumentAnalysisResponse, status_code=status.HTTP_201_CREATED)
async def upload_and_analyze_document(
    task_id: str,
    document_type: str,
    file: UploadFile = File(...),
    current_user: UserInDB = Depends(get_current_user)
):
    """
    Upload document and analyze it using OCR with specific validation rules
    """
    try:
        # Verify task exists and belongs to current user
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
        
        # Validate file
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
        
        # Check file type
        allowed_extensions = {'.pdf', '.jpg', '.jpeg', '.png', '.tiff', '.bmp'}
        file_extension = '.' + file.filename.split('.')[-1].lower() if '.' in file.filename else ''
        if file_extension not in allowed_extensions:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File type not allowed. Allowed types: {', '.join(allowed_extensions)}"
            )
        
        # Process document with OCR service
        ocr_result = ocr_service.process_document_from_file(
            document_type=document_type,
            file_data=file_content,
            file_name=file.filename
        )
        
        # Create analysis record
        analysis_id = str(uuid.uuid4())
        now = datetime.utcnow()
        
        # Convert OCR result to response format
        validation_results = {}
        for key, result in ocr_result.validation_results.items():
            validation_results[key] = {
                "valid": result.get("valid", False),
                "issues": result.get("issues", []),
                "recommendations": result.get("recommendations", []),
                "details": result.get("details", {})
            }
        
        analysis_doc = {
            "analysis_id": analysis_id,
            "task_id": task_id,
            "user_id": current_user.uid,
            "document_type": document_type,
            "confidence_score": ocr_result.confidence_score,
            "validation_results": validation_results,
            "issues": ocr_result.issues,
            "recommendations": ocr_result.recommendations,
            "status": "completed",
            "created_at": now,
            "metadata": ocr_result.metadata
        }
        
        # Save analysis to Firestore
        db.collection('OCR_DOCUMENT_ANALYSIS').document(analysis_id).set(analysis_doc)
        
        return OCRDocumentAnalysisResponse(
            analysis_id=analysis_id,
            task_id=task_id,
            document_type=document_type,
            confidence_score=ocr_result.confidence_score,
            validation_results=validation_results,
            issues=ocr_result.issues,
            recommendations=ocr_result.recommendations,
            status="completed",
            created_at=now,
            metadata=ocr_result.metadata
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in OCR document upload and analysis: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to upload and analyze document: {str(e)}"
        )


@router.post("/ocr/analyze-document", response_model=OCRDocumentAnalysisResponse, status_code=status.HTTP_201_CREATED)
async def analyze_document_with_ocr(
    analysis_request: OCRDocumentAnalysisRequest,
    current_user: UserInDB = Depends(get_current_user)
):
    """
    Analyze uploaded document using OCR with specific validation rules
    """
    try:
        # Verify task exists and belongs to current user
        task_doc = db.collection('TASK').document(analysis_request.task_id).get()
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
        
        # Check if documents are uploaded for this task
        docs_query = db.collection('USER_DOCUMENT').where(
            'task_id', '==', analysis_request.task_id
        ).where('user_id', '==', current_user.uid).stream()
        
        documents = list(docs_query)
        if not documents:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No documents found for this task"
            )
        
        # Process document with OCR service
        ocr_result = ocr_service.process_document(
            document_type=analysis_request.document_type,
            extracted_text=analysis_request.extracted_text,
            file_metadata=analysis_request.file_metadata
        )
        
        # Create analysis record
        analysis_id = str(uuid.uuid4())
        now = datetime.utcnow()
        
        # Convert OCR result to response format
        validation_results = {}
        for key, result in ocr_result.validation_results.items():
            validation_results[key] = {
                "valid": result.get("valid", False),
                "issues": result.get("issues", []),
                "recommendations": result.get("recommendations", []),
                "details": result.get("details", {})
            }
        
        analysis_doc = {
            "analysis_id": analysis_id,
            "task_id": analysis_request.task_id,
            "user_id": current_user.uid,
            "document_type": analysis_request.document_type,
            "confidence_score": ocr_result.confidence_score,
            "validation_results": validation_results,
            "issues": ocr_result.issues,
            "recommendations": ocr_result.recommendations,
            "status": "completed",
            "created_at": now,
            "metadata": ocr_result.metadata
        }
        
        # Save analysis to Firestore
        db.collection('OCR_DOCUMENT_ANALYSIS').document(analysis_id).set(analysis_doc)
        
        return OCRDocumentAnalysisResponse(
            analysis_id=analysis_id,
            task_id=analysis_request.task_id,
            document_type=analysis_request.document_type,
            confidence_score=ocr_result.confidence_score,
            validation_results=validation_results,
            issues=ocr_result.issues,
            recommendations=ocr_result.recommendations,
            status="completed",
            created_at=now,
            metadata=ocr_result.metadata
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in OCR document analysis: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to analyze document with OCR: {str(e)}"
        )


@router.post("/ocr/process", response_model=OCRProcessResponse)
async def process_document_ocr(
    process_request: OCRProcessRequest,
    current_user: UserInDB = Depends(get_current_user)
):
    """
    Process document text with OCR validation rules (without task association)
    """
    try:
        # Process document with OCR service
        ocr_result = ocr_service.process_document(
            document_type=process_request.document_type,
            extracted_text=process_request.extracted_text,
            file_metadata=process_request.file_metadata
        )
        
        # Convert OCR result to response format
        validation_results = {}
        for key, result in ocr_result.validation_results.items():
            validation_results[key] = {
                "valid": result.get("valid", False),
                "issues": result.get("issues", []),
                "recommendations": result.get("recommendations", []),
                "details": result.get("details", {})
            }
        
        return OCRProcessResponse(
            document_type=ocr_result.document_type.value,
            confidence_score=ocr_result.confidence_score,
            extracted_text=ocr_result.extracted_text,
            validation_results=validation_results,
            issues=ocr_result.issues,
            recommendations=ocr_result.recommendations,
            metadata=ocr_result.metadata
        )
        
    except Exception as e:
        logger.error(f"Error in OCR processing: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process document with OCR: {str(e)}"
        )


@router.get("/ocr/document-types", response_model=List[DocumentTypeConfig])
async def get_supported_document_types(
    current_user: UserInDB = Depends(get_current_user)
):
    """
    Get list of supported document types and their validation rules
    """
    try:
        supported_types = ocr_service.list_supported_document_types()
        return supported_types
        
    except Exception as e:
        logger.error(f"Error getting supported document types: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get supported document types: {str(e)}"
        )


@router.get("/ocr/document-types/{document_type}", response_model=DocumentTypeConfig)
async def get_document_type_config(
    document_type: str,
    current_user: UserInDB = Depends(get_current_user)
):
    """
    Get configuration for a specific document type
    """
    try:
        config = ocr_service.get_document_type_config(document_type)
        if not config:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Document type '{document_type}' not supported"
            )
        
        return DocumentTypeConfig(
            checkId=config["checkId"],
            docDescription=config["docDescription"],
            docName=config["docName"],
            ocrValidationRules=config["ocrValidationRules"].__dict__,
            requiredFor=config["requiredFor"]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting document type config: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get document type configuration: {str(e)}"
        )


@router.get("/ocr/analysis/{analysis_id}", response_model=OCRDocumentAnalysisResponse)
async def get_ocr_analysis(
    analysis_id: str,
    current_user: UserInDB = Depends(get_current_user)
):
    """
    Get OCR analysis results by analysis ID
    """
    try:
        analysis_doc = db.collection('OCR_DOCUMENT_ANALYSIS').document(analysis_id).get()
        if not analysis_doc.exists:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Analysis not found"
            )
        
        analysis_data = analysis_doc.to_dict()
        if analysis_data['user_id'] != current_user.uid:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied: Analysis does not belong to current user"
            )
        
        return OCRDocumentAnalysisResponse(**analysis_data)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting OCR analysis: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get OCR analysis: {str(e)}"
        )


@router.get("/ocr/task/{task_id}/analyses", response_model=List[OCRDocumentAnalysisResponse])
async def get_task_ocr_analyses(
    task_id: str,
    current_user: UserInDB = Depends(get_current_user)
):
    """
    Get all OCR analyses for a specific task
    """
    try:
        # Verify task exists and belongs to current user
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
        
        # Get analyses for this task
        analyses_query = db.collection('OCR_DOCUMENT_ANALYSIS').where(
            'task_id', '==', task_id
        ).where('user_id', '==', current_user.uid).stream()
        
        analyses = []
        for analysis_doc in analyses_query:
            analysis_data = analysis_doc.to_dict()
            analyses.append(OCRDocumentAnalysisResponse(**analysis_data))
        
        return analyses
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting task OCR analyses: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get task OCR analyses: {str(e)}"
        )
