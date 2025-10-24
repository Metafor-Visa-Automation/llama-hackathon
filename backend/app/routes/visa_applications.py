from fastapi import APIRouter, HTTPException, Depends, status
from app.models.schemas import (
    VisaApplicationCreate, 
    VisaApplication, 
    VisaApplicationUpdate,
    ApplicationStatus,
    FormFillingRequest,
    FormFillingResponse,
    DocumentChecklistResponse
)
from app.routes.auth import get_current_user
from app.core.firebase import get_firestore_db
from datetime import datetime
import uuid

router = APIRouter()

@router.post("/applications", response_model=VisaApplication)
async def create_visa_application(
    application_data: VisaApplicationCreate,
    current_user: dict = Depends(get_current_user)
):
    """Create a new visa application"""
    try:
        db = get_firestore_db()
        
        application_id = str(uuid.uuid4())
        application_doc = {
            "id": application_id,
            "user_id": current_user["uid"],
            **application_data.dict(),
            "status": ApplicationStatus.DRAFT.value,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "form_data": None,
            "document_checklist": None
        }
        
        db.collection("visa_applications").document(application_id).set(application_doc)
        
        return VisaApplication(**application_doc)
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create visa application: {str(e)}"
        )

@router.get("/applications", response_model=list[VisaApplication])
async def get_user_visa_applications(current_user: dict = Depends(get_current_user)):
    """Get all visa applications for current user"""
    try:
        db = get_firestore_db()
        
        applications = db.collection("visa_applications")\
            .where("user_id", "==", current_user["uid"])\
            .order_by("created_at", direction="DESCENDING")\
            .stream()
        
        application_list = []
        for app in applications:
            app_data = app.to_dict()
            application_list.append(VisaApplication(**app_data))
        
        return application_list
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get visa applications: {str(e)}"
        )

@router.get("/applications/{application_id}", response_model=VisaApplication)
async def get_visa_application(
    application_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get specific visa application by ID"""
    try:
        db = get_firestore_db()
        
        app_doc = db.collection("visa_applications").document(application_id).get()
        
        if not app_doc.exists:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Visa application not found"
            )
        
        app_data = app_doc.to_dict()
        
        # Check if user owns this application
        if app_data["user_id"] != current_user["uid"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
        
        return VisaApplication(**app_data)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get visa application: {str(e)}"
        )

@router.put("/applications/{application_id}", response_model=VisaApplication)
async def update_visa_application(
    application_id: str,
    application_update: VisaApplicationUpdate,
    current_user: dict = Depends(get_current_user)
):
    """Update visa application"""
    try:
        db = get_firestore_db()
        
        # Check if application exists and user owns it
        app_doc = db.collection("visa_applications").document(application_id).get()
        if not app_doc.exists:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Visa application not found"
            )
        
        app_data = app_doc.to_dict()
        if app_data["user_id"] != current_user["uid"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
        
        # Prepare update data
        update_data = application_update.dict(exclude_unset=True)
        update_data["updated_at"] = datetime.utcnow()
        
        # Update application
        db.collection("visa_applications").document(application_id).update(update_data)
        
        # Get updated data
        updated_doc = db.collection("visa_applications").document(application_id).get()
        updated_data = updated_doc.to_dict()
        
        return VisaApplication(**updated_data)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update visa application: {str(e)}"
        )

@router.delete("/applications/{application_id}")
async def delete_visa_application(
    application_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Delete visa application"""
    try:
        db = get_firestore_db()
        
        # Check if application exists and user owns it
        app_doc = db.collection("visa_applications").document(application_id).get()
        if not app_doc.exists:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Visa application not found"
            )
        
        app_data = app_doc.to_dict()
        if app_data["user_id"] != current_user["uid"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
        
        # Delete application
        db.collection("visa_applications").document(application_id).delete()
        
        return {"message": "Visa application deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete visa application: {str(e)}"
        )

@router.post("/applications/{application_id}/submit")
async def submit_visa_application(
    application_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Submit visa application for review"""
    try:
        db = get_firestore_db()
        
        # Check if application exists and user owns it
        app_doc = db.collection("visa_applications").document(application_id).get()
        if not app_doc.exists:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Visa application not found"
            )
        
        app_data = app_doc.to_dict()
        if app_data["user_id"] != current_user["uid"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
        
        # Update status to submitted
        db.collection("visa_applications").document(application_id).update({
            "status": ApplicationStatus.SUBMITTED.value,
            "updated_at": datetime.utcnow()
        })
        
        return {"message": "Visa application submitted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to submit visa application: {str(e)}"
        )

@router.post("/form-filling", response_model=FormFillingResponse)
async def fill_visa_form(
    form_request: FormFillingRequest,
    current_user: dict = Depends(get_current_user)
):
    """AI-powered form filling endpoint"""
    try:
        # This is a placeholder for AI form filling functionality
        # In the actual implementation, this would integrate with Ollama/Llama 3
        
        filled_form = {
            "form_type": form_request.form_type,
            "filled_fields": form_request.user_responses,
            "ai_suggestions": "AI form filling will be implemented here"
        }
        
        return FormFillingResponse(
            filled_form=filled_form,
            confidence_score=0.95,
            warnings=["This is a placeholder response"]
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fill form: {str(e)}"
        )

@router.get("/document-checklist", response_model=DocumentChecklistResponse)
async def get_document_checklist(
    visa_type: str,
    destination_country: str,
    current_user: dict = Depends(get_current_user)
):
    """Get dynamic document checklist based on visa type and destination"""
    try:
        # This is a placeholder for dynamic document checklist generation
        # In the actual implementation, this would query country-specific requirements
        
        requirements = [
            {
                "document_type": "passport",
                "is_required": True,
                "description": "Valid passport with at least 6 months validity",
                "country_specific_notes": f"Required for {destination_country}"
            },
            {
                "document_type": "photo",
                "is_required": True,
                "description": "Recent passport-sized photograph",
                "country_specific_notes": None
            }
        ]
        
        return DocumentChecklistResponse(
            visa_type=visa_type,
            destination_country=destination_country,
            requirements=requirements,
            estimated_processing_time="5-10 business days"
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get document checklist: {str(e)}"
        )
