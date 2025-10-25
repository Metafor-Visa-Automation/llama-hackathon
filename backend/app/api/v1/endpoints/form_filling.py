"""
Form Filling API Endpoints
Handles automatic form filling for Schengen visa applications
"""

from typing import List
from fastapi import APIRouter, HTTPException, status, Depends, UploadFile, File
from fastapi.responses import Response
from app.core.firebase import db
from app.models.schemas import (
    FormFillingRequest, FormFillingResponse, FormPreviewRequest, 
    FormPreviewResponse, UserFormDataSchema
)
from app.services.security import get_current_user, UserInDB
from app.services.form_filling_service import FormFillingService, UserFormData
from datetime import datetime
import uuid
import logging
import base64

logger = logging.getLogger(__name__)
router = APIRouter()

# Initialize form filling service
form_filling_service = FormFillingService()


@router.post("/form-filling/fill-schengen-form", response_model=FormFillingResponse, status_code=status.HTTP_201_CREATED)
async def fill_schengen_form(
    form_request: FormFillingRequest,
    current_user: UserInDB = Depends(get_current_user)
):
    """
    Fill Schengen visa application form with user data
    """
    try:
        # Validate user data using schema
        try:
            user_form_data = UserFormDataSchema(**form_request.user_data)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid user data format: {str(e)}"
            )
        
        # Convert to UserFormData object
        user_data = UserFormData(
            surname=user_form_data.surname,
            surname_at_birth=user_form_data.surname_at_birth,
            first_name=user_form_data.first_name,
            date_of_birth=user_form_data.date_of_birth,
            place_of_birth=user_form_data.place_of_birth,
            country_of_birth=user_form_data.country_of_birth,
            current_nationality=user_form_data.current_nationality,
            sex=user_form_data.sex,
            marital_status=user_form_data.marital_status,
            passport_type=user_form_data.passport_type,
            passport_number=user_form_data.passport_number,
            passport_issue_date=user_form_data.passport_issue_date,
            passport_expiry_date=user_form_data.passport_expiry_date,
            passport_issued_by=user_form_data.passport_issued_by,
            current_address=user_form_data.current_address,
            city=user_form_data.city,
            postal_code=user_form_data.postal_code,
            country=user_form_data.country,
            phone_number=user_form_data.phone_number,
            email=user_form_data.email,
            purpose_of_journey=user_form_data.purpose_of_journey,
            intended_arrival_date=user_form_data.intended_arrival_date,
            intended_departure_date=user_form_data.intended_departure_date,
            member_state_of_first_entry=user_form_data.member_state_of_first_entry,
            number_of_entries_requested=user_form_data.number_of_entries_requested,
            family_members_in_eu=user_form_data.family_members_in_eu,
            eu_residence_permit=user_form_data.eu_residence_permit,
            previous_schengen_visa=user_form_data.previous_schengen_visa,
            fingerprints_taken=user_form_data.fingerprints_taken,
            emergency_contact_name=user_form_data.emergency_contact_name,
            emergency_contact_phone=user_form_data.emergency_contact_phone,
            emergency_contact_email=user_form_data.emergency_contact_email
        )
        
        # Validate user data
        validation_results = form_filling_service.validate_user_data(user_data)
        
        if not validation_results["is_valid"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Data validation failed: {validation_results['issues']}"
            )
        
        # Fill the form
        filled_pdf_bytes = form_filling_service.fill_form(
            user_data=user_data,
            template_pdf_path=form_request.template_pdf_path
        )
        
        # Create form filling record
        filled_form_id = str(uuid.uuid4())
        now = datetime.utcnow()
        
        # Get form preview if requested
        preview = None
        if form_request.include_preview:
            preview = form_filling_service.get_form_preview(user_data)
        
        # Save form filling record to Firestore
        form_record = {
            "filled_form_id": filled_form_id,
            "user_id": current_user.uid,
            "form_type": "Schengen Visa Application",
            "user_data": form_request.user_data,
            "validation_results": validation_results,
            "preview": preview,
            "status": "completed",
            "created_at": now,
            "file_size": len(filled_pdf_bytes)
        }
        
        db.collection('FORM_FILLING_RECORDS').document(filled_form_id).set(form_record)
        
        return FormFillingResponse(
            filled_form_id=filled_form_id,
            user_id=current_user.uid,
            form_type="Schengen Visa Application",
            filled_form_data=filled_pdf_bytes,
            validation_results=validation_results,
            preview=preview,
            created_at=now
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error filling Schengen form: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fill form: {str(e)}"
        )


