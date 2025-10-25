from fastapi import APIRouter, HTTPException, status, Depends
from app.core.firebase import db
from app.models.schemas import (
    ApplicationCreate, ApplicationResponse, ApplicationInDB,
    TaskResponse, TaskInDB, ApplicationStatus, TaskStatus
)
from app.services.security import get_current_user, UserInDB
from datetime import datetime
import uuid

router = APIRouter()


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
        ).order_by('created_at', direction='DESCENDING').stream()
        
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
        
        return applications
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch applications: {str(e)}"
        )
