from fastapi import APIRouter, HTTPException, status, Depends, Query
from app.core.firebase import db
from app.models.schemas import (
    TaskResponse, TaskInDB, TaskUpdate, TaskStatus,
    ApplicationResponse, ApplicationInDB, TaskComplete, TaskDashboard
)
from app.services.security import get_current_user, UserInDB
from typing import List, Optional
from datetime import datetime

router = APIRouter()


@router.get("/", response_model=List[TaskResponse])
async def get_user_tasks(
    current_user: UserInDB = Depends(get_current_user),
    status_filter: Optional[TaskStatus] = Query(None, description="Filter by task status"),
    application_id: Optional[str] = Query(None, description="Filter by application ID"),
    limit: int = Query(50, ge=1, le=100, description="Number of results to return")
):
    """
    Get all tasks for the current user with optional filtering
    """
    try:
        query = db.collection('TASK').where('user_id', '==', current_user.uid)
        
        # Apply filters
        if status_filter:
            query = query.where('status', '==', status_filter.value)
        if application_id:
            query = query.where('application_id', '==', application_id)
        
        # Execute query
        docs = query.limit(limit).order_by('created_at', direction='DESCENDING').stream()
        
        tasks = []
        for doc in docs:
            data = doc.to_dict()
            tasks.append(TaskResponse(
                task_id=data['task_id'],
                application_id=data['application_id'],
                user_id=data['user_id'],
                template_id=data['template_id'],
                title=data['title'],
                description=data['description'],
                status=data['status'],
                notes=data.get('notes'),
                created_at=data['created_at'],
                updated_at=data['updated_at']
            ))
        
        return tasks
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch tasks: {str(e)}"
        )


@router.get("/{task_id}", response_model=TaskResponse)
async def get_task(
    task_id: str,
    current_user: UserInDB = Depends(get_current_user)
):
    """
    Get a specific task by ID
    """
    try:
        doc = db.collection('TASK').document(task_id).get()
        if not doc.exists:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found"
            )
        
        data = doc.to_dict()
        
        # Verify task belongs to current user
        if data['user_id'] != current_user.uid:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied: Task does not belong to current user"
            )
        
        return TaskResponse(
            task_id=data['task_id'],
            application_id=data['application_id'],
            user_id=data['user_id'],
            template_id=data['template_id'],
            title=data['title'],
            description=data['description'],
            status=data['status'],
            notes=data.get('notes'),
            created_at=data['created_at'],
            updated_at=data['updated_at']
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch task: {str(e)}"
        )


@router.put("/{task_id}", response_model=TaskResponse)
async def update_task(
    task_id: str,
    task_update: TaskUpdate,
    current_user: UserInDB = Depends(get_current_user)
):
    """
    Update a specific task
    """
    try:
        # Verify task exists and belongs to current user
        doc_ref = db.collection('TASK').document(task_id)
        doc = doc_ref.get()
        
        if not doc.exists:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found"
            )
        
        data = doc.to_dict()
        if data['user_id'] != current_user.uid:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied: Task does not belong to current user"
            )
        
        # Prepare update data
        update_data = {"updated_at": datetime.utcnow()}
        if task_update.status is not None:
            update_data["status"] = task_update.status.value
        if task_update.notes is not None:
            update_data["notes"] = task_update.notes
        
        # Update task
        doc_ref.update(update_data)
        
        # Fetch updated data
        updated_doc = doc_ref.get()
        updated_data = updated_doc.to_dict()
        
        return TaskResponse(
            task_id=updated_data['task_id'],
            application_id=updated_data['application_id'],
            user_id=updated_data['user_id'],
            template_id=updated_data['template_id'],
            title=updated_data['title'],
            description=updated_data['description'],
            status=updated_data['status'],
            notes=updated_data.get('notes'),
            created_at=updated_data['created_at'],
            updated_at=updated_data['updated_at']
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update task: {str(e)}"
        )


@router.get("/statistics")
async def get_task_statistics(current_user: UserInDB = Depends(get_current_user)):
    """
    Get task statistics for the current user
    """
    try:
        # Get all tasks for the user
        docs = db.collection('TASK').where('user_id', '==', current_user.uid).stream()
        
        stats = {
            "total_tasks": 0,
            "pending": 0,
            "in_progress": 0,
            "done": 0,
            "rejected": 0,
            "by_application": {}
        }
        
        for doc in docs:
            data = doc.to_dict()
            stats["total_tasks"] += 1
            
            # Count by status
            status = data['status']
            if status in stats:
                stats[status] += 1
            
            # Count by application
            app_id = data['application_id']
            if app_id not in stats["by_application"]:
                stats["by_application"][app_id] = {
                    "total": 0,
                    "pending": 0,
                    "in_progress": 0,
                    "done": 0,
                    "rejected": 0
                }
            
            stats["by_application"][app_id]["total"] += 1
            if status in stats["by_application"][app_id]:
                stats["by_application"][app_id][status] += 1
        
        return stats
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch task statistics: {str(e)}"
        )