@router.post("/form-filling/preview-form", response_model=FormPreviewResponse)
async def preview_form_filling(
    preview_request: FormPreviewRequest,
    current_user: UserInDB = Depends(get_current_user)
):
    """
    Get preview of how the form will be filled without actually filling it
    """
    try:
        # Validate user data using schema
        try:
            user_form_data = UserFormDataSchema(**preview_request.user_data)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid user data format: {str(e)}"
            )
        
        # Convert to UserFormData object
        user_data = UserFormData(
            surname=user_form_data.surname,
            surname_at_birth=user_form_data.surname_at_birth,
            first_name=user_form_data.first_name,
            date_of_birth=user_form_data.date_of_birth,
            place_of_birth=user_form_data.place_of_birth,
            country_of_birth=user_form_data.country_of_birth,
            current_nationality=user_form_data.current_nationality,
            sex=user_form_data.sex,
            marital_status=user_form_data.marital_status,
            passport_type=user_form_data.passport_type,
            passport_number=user_form_data.passport_number,
            passport_issue_date=user_form_data.passport_issue_date,
            passport_expiry_date=user_form_data.passport_expiry_date,
            passport_issued_by=user_form_data.passport_issued_by,
            current_address=user_form_data.current_address,
            city=user_form_data.city,
            postal_code=user_form_data.postal_code,
            country=user_form_data.country,
            phone_number=user_form_data.phone_number,
            email=user_form_data.email,
            purpose_of_journey=user_form_data.purpose_of_journey,
            intended_arrival_date=user_form_data.intended_arrival_date,
            intended_departure_date=user_form_data.intended_departure_date,
            member_state_of_first_entry=user_form_data.member_state_of_first_entry,
            number_of_entries_requested=user_form_data.number_of_entries_requested,
            family_members_in_eu=user_form_data.family_members_in_eu,
            eu_residence_permit=user_form_data.eu_residence_permit,
            previous_schengen_visa=user_form_data.previous_schengen_visa,
            fingerprints_taken=user_form_data.fingerprints_taken,
            emergency_contact_name=user_form_data.emergency_contact_name,
            emergency_contact_phone=user_form_data.emergency_contact_phone,
            emergency_contact_email=user_form_data.emergency_contact_email
        )
        
        # Get form preview
        preview = form_filling_service.get_form_preview(user_data)
        
        return FormPreviewResponse(
            form_type=preview["form_type"],
            filled_fields=preview["filled_fields"],
            validation_results=preview["validation"],
            recommendations=preview["validation"].get("recommendations", [])
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting form preview: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get form preview: {str(e)}"
        )


@router.get("/form-filling/download/{filled_form_id}")
async def download_filled_form(
    filled_form_id: str,
    current_user: UserInDB = Depends(get_current_user)
):
    """
    Download a filled form by ID
    """
    try:
        # Get form record from Firestore
        form_doc = db.collection('FORM_FILLING_RECORDS').document(filled_form_id).get()
        if not form_doc.exists:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Form not found"
            )
        
        form_data = form_doc.to_dict()
        if form_data['user_id'] != current_user.uid:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied: Form does not belong to current user"
            )
        
        # Recreate the filled form
        user_data_dict = form_data['user_data']
        user_form_data = UserFormDataSchema(**user_data_dict)
        
        user_data = UserFormData(
            surname=user_form_data.surname,
            surname_at_birth=user_form_data.surname_at_birth,
            first_name=user_form_data.first_name,
            date_of_birth=user_form_data.date_of_birth,
            place_of_birth=user_form_data.place_of_birth,
            country_of_birth=user_form_data.country_of_birth,
            current_nationality=user_form_data.current_nationality,
            sex=user_form_data.sex,
            marital_status=user_form_data.marital_status,
            passport_type=user_form_data.passport_type,
            passport_number=user_form_data.passport_number,
            passport_issue_date=user_form_data.passport_issue_date,
            passport_expiry_date=user_form_data.passport_expiry_date,
            passport_issued_by=user_form_data.passport_issued_by,
            current_address=user_form_data.current_address,
            city=user_form_data.city,
            postal_code=user_form_data.postal_code,
            country=user_form_data.country,
            phone_number=user_form_data.phone_number,
            email=user_form_data.email,
            purpose_of_journey=user_form_data.purpose_of_journey,
            intended_arrival_date=user_form_data.intended_arrival_date,
            intended_departure_date=user_form_data.intended_departure_date,
            member_state_of_first_entry=user_form_data.member_state_of_first_entry,
            number_of_entries_requested=user_form_data.number_of_entries_requested,
            family_members_in_eu=user_form_data.family_members_in_eu,
            eu_residence_permit=user_form_data.eu_residence_permit,
            previous_schengen_visa=user_form_data.previous_schengen_visa,
            fingerprints_taken=user_form_data.fingerprints_taken,
            emergency_contact_name=user_form_data.emergency_contact_name,
            emergency_contact_phone=user_form_data.emergency_contact_phone,
            emergency_contact_email=user_form_data.emergency_contact_email
        )
        
        # Generate filled PDF
        filled_pdf_bytes = form_filling_service.fill_form(user_data)
        
        # Return PDF as download
        return Response(
            content=filled_pdf_bytes,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename=schengen_visa_form_{filled_form_id}.pdf"
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error downloading filled form: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to download form: {str(e)}"
        )


