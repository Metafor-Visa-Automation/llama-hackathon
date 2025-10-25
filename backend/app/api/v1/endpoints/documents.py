"""
Word Document API Endpoints
"""

from fastapi import APIRouter, HTTPException, Depends, File, UploadFile
from fastapi.responses import FileResponse
from typing import Dict, Any, Optional
import os
import logging
from pydantic import BaseModel, Field

from app.services.word_document_service import WordDocumentService
from app.services.security import get_current_user

logger = logging.getLogger(__name__)

router = APIRouter()

# Initialize the service
word_service = WordDocumentService()


class FormDataRequest(BaseModel):
    """Request model for form data"""
    field_data: Dict[str, str] = Field(..., description="Form field data with FIELD1-FIELD34 keys")
    filename: Optional[str] = Field(None, description="Optional custom filename for the output")


class FormDataResponse(BaseModel):
    """Response model for form data processing"""
    success: bool
    message: str
    filename: str
    download_url: str


@router.post("/edit-word-document", response_model=FormDataResponse)
async def edit_word_document(
    request: FormDataRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Edit the Schengen visa application Word document with user data
    
    Args:
        request: Form data request containing field data and optional filename
        current_user: Current authenticated user
        
    Returns:
        Response with download URL for the generated document
    """
    try:
        # Validate user data
        validated_data = word_service.validate_user_data(request.field_data)
        
        # Generate the document
        output_path = word_service.edit_document(
            user_data=validated_data,
            filename=request.filename
        )
        
        # Extract filename from path
        filename = os.path.basename(output_path)
        
        # Generate download URL
        download_url = f"/api/v1/documents/download/{filename}"
        
        return FormDataResponse(
            success=True,
            message="Word document generated successfully",
            filename=filename,
            download_url=download_url
        )
        
    except FileNotFoundError as e:
        logger.error(f"Template file not found: {e}")
        raise HTTPException(status_code=404, detail="Template file not found")
        
    except Exception as e:
        logger.error(f"Error generating Word document: {e}")
        raise HTTPException(status_code=500, detail=f"Error generating document: {str(e)}")


@router.get("/sample-data")
async def get_sample_data(current_user: dict = Depends(get_current_user)):
    """
    Get sample form data for testing
    
    Returns:
        Sample data structure for all 34 fields
    """
    try:
        sample_data = word_service.get_sample_data()
        
        return {
            "success": True,
            "message": "Sample data retrieved successfully",
            "data": sample_data,
            "field_descriptions": {
                "FIELD1": "Surname (Family name)",
                "FIELD2": "Surname at birth (Former family name(s))",
                "FIELD3": "First name(s) (Given name(s))",
                "FIELD4": "Date of birth (day-month-year)",
                "FIELD5": "Place of birth",
                "FIELD6": "Country of birth",
                "FIELD7": "Current nationality",
                "FIELD8": "Parental authority (in case of minors) / legal guardian",
                "FIELD9": "National identity number, where applicable",
                "FIELD10": "Surname (family name) of family member",
                "FIELD11": "First name of family member",
                "FIELD12": "Date of birth of family member",
                "FIELD13": "Nationality of family member",
                "FIELD14": "Number of travel document or ID card of family member",
                "FIELD15": "Applicant's home address and e-mail address",
                "FIELD16": "Telephone number",
                "FIELD17": "Current occupation",
                "FIELD18": "Employer and employer's address and telephone number",
                "FIELD19": "Purpose of the journey",
                "FIELD20": "Member State of main destination",
                "FIELD21": "Address and e-mail address of inviting person(s)/hotel(s)",
                "FIELD22": "Telephone number of accommodation",
                "FIELD23": "Name and address of inviting company/organisation",
                "FIELD24": "Member State of main destination",
                "FIELD25": "Member State of first entry",
                "FIELD26": "Number of travel document",
                "FIELD27": "Date of issue",
                "FIELD28": "Valid until",
                "FIELD29": "Issued by (country)",
                "FIELD30": "Surname and first name of the inviting person(s)",
                "FIELD31": "Contact person in company/organisation details",
                "FIELD32": "Telephone number of company/organisation",
                "FIELD33": "Cost of travelling and living",
                "FIELD34": "Place and date"
            }
        }
        
    except Exception as e:
        logger.error(f"Error retrieving sample data: {e}")
        raise HTTPException(status_code=500, detail=f"Error retrieving sample data: {str(e)}")


@router.get("/download/{filename}")
async def download_document(filename: str, current_user: dict = Depends(get_current_user)):
    """
    Download a generated document
    
    Args:
        filename: Name of the file to download
        current_user: Current authenticated user
        
    Returns:
        File response for download
    """
    try:
        # Security check - ensure filename doesn't contain path traversal
        if ".." in filename or "/" in filename or "\\" in filename:
            raise HTTPException(status_code=400, detail="Invalid filename")
        
        file_path = os.path.join(word_service.output_dir, filename)
        
        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail="File not found")
        
        return FileResponse(
            path=file_path,
            filename=filename,
            media_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error downloading document: {e}")
        raise HTTPException(status_code=500, detail=f"Error downloading document: {str(e)}")


@router.get("/list-documents")
async def list_documents(current_user: dict = Depends(get_current_user)):
    """
    List all generated documents for the current user
    
    Returns:
        List of available documents
    """
    try:
        documents = []
        
        if os.path.exists(word_service.output_dir):
            for filename in os.listdir(word_service.output_dir):
                if filename.endswith('.docx'):
                    file_path = os.path.join(word_service.output_dir, filename)
                    file_size = os.path.getsize(file_path)
                    file_mtime = os.path.getmtime(file_path)
                    
                    documents.append({
                        "filename": filename,
                        "size": file_size,
                        "created_at": file_mtime,
                        "download_url": f"/api/v1/documents/download/{filename}"
                    })
        
        return {
            "success": True,
            "message": "Documents listed successfully",
            "documents": documents
        }
        
    except Exception as e:
        logger.error(f"Error listing documents: {e}")
        raise HTTPException(status_code=500, detail=f"Error listing documents: {str(e)}")


@router.delete("/delete/{filename}")
async def delete_document(filename: str, current_user: dict = Depends(get_current_user)):
    """
    Delete a generated document
    
    Args:
        filename: Name of the file to delete
        current_user: Current authenticated user
        
    Returns:
        Success message
    """
    try:
        # Security check - ensure filename doesn't contain path traversal
        if ".." in filename or "/" in filename or "\\" in filename:
            raise HTTPException(status_code=400, detail="Invalid filename")
        
        file_path = os.path.join(word_service.output_dir, filename)
        
        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail="File not found")
        
        os.remove(file_path)
        
        return {
            "success": True,
            "message": f"Document {filename} deleted successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting document: {e}")
        raise HTTPException(status_code=500, detail=f"Error deleting document: {str(e)}")