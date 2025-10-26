"""
AI Form Filling API Endpoints
Handles automatic form filling for Schengen visa applications using AI
Uses Groq's Llama 4 Scout model via SchengenFormFillingService
"""

from typing import Dict, Any, Optional
from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field, EmailStr
from app.services.security import get_current_user, UserInDB
from app.services.schengen_form_filling_service import SchengenFormFillingService
import logging
import os

logger = logging.getLogger(__name__)
router = APIRouter()

# Initialize AI form filling service
ai_form_service = SchengenFormFillingService()


# Request/Response Models
class TravelDates(BaseModel):
    """Travel dates model"""
    arrival: str = Field(..., description="Arrival date in DD-MM-YYYY format")
    departure: str = Field(..., description="Departure date in DD-MM-YYYY format")


class UserDataForAI(BaseModel):
    """User data for AI form filling"""
    surname: str = Field(..., description="Last name / Family name")
    name: str = Field(..., description="First name(s)")
    email: EmailStr = Field(..., description="Email address")
    phone: Optional[str] = Field(None, description="Phone number with country code")
    date_of_birth: str = Field(..., description="Date of birth in DD-MM-YYYY format")
    place_of_birth: str = Field(..., description="Place of birth")
    nationality: str = Field(..., description="Nationality")
    passport_number: str = Field(..., description="Passport number")
    passport_issue_date: str = Field(..., description="Passport issue date in DD-MM-YYYY format")
    passport_expiry_date: str = Field(..., description="Passport expiry date in DD-MM-YYYY format")
    tc_kimlik_no: Optional[str] = Field(None, description="Turkish national ID number (optional)")
    profile_type: Optional[str] = Field(None, description="Profile type: STUDENT, WORKER, TOURIST, etc.")


class ApplicationDataForAI(BaseModel):
    """Application data for AI form filling"""
    destination_country: str = Field(..., description="Destination country")
    purpose: str = Field(..., description="Purpose of travel: Tourism, Business, Study, etc.")
    travel_dates: TravelDates = Field(..., description="Travel dates")
    duration: Optional[str] = Field(None, description="Duration of stay")
    entry_type: Optional[str] = Field(None, description="Entry type: Single Entry, Multiple Entry")


class AIFormFillingRequest(BaseModel):
    """Request model for AI form filling"""
    user_data: UserDataForAI = Field(..., description="User profile data")
    application_data: ApplicationDataForAI = Field(..., description="Visa application data")
    document_filename: Optional[str] = Field(None, description="Custom filename for generated document")


class AIFormFillingResponse(BaseModel):
    """Response model for AI form filling"""
    success: bool
    filled_fields: Dict[str, Any] = Field(default_factory=dict)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    document_path: Optional[str] = Field(None, description="Path to generated Word document")
    error: Optional[str] = Field(None, description="Error message if success is false")


class ValidateFormRequest(BaseModel):
    """Request model for form validation"""
    filled_fields: Dict[str, Any] = Field(..., description="Filled form fields to validate")


class ValidateFormResponse(BaseModel):
    """Response model for form validation"""
    valid: bool
    errors: list = Field(default_factory=list)
    warnings: list = Field(default_factory=list)
    fields_checked: int


class ServiceStatusResponse(BaseModel):
    """Response model for service status"""
    available: bool
    service: str
    model: str = Field(None)
    status: str
    error: str = Field(None)


@router.post(
    "/form-filling/ai/fill-schengen-form",
    response_model=AIFormFillingResponse,
    status_code=status.HTTP_200_OK,
    summary="Fill Schengen Form with AI",
    description="Automatically fills a Schengen visa application form using AI and user/application data"
)
async def fill_schengen_form_with_ai(
    request: AIFormFillingRequest,
    current_user: UserInDB = Depends(get_current_user)
):
    """
    Fill Schengen visa application form using AI
    
    This endpoint uses Groq's Llama 4 Scout model to intelligently fill out
    the Harmonised Schengen Visa Application Form based on provided user and
    application data. The AI prepares the data and fills the Word document template.
    
    **Features:**
    - Fills up to 61 form fields automatically
    - Validates data formats (dates, phone numbers, etc.)
    - Returns both text fields and boolean checkboxes
    - Provides metadata about the filling process
    - Automatically generates Word document with filled data
    
    **Returns:**
    - Filled form fields with values
    - Metadata including fields filled count and model used
    - Success/error status
    - Path to generated Word document
    """
    try:
        logger.info(f"AI form filling requested by user: {current_user.uid}")
        
        # Convert request models to dictionaries
        user_data = request.user_data.dict()
        application_data = request.application_data.dict()
        
        # Step 1: AI prepares and fills the form data
        logger.info("Step 1: AI analyzing and preparing form data...")
        result = ai_form_service.fill_schengen_form(
            user_data=user_data,
            application_data=application_data
        )
        
        if not result["success"]:
            logger.error(f"Form filling failed: {result.get('error')}")
            return AIFormFillingResponse(
                success=False,
                error=result.get("error", "Unknown error occurred"),
                filled_fields={}
            )
        
        logger.info(f"Step 1 Complete: AI filled {result['metadata']['fields_filled']} fields")
        
        # Step 2: Generate Word document with AI-prepared data
        document_path = None
        try:
            logger.info("Step 2: Generating Word document from AI-prepared data...")
            document_path = ai_form_service.generate_word_document(
                filled_fields=result["filled_fields"],
                output_filename=request.document_filename
            )
            logger.info(f"Step 2 Complete: Word document generated at {document_path}")
        except Exception as doc_error:
            logger.error(f"Failed to generate Word document: {doc_error}")
            # Don't fail the entire request if document generation fails
            result["metadata"]["document_error"] = str(doc_error)
        
        return AIFormFillingResponse(
            success=True,
            filled_fields=result["filled_fields"],
            metadata=result["metadata"],
            document_path=document_path
        )
        
    except Exception as e:
        logger.error(f"Error in AI form filling endpoint: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fill form: {str(e)}"
        )