@router.get("/form-filling/history", response_model=List[dict])
async def get_form_filling_history(
    current_user: UserInDB = Depends(get_current_user)
):
    """
    Get user's form filling history
    """
    try:
        # Get form filling records for current user
        forms_query = db.collection('FORM_FILLING_RECORDS').where(
            'user_id', '==', current_user.uid
        ).order_by('created_at', direction='DESCENDING').stream()
        
        forms = []
        for form_doc in forms_query:
            form_data = form_doc.to_dict()
            # Remove sensitive data and large fields
            form_summary = {
                "filled_form_id": form_data["filled_form_id"],
                "form_type": form_data["form_type"],
                "status": form_data["status"],
                "created_at": form_data["created_at"],
                "file_size": form_data.get("file_size", 0),
                "validation_results": form_data.get("validation_results", {})
            }
            forms.append(form_summary)
        
        return forms
        
    except Exception as e:
        logger.error(f"Error getting form filling history: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get form filling history: {str(e)}"
        )


@router.get("/form-filling/templates")
async def get_available_form_templates(
    current_user: UserInDB = Depends(get_current_user)
):
    """
    Get list of available form templates
    """
    try:
        templates = [
            {
                "template_id": "schengen_visa_application",
                "template_name": "Schengen Visa Application Form",
                "description": "Standard Schengen visa application form",
                "file_path": "backend/schengen-visa-application-form.pdf",
                "supported_fields": [
                    "Personal Information",
                    "Passport Information", 
                    "Address Information",
                    "Travel Information",
                    "Additional Information"
                ]
            }
        ]
        
        return templates
        
    except Exception as e:
        logger.error(f"Error getting form templates: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get form templates: {str(e)}"
        )


@router.post("/form-filling/validate-data")
async def validate_form_data(
    user_data: dict,
    current_user: UserInDB = Depends(get_current_user)
):
    """
    Validate user data for form filling without filling the form
    """
    try:
        # Validate user data using schema
        try:
            user_form_data = UserFormDataSchema(**user_data)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid user data format: {str(e)}"
            )
        
        # Convert to UserFormData object
        user_data_obj = UserFormData(
            surname=user_form_data.surname,
            surname_at_birth=user_form_data.surname_at_birth,
            first_name=user_form_data.first_name,
            date_of_birth=user_form_data.date_of_birth,
            place_of_birth=user_form_data.place_of_birth,
            country_of_birth=user_form_data.country_of_birth,
            current_nationality=user_form_data.current_nationality,
            sex=user_form_data.sex,
            marital_status=user_form_data.marital_status,
            passport_type=user_form_data.passport_type,
            passport_number=user_form_data.passport_number,
            passport_issue_date=user_form_data.passport_issue_date,
            passport_expiry_date=user_form_data.passport_expiry_date,
            passport_issued_by=user_form_data.passport_issued_by,
            current_address=user_form_data.current_address,
            city=user_form_data.city,
            postal_code=user_form_data.postal_code,
            country=user_form_data.country,
            phone_number=user_form_data.phone_number,
            email=user_form_data.email,
            purpose_of_journey=user_form_data.purpose_of_journey,
            intended_arrival_date=user_form_data.intended_arrival_date,
            intended_departure_date=user_form_data.intended_departure_date,
            member_state_of_first_entry=user_form_data.member_state_of_first_entry,
            number_of_entries_requested=user_form_data.number_of_entries_requested,
            family_members_in_eu=user_form_data.family_members_in_eu,
            eu_residence_permit=user_form_data.eu_residence_permit,
            previous_schengen_visa=user_form_data.previous_schengen_visa,
            fingerprints_taken=user_form_data.fingerprints_taken,
            emergency_contact_name=user_form_data.emergency_contact_name,
            emergency_contact_phone=user_form_data.emergency_contact_phone,
            emergency_contact_email=user_form_data.emergency_contact_email
        )
        
        # Validate user data
        validation_results = form_filling_service.validate_user_data(user_data_obj)
        
        return {
            "is_valid": validation_results["is_valid"],
            "issues": validation_results["issues"],
            "recommendations": validation_results["recommendations"]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error validating form data: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to validate form data: {str(e)}"
        )
