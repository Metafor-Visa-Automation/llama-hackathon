from fastapi import APIRouter, HTTPException, status, Depends
from app.core.firebase import db
from app.models.schemas import (
    ApplicationCreate, ApplicationResponse, ApplicationInDB,
    TaskResponse, TaskInDB, ApplicationStatus, TaskStatus,
    ApplicationUpdate, ApplicationSubmit, ApplicationProgressUpdate,
    ApplicationGenerateLetter
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