@router.get("/applications/{app_id}", response_model=ApplicationResponse)
async def get_application(
    app_id: str,
    current_user: UserInDB = Depends(get_current_user)
):
    """
    Get a specific application by ID
    """
    try:
        doc = db.collection('APPLICATION').document(app_id).get()
        if not doc.exists:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Application not found"
            )
        
        data = doc.to_dict()
        
        # Verify application belongs to current user
        if data['user_id'] != current_user.uid:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied: Application does not belong to current user"
            )
        
        return ApplicationResponse(
            app_id=data['app_id'],
            user_id=data['user_id'],
            requirement_id=data['requirement_id'],
            status=data['status'],
            ai_filled_form_data=data['ai_filled_form_data'],
            created_at=data['created_at'],
            updated_at=data['updated_at']
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch application: {str(e)}"
        )


@router.post("/tasks/{task_id}/complete", response_model=TaskResponse)
async def complete_task(
    task_id: str,
    completion_data: TaskComplete,
    current_user: UserInDB = Depends(get_current_user)
):
    """
    Mark a task as completed
    """
    try:
        # Verify task exists and belongs to current user
        task_ref = db.collection('TASK').document(task_id)
        task_doc = task_ref.get()
        
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
        
        # Check if task is already completed
        if task_data['status'] == TaskStatus.DONE.value:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Task is already completed"
            )
        
        # Check if task has required documents uploaded
        docs_query = db.collection('USER_DOCUMENT').where(
            'task_id', '==', task_id
        ).where('user_id', '==', current_user.uid).stream()
        
        has_documents = any(True for _ in docs_query)
        
        if not has_documents:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot complete task without uploading required documents"
            )
        
        # Update task status to DONE
        update_data = {
            "status": TaskStatus.DONE.value,
            "updated_at": datetime.utcnow(),
            "completed_at": datetime.utcnow(),
            "completion_notes": completion_data.completion_notes
        }
        
        task_ref.update(update_data)
        
        # Fetch updated data
        updated_doc = task_ref.get()
        updated_data = updated_doc.to_dict()
        
        return TaskResponse(
            task_id=updated_data['task_id'],
            application_id=updated_data['application_id'],
            user_id=updated_data['user_id'],
            template_id=updated_data['template_id'],
            title=updated_data['title'],
            description=updated_data['description'],
            status=updated_data['status'],
            notes=updated_data.get('notes'),
            created_at=updated_data['created_at'],
            updated_at=updated_data['updated_at']
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to complete task: {str(e)}"
        )


@router.get("/tasks/dashboard", response_model=TaskDashboard)
async def get_task_dashboard(current_user: UserInDB = Depends(get_current_user)):
    """
    Get comprehensive task dashboard
    """
    try:
        # Get all tasks for the user
        tasks_query = db.collection('TASK').where('user_id', '==', current_user.uid).stream()
        
        tasks = []
        for task_doc in tasks_query:
            task_data = task_doc.to_dict()
            tasks.append(task_data)
        
        # Calculate task statistics
        total_tasks = len(tasks)
        pending_tasks = len([t for t in tasks if t['status'] == 'PENDING'])
        in_progress_tasks = len([t for t in tasks if t['status'] == 'IN_PROGRESS'])
        completed_tasks = len([t for t in tasks if t['status'] == 'DONE'])
        rejected_tasks = len([t for t in tasks if t['status'] == 'REJECTED'])
        
        # Group tasks by application
        tasks_by_application = {}
        for task in tasks:
            app_id = task['application_id']
            if app_id not in tasks_by_application:
                tasks_by_application[app_id] = {
                    "total": 0,
                    "pending": 0,
                    "in_progress": 0,
                    "done": 0,
                    "rejected": 0
                }
            
            tasks_by_application[app_id]["total"] += 1
            status = task['status'].lower()
            if status in tasks_by_application[app_id]:
                tasks_by_application[app_id][status] += 1
        
        # Get recent activity (last 10 tasks)
        recent_activity = []
        sorted_tasks = sorted(tasks, key=lambda x: x['updated_at'], reverse=True)[:10]
        
        for task in sorted_tasks:
            recent_activity.append({
                "task_id": task['task_id'],
                "title": task['title'],
                "status": task['status'],
                "application_id": task['application_id'],
                "updated_at": task['updated_at'],
                "action": f"Task {task['status'].lower().replace('_', ' ')}"
            })
        
        # Calculate upcoming deadlines (tasks that are pending or in progress)
        upcoming_deadlines = []
        cutoff_date = datetime.utcnow()
        
        for task in tasks:
            if task['status'] in ['PENDING', 'IN_PROGRESS']:
                # Calculate estimated deadline (7 days from creation)
                deadline_date = task['created_at'].replace(day=task['created_at'].day + 7)
                if deadline_date > cutoff_date:
                    upcoming_deadlines.append({
                        "task_id": task['task_id'],
                        "title": task['title'],
                        "application_id": task['application_id'],
                        "deadline": deadline_date.isoformat(),
                        "days_remaining": (deadline_date - cutoff_date).days,
                        "status": task['status']
                    })
        
        # Sort by days remaining
        upcoming_deadlines.sort(key=lambda x: x['days_remaining'])
        
        return TaskDashboard(
            total_tasks=total_tasks,
            pending_tasks=pending_tasks,
            in_progress_tasks=in_progress_tasks,
            completed_tasks=completed_tasks,
            rejected_tasks=rejected_tasks,
            tasks_by_application=tasks_by_application,
            recent_activity=recent_activity,
            upcoming_deadlines=upcoming_deadlines[:5]  # Limit to 5 upcoming deadlines
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch task dashboard: {str(e)}"
        )
