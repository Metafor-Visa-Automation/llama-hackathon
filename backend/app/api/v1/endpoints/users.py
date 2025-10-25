from fastapi import APIRouter, HTTPException, status, Depends
from app.core.firebase import db
from app.models.schemas import UserUpdate, UserResponse, UserInDB, UserDashboard, ApplicationResponse, NotificationResponse
from app.services.security import get_current_user
from datetime import datetime
from typing import List

router = APIRouter()


@router.get("/me", response_model=UserResponse)
async def get_user_profile(current_user: UserInDB = Depends(get_current_user)):
    """
    Get current user's profile
    """
    return UserResponse(
        uid=current_user.uid,
        email=current_user.email,
        name=current_user.name,
        surname=current_user.surname,
        profile_type=current_user.profile_type,
        passport_type=current_user.passport_type,
        phone=current_user.phone,
        date_of_birth=current_user.date_of_birth,
        nationality=current_user.nationality,
        created_at=current_user.created_at,
        updated_at=current_user.updated_at
    )


@router.put("/me", response_model=UserResponse)
async def update_user_profile(
    user_update: UserUpdate,
    current_user: UserInDB = Depends(get_current_user)
):
    """
    Update current user's profile
    """
    try:
        # Prepare update data (only include non-None values)
        update_data = {}
        if user_update.name is not None:
            update_data["name"] = user_update.name
        if user_update.surname is not None:
            update_data["surname"] = user_update.surname
        if user_update.profile_type is not None:
            update_data["profile_type"] = user_update.profile_type.value
        if user_update.passport_type is not None:
            update_data["passport_type"] = user_update.passport_type.value
        if user_update.phone is not None:
            update_data["phone"] = user_update.phone
        if user_update.date_of_birth is not None:
            update_data["date_of_birth"] = user_update.date_of_birth
        if user_update.nationality is not None:
            update_data["nationality"] = user_update.nationality
        
        # Always update the timestamp
        update_data["updated_at"] = datetime.utcnow()
        
        # Update in Firestore
        db.collection('USER').document(current_user.uid).update(update_data)
        
        # Fetch updated user data
        updated_doc = db.collection('USER').document(current_user.uid).get()
        updated_data = updated_doc.to_dict()
        
        return UserResponse(
            uid=updated_data["uid"],
            email=updated_data["email"],
            name=updated_data["name"],
            surname=updated_data["surname"],
            profile_type=updated_data["profile_type"],
            passport_type=updated_data["passport_type"],
            phone=updated_data.get("phone"),
            date_of_birth=updated_data.get("date_of_birth"),
            nationality=updated_data.get("nationality"),
            created_at=updated_data["created_at"],
            updated_at=updated_data["updated_at"]
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update profile: {str(e)}"
        )


