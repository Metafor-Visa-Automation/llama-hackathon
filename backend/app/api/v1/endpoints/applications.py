from fastapi import APIRouter, HTTPException, status, Depends
from app.core.firebase import db
from app.models.schemas import ApplicationCreate, ApplicationUpdate, ApplicationResponse
from app.services.security import get_current_user, UserInDB
from datetime import datetime
from typing import List
import uuid

router = APIRouter()


@router.post("/applications", response_model=ApplicationResponse, status_code=status.HTTP_201_CREATED)
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
            "travel_purpose": application_data.travel_purpose,
            "application_start_date": application_data.application_start_date,
            "application_end_date": application_data.application_end_date,
            "status": "DRAFT",
            "application_steps": application_data.application_steps,
            "created_at": now,
            "updated_at": now
        }
        
        db.collection('applications').document(app_id).set(application_doc)
        
        return ApplicationResponse(
            app_id=app_id,
            user_id=current_user.uid,
            application_name=application_data.application_name,
            country_code=application_data.country_code,
            travel_purpose=application_data.travel_purpose,
            application_start_date=application_data.application_start_date,
            application_end_date=application_data.application_end_date,
            status="DRAFT",
            application_steps=application_data.application_steps,
            created_at=now,
            updated_at=now
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create application: {str(e)}"
        )


@router.get("/applications", response_model=List[ApplicationResponse])
async def get_user_applications(current_user: UserInDB = Depends(get_current_user)):
    """
    Get all applications for the current user
    """
    try:
        applications_query = db.collection('applications').where(
            'user_id', '==', current_user.uid
        ).stream()
        
        applications = []
        for app_doc in applications_query:
            app_data = app_doc.to_dict()
            applications.append(ApplicationResponse(
                app_id=app_data['app_id'],
                user_id=app_data['user_id'],
                application_name=app_data['application_name'],
                country_code=app_data['country_code'],
                travel_purpose=app_data.get('travel_purpose', ''),
                application_start_date=app_data.get('application_start_date'),
                application_end_date=app_data.get('application_end_date'),
                status=app_data['status'],
                application_steps=app_data.get('application_steps', []),
                created_at=app_data['created_at'],
                updated_at=app_data['updated_at']
            ))
        
        return applications
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch applications: {str(e)}"
        )


@router.get("/applications/{app_id}", response_model=ApplicationResponse)
async def get_application(
    app_id: str,
    current_user: UserInDB = Depends(get_current_user)
):
    """
    Get a specific application
    """
    try:
        app_doc = db.collection('applications').document(app_id).get()
        
        if not app_doc.exists:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Application not found"
            )
        
        app_data = app_doc.to_dict()
        
        # Verify ownership
        if app_data['user_id'] != current_user.uid:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
        
        return ApplicationResponse(
            app_id=app_data['app_id'],
            user_id=app_data['user_id'],
            application_name=app_data['application_name'],
            country_code=app_data['country_code'],
            travel_purpose=app_data.get('travel_purpose', ''),
            application_start_date=app_data.get('application_start_date'),
            application_end_date=app_data.get('application_end_date'),
            status=app_data['status'],
            application_steps=app_data.get('application_steps', []),
            created_at=app_data['created_at'],
            updated_at=app_data['updated_at']
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get application: {str(e)}"
        )


@router.put("/applications/{app_id}", response_model=ApplicationResponse)
async def update_application(
    app_id: str,
    application_update: ApplicationUpdate,
    current_user: UserInDB = Depends(get_current_user)
):
    """
    Update an application
    """
    try:
        app_doc = db.collection('applications').document(app_id).get()
        
        if not app_doc.exists:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Application not found"
            )
        
        app_data = app_doc.to_dict()
        
        # Verify ownership
        if app_data['user_id'] != current_user.uid:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
        
        # Prepare update data
        update_data = {"updated_at": datetime.utcnow()}
        
        if application_update.application_name is not None:
            update_data["application_name"] = application_update.application_name
        if application_update.country_code is not None:
            update_data["country_code"] = application_update.country_code
        if application_update.travel_purpose is not None:
            update_data["travel_purpose"] = application_update.travel_purpose
        if application_update.application_start_date is not None:
            update_data["application_start_date"] = application_update.application_start_date
        if application_update.application_end_date is not None:
            update_data["application_end_date"] = application_update.application_end_date
        if application_update.status is not None:
            update_data["status"] = application_update.status
        if application_update.application_steps is not None:
            update_data["application_steps"] = application_update.application_steps
        
        # Update application
        db.collection('applications').document(app_id).update(update_data)
        
        # Fetch updated data
        updated_doc = db.collection('applications').document(app_id).get()
        updated_data = updated_doc.to_dict()
        
        return ApplicationResponse(
            app_id=updated_data['app_id'],
            user_id=updated_data['user_id'],
            application_name=updated_data['application_name'],
            country_code=updated_data['country_code'],
            travel_purpose=updated_data.get('travel_purpose', ''),
            application_start_date=updated_data.get('application_start_date'),
            application_end_date=updated_data.get('application_end_date'),
            status=updated_data['status'],
            application_steps=updated_data.get('application_steps', []),
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


@router.delete("/applications/{app_id}")
async def delete_application(
    app_id: str,
    current_user: UserInDB = Depends(get_current_user)
):
    """
    Delete an application
    """
    try:
        app_doc = db.collection('applications').document(app_id).get()
        
        if not app_doc.exists:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Application not found"
            )
        
        app_data = app_doc.to_dict()
        
        # Verify ownership
        if app_data['user_id'] != current_user.uid:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
        
        # Delete application
        db.collection('applications').document(app_id).delete()
        
        return {"message": "Application deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete application: {str(e)}"
        )