@router.get(
    "/form-filling/ai/form-fields",
    response_model=Dict[str, str],
    summary="Get Form Field Descriptions",
    description="Returns descriptions of all 61 Schengen form fields"
)
async def get_form_field_descriptions(
    current_user: UserInDB = Depends(get_current_user)
):
    """
    Get descriptions of all Schengen form fields
    
    Returns a dictionary mapping field IDs (field1, field2, etc.) to their
    human-readable descriptions. Useful for understanding what each field
    represents in the Schengen visa application form.
    
    **Returns:**
    - Dictionary of field IDs and descriptions
    - 61 total fields covering all aspects of the application
    """
    try:
        fields = ai_form_service.get_form_field_descriptions()
        return fields
    except Exception as e:
        logger.error(f"Error getting form fields: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get form fields: {str(e)}"
        )


@router.post(
    "/form-filling/ai/validate-form",
    response_model=ValidateFormResponse,
    summary="Validate Filled Form",
    description="Validates a filled Schengen form and returns errors and warnings"
)
async def validate_filled_form(
    request: ValidateFormRequest,
    current_user: UserInDB = Depends(get_current_user)
):
    """
    Validate filled Schengen form
    
    Checks that all required fields are present, validates date formats,
    and provides warnings about common issues (e.g., passport validity).
    
    **Validation includes:**
    - Required field presence check
    - Date format validation (DD-MM-YYYY)
    - Passport expiry date warnings
    - Data consistency checks
    
    **Returns:**
    - Validation status (valid/invalid)
    - List of errors (if any)
    - List of warnings
    - Number of fields checked
    """
    try:
        logger.info(f"Form validation requested by user: {current_user.uid}")
        
        validation_result = ai_form_service.validate_filled_form(
            filled_fields=request.filled_fields
        )
        
        return ValidateFormResponse(
            valid=validation_result["valid"],
            errors=validation_result["errors"],
            warnings=validation_result["warnings"],
            fields_checked=validation_result["fields_checked"]
        )
        
    except Exception as e:
        logger.error(f"Error validating form: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to validate form: {str(e)}"
        )


@router.get(
    "/form-filling/ai/service-status",
    response_model=ServiceStatusResponse,
    summary="Check Service Availability",
    description="Checks if the AI form filling service is available"
)
async def check_service_status(
    current_user: UserInDB = Depends(get_current_user)
):
    """
    Check AI form filling service status
    
    Verifies that the Groq API key is configured and the service is
    operational. Useful for health checks and troubleshooting.
    
    **Returns:**
    - Service availability status
    - Model name being used
    - Current operational status
    - Error message if unavailable
    """
    try:
        is_available = ai_form_service.is_available()
        
        if is_available:
            return ServiceStatusResponse(
                available=True,
                service="Schengen Form Filling Service",
                model="meta-llama/llama-4-scout-17b-16e-instruct",
                status="operational"
            )
        else:
            return ServiceStatusResponse(
                available=False,
                service="Schengen Form Filling Service",
                status="unavailable",
                error="GROQ_API_KEY not configured"
            )
            
    except Exception as e:
        logger.error(f"Error checking service status: {e}")
        return ServiceStatusResponse(
            available=False,
            service="Schengen Form Filling Service",
            status="error",
            error=str(e)
        )


@router.post(
    "/form-filling/ai/generate-document",
    summary="Generate Word Document from Filled Fields",
    description="Generates a Word document from previously filled form fields"
)
async def generate_word_document(
    request: ValidateFormRequest,
    current_user: UserInDB = Depends(get_current_user)
):
    """
    Generate Word document from filled form fields
    
    Takes filled form fields and generates a formatted Word document
    (.docx) with all the information organized by sections.
    
    **Features:**
    - Professional formatting with sections
    - Clear field labels and values
    - Boolean fields displayed as checkmarks
    - Important notes and disclaimers included
    
    **Returns:**
    - Path to generated Word document
    - Filename for download
    """
    try:
        logger.info(f"Word document generation requested by user: {current_user.uid}")
        
        document_path = ai_form_service.generate_word_document(
            filled_fields=request.filled_fields
        )
        
        return {
            "success": True,
            "document_path": document_path,
            "filename": os.path.basename(document_path),
            "message": "Word document generated successfully"
        }
        
    except Exception as e:
        logger.error(f"Error generating Word document: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate Word document: {str(e)}"
        )


@router.get(
    "/form-filling/ai/download-document/{filename}",
    summary="Download Generated Word Document",
    description="Downloads a previously generated Word document"
)
async def download_word_document(
    filename: str,
    current_user: UserInDB = Depends(get_current_user)
):
    """
    Download generated Word document
    
    Downloads a Word document that was previously generated.
    The file is returned as an attachment that browsers will
    prompt to download.
    
    **Returns:**
    - Word document file (.docx)
    - Proper content-type headers
    - Content-disposition for download
    """
    try:
        # Security: Prevent path traversal
        filename = os.path.basename(filename)
        
        file_path = os.path.join("generated_documents", filename)
        
        if not os.path.exists(file_path):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Document not found"
            )
        
        logger.info(f"Downloading document: {filename}")
        
        return FileResponse(
            path=file_path,
            filename=filename,
            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            headers={
                "Content-Disposition": f"attachment; filename={filename}"
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error downloading document: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to download document: {str(e)}"
        )