@router.get("/me/dashboard", response_model=UserDashboard)
async def get_user_dashboard(current_user: UserInDB = Depends(get_current_user)):
    """
    Get user dashboard with comprehensive overview
    """
    try:
        # Get user data
        user_response = UserResponse(
            uid=current_user.uid,
            email=current_user.email,
            name=current_user.name,
            surname=current_user.surname,
            profile_type=current_user.profile_type,
            passport_type=current_user.passport_type,
            phone=current_user.phone,
            date_of_birth=current_user.date_of_birth,
            nationality=current_user.nationality,
            created_at=current_user.created_at,
            updated_at=current_user.updated_at
        )
        
        # Get application statistics
        applications_query = db.collection('APPLICATION').where(
            'user_id', '==', current_user.uid
        ).stream()
        
        applications = []
        total_applications = 0
        active_applications = 0
        
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
            total_applications += 1
            
            # Count active applications (DRAFT, SUBMITTED, UNDER_REVIEW)
            if app_data['status'] in ['DRAFT', 'SUBMITTED', 'UNDER_REVIEW']:
                active_applications += 1
        
        # Get task statistics
        tasks_query = db.collection('TASK').where(
            'user_id', '==', current_user.uid
        ).stream()
        
        completed_tasks = 0
        pending_tasks = 0
        
        for task_doc in tasks_query:
            task_data = task_doc.to_dict()
            if task_data['status'] == 'DONE':
                completed_tasks += 1
            else:
                pending_tasks += 1
        
        # Get recent applications (last 5)
        recent_applications = sorted(
            applications, 
            key=lambda x: x.created_at, 
            reverse=True
        )[:5]
        
        # Calculate upcoming deadlines (simplified - applications submitted in last 30 days)
        upcoming_deadlines = []
        cutoff_date = datetime.utcnow()
        
        for app in applications:
            if app.status in ['SUBMITTED', 'UNDER_REVIEW']:
                # Calculate estimated deadline (30 days from submission)
                deadline_date = app.created_at.replace(day=app.created_at.day + 30)
                if deadline_date > cutoff_date:
                    upcoming_deadlines.append({
                        "application_id": app.app_id,
                        "requirement_id": app.requirement_id,
                        "deadline": deadline_date.isoformat(),
                        "days_remaining": (deadline_date - cutoff_date).days,
                        "status": app.status
                    })
        
        # Sort by days remaining
        upcoming_deadlines.sort(key=lambda x: x['days_remaining'])
        
        # Calculate progress summary
        progress_summary = {
            "completion_rate": round((completed_tasks / (completed_tasks + pending_tasks)) * 100, 1) if (completed_tasks + pending_tasks) > 0 else 0,
            "applications_submitted": len([app for app in applications if app.status == 'SUBMITTED']),
            "applications_approved": len([app for app in applications if app.status == 'APPROVED']),
            "total_documents_uploaded": completed_tasks  # Assuming each completed task has a document
        }
        
        return UserDashboard(
            user=user_response,
            total_applications=total_applications,
            active_applications=active_applications,
            completed_tasks=completed_tasks,
            pending_tasks=pending_tasks,
            recent_applications=recent_applications,
            upcoming_deadlines=upcoming_deadlines[:5],  # Limit to 5 upcoming deadlines
            progress_summary=progress_summary
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch dashboard: {str(e)}"
        )


@router.get("/me/notifications", response_model=List[NotificationResponse])
async def get_user_notifications(
    current_user: UserInDB = Depends(get_current_user),
    unread_only: bool = False,
    limit: int = 50
):
    """
    Get user notifications
    """
    try:
        query = db.collection('NOTIFICATION').where('user_id', '==', current_user.uid)
        
        if unread_only:
            query = query.where('is_read', '==', False)
        
        docs = query.limit(limit).order_by('created_at', direction='DESCENDING').stream()
        
        notifications = []
        for doc in docs:
            data = doc.to_dict()
            notifications.append(NotificationResponse(
                notification_id=data['notification_id'],
                user_id=data['user_id'],
                title=data['title'],
                message=data['message'],
                type=data['type'],
                is_read=data['is_read'],
                created_at=data['created_at'],
                read_at=data.get('read_at')
            ))
        
        return notifications
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch notifications: {str(e)}"
        )


@router.post("/me/notifications/read")
async def mark_notifications_read(
    notification_ids: List[str],
    current_user: UserInDB = Depends(get_current_user)
):
    """
    Mark notifications as read
    """
    try:
        batch = db.batch()
        now = datetime.utcnow()
        
        for notification_id in notification_ids:
            notification_ref = db.collection('NOTIFICATION').document(notification_id)
            notification_doc = notification_ref.get()
            
            if notification_doc.exists:
                data = notification_doc.to_dict()
                if data['user_id'] == current_user.uid:
                    batch.update(notification_ref, {
                        'is_read': True,
                        'read_at': now,
                        'updated_at': now
                    })
        
        batch.commit()
        
        return {"message": f"Marked {len(notification_ids)} notifications as read"}
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to mark notifications as read: {str(e)}"
        )
