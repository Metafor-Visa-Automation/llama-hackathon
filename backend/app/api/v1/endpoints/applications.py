from fastapi import APIRouter, HTTPException, status, Depends
from app.core.firebase import db
from app.models.schemas import (
    ApplicationCreate, ApplicationResponse, ApplicationStatus,
    ApplicationUpdate, ApplicationStepUpdate
)
from app.services.security import get_current_user, UserInDB
from datetime import datetime
import uuid
from typing import List

router = APIRouter()


@router.post("", response_model=ApplicationResponse, status_code=status.HTTP_201_CREATED)
async def create_application(
    application_data: ApplicationCreate,
    current_user: UserInDB = Depends(get_current_user)
):
    """
    Create a new visa application
    """
    try:
        app_id = str(uuid.uuid4())
        now = datetime.utcnow()
        
        application_doc = {
            "app_id": app_id,
            "user_id": current_user.uid,
            "application_name": application_data.application_name,
            "country_code": application_data.country_code,
            "status": ApplicationStatus.DRAFT.value,
            "application_steps": [],
            "created_at": now,
            "updated_at": now
        }
        
        db.collection('APPLICATION').document(app_id).set(application_doc)
        
        return ApplicationResponse(
            **application_doc
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create application: {str(e)}"
        )


@router.get("", response_model=list[ApplicationResponse])
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
            applications.append(ApplicationResponse(**app_data))
        
        applications.sort(key=lambda x: x.created_at, reverse=True)
        
        return applications
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch applications: {str(e)}"
        )


@router.put("/{app_id}", response_model=ApplicationResponse)
async def update_application(
    app_id: str,
    application_update: ApplicationUpdate,
    current_user: UserInDB = Depends(get_current_user)
):
    """
    Update an existing visa application
    """
    try:
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
        
        update_data = {"updated_at": datetime.utcnow()}
        if application_update.status is not None:
            update_data["status"] = application_update.status.value
        
        app_ref.update(update_data)
        
        updated_doc = app_ref.get()
        updated_data = updated_doc.to_dict()
        
        return ApplicationResponse(**updated_data)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update application: {str(e)}"
        )

@router.put("/{app_id}/steps/{step_id}", response_model=ApplicationResponse)
async def update_application_step(
    app_id: str,
    step_id: str,
    step_update: ApplicationStepUpdate,
    current_user: UserInDB = Depends(get_current_user)
):
    """
    Update a specific step in a visa application
    """
    try:
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

        steps = app_data.get("application_steps", [])
        step_found = False
        for step in steps:
            if step.get("step_id") == step_id:
                if step_update.document_id is not None:
                    step["document_id"] = step_update.document_id
                if step_update.status is not None:
                    step["status"] = step_update.status
                step_found = True
                break
        
        if not step_found:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Step with id {step_id} not found in application"
            )

        app_data["application_steps"] = steps
        app_data["updated_at"] = datetime.utcnow()
        
        app_ref.set(app_data)

        return ApplicationResponse(**app_data)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update application step: {str(e)}"
        )
