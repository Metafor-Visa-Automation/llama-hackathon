from fastapi import APIRouter, HTTPException, status, Depends, Query
from app.core.firebase import db
from app.services.security import get_current_user, UserInDB
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta

router = APIRouter()


class AdminStatsResponse(BaseModel):
    total_users: int
    total_applications: int
    total_tasks: int
    total_documents: int
    total_social_audits: int
    users_by_profile_type: Dict[str, int]
    applications_by_status: Dict[str, int]
    tasks_by_status: Dict[str, int]
    recent_activity: List[Dict[str, Any]]


class UserManagementResponse(BaseModel):
    uid: str
    email: str
    name: str
    surname: str
    profile_type: str
    passport_type: str
    created_at: datetime
    last_login: Optional[datetime] = None
    total_applications: int = 0
    total_tasks: int = 0


class SystemHealthResponse(BaseModel):
    firestore_status: str
    storage_status: str
    api_status: str
    uptime: str
    last_check: datetime


# Admin role check (simplified - in production, implement proper role-based access)
async def require_admin(current_user: UserInDB = Depends(get_current_user)):
    """
    Check if user has admin privileges
    For now, we'll use a simple check - in production, implement proper role management
    """
    # This is a placeholder - implement proper admin role checking
    # For demo purposes, we'll allow any authenticated user to access admin endpoints
    return current_user


@router.get("/stats", response_model=AdminStatsResponse)
async def get_admin_statistics(admin_user: UserInDB = Depends(require_admin)):
    """
    Get comprehensive system statistics for admin dashboard
    """
    try:
        # Get user statistics
        users_docs = db.collection('USER').stream()
        total_users = 0
        users_by_profile_type = {}
        
        for doc in users_docs:
            total_users += 1
            data = doc.to_dict()
            profile_type = data.get('profile_type', 'UNKNOWN')
            users_by_profile_type[profile_type] = users_by_profile_type.get(profile_type, 0) + 1
        
        # Get application statistics
        apps_docs = db.collection('APPLICATION').stream()
        total_applications = 0
        applications_by_status = {}
        
        for doc in apps_docs:
            total_applications += 1
            data = doc.to_dict()
            status = data.get('status', 'UNKNOWN')
            applications_by_status[status] = applications_by_status.get(status, 0) + 1
        
        # Get task statistics
        tasks_docs = db.collection('TASK').stream()
        total_tasks = 0
        tasks_by_status = {}
        
        for doc in tasks_docs:
            total_tasks += 1
            data = doc.to_dict()
            status = data.get('status', 'UNKNOWN')
            tasks_by_status[status] = tasks_by_status.get(status, 0) + 1
        
        # Get document statistics
        docs_docs = db.collection('USER_DOCUMENT').stream()
        total_documents = sum(1 for _ in docs_docs)
        
        # Get social audit statistics
        audits_docs = db.collection('SOCIAL_MEDIA_AUDIT').stream()
        total_social_audits = sum(1 for _ in audits_docs)
        
        # Get recent activity (last 24 hours)
        recent_activity = []
        cutoff_time = datetime.utcnow() - timedelta(hours=24)
        
        # Recent applications
        recent_apps = db.collection('APPLICATION').where('created_at', '>=', cutoff_time).limit(10).stream()
        for doc in recent_apps:
            data = doc.to_dict()
            recent_activity.append({
                "type": "application_created",
                "user_id": data['user_id'],
                "application_id": data['app_id'],
                "timestamp": data['created_at'],
                "description": f"New application created for requirement {data['requirement_id']}"
            })
        
        return AdminStatsResponse(
            total_users=total_users,
            total_applications=total_applications,
            total_tasks=total_tasks,
            total_documents=total_documents,
            total_social_audits=total_social_audits,
            users_by_profile_type=users_by_profile_type,
            applications_by_status=applications_by_status,
            tasks_by_status=tasks_by_status,
            recent_activity=recent_activity
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch admin statistics: {str(e)}"
        )


@router.get("/users", response_model=List[UserManagementResponse])
async def get_all_users(
    admin_user: UserInDB = Depends(require_admin),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0)
):
    """
    Get all users for admin management
    """
    try:
        # Get users with pagination
        users_query = db.collection('USER').order_by('created_at', direction='DESCENDING').offset(offset).limit(limit)
        users_docs = users_query.stream()
        
        users = []
        for doc in users_docs:
            data = doc.to_dict()
            
            # Get user's application count
            apps_count = len(list(db.collection('APPLICATION').where('user_id', '==', data['uid']).stream()))
            
            # Get user's task count
            tasks_count = len(list(db.collection('TASK').where('user_id', '==', data['uid']).stream()))
            
            users.append(UserManagementResponse(
                uid=data['uid'],
                email=data['email'],
                name=data['name'],
                surname=data['surname'],
                profile_type=data['profile_type'],
                passport_type=data['passport_type'],
                created_at=data['created_at'],
                last_login=data.get('last_login'),
                total_applications=apps_count,
                total_tasks=tasks_count
            ))
        
        return users
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch users: {str(e)}"
        )


@router.get("/users/{user_id}", response_model=UserManagementResponse)
async def get_user_details(
    user_id: str,
    admin_user: UserInDB = Depends(require_admin)
):
    """
    Get detailed information about a specific user
    """
    try:
        doc = db.collection('USER').document(user_id).get()
        if not doc.exists:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        data = doc.to_dict()
        
        # Get user's application count
        apps_count = len(list(db.collection('APPLICATION').where('user_id', '==', user_id).stream()))
        
        # Get user's task count
        tasks_count = len(list(db.collection('TASK').where('user_id', '==', user_id).stream()))
        
        return UserManagementResponse(
            uid=data['uid'],
            email=data['email'],
            name=data['name'],
            surname=data['surname'],
            profile_type=data['profile_type'],
            passport_type=data['passport_type'],
            created_at=data['created_at'],
            last_login=data.get('last_login'),
            total_applications=apps_count,
            total_tasks=tasks_count
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch user details: {str(e)}"
        )


@router.get("/system-health", response_model=SystemHealthResponse)
async def get_system_health(admin_user: UserInDB = Depends(require_admin)):
    """
    Get system health status
    """
    try:
        # Test Firestore connection
        firestore_status = "healthy"
        try:
            db.collection('USER').limit(1).stream()
        except Exception:
            firestore_status = "unhealthy"
        
        # Test Storage connection (simplified)
        storage_status = "healthy"  # We'll assume it's healthy if we got this far
        
        # API status
        api_status = "healthy"
        
        # Calculate uptime (simplified)
        uptime = "N/A"  # In production, track actual uptime
        
        return SystemHealthResponse(
            firestore_status=firestore_status,
            storage_status=storage_status,
            api_status=api_status,
            uptime=uptime,
            last_check=datetime.utcnow()
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to check system health: {str(e)}"
        )


@router.get("/collections")
async def get_collection_info(admin_user: UserInDB = Depends(require_admin)):
    """
    Get information about all Firestore collections
    """
    try:
        collections = [
            'USER', 'APPLICATION', 'TASK', 'USER_DOCUMENT',
            'COUNTRY', 'VISA_REQUIREMENT', 'SOCIAL_MEDIA_AUDIT'
        ]
        
        collection_info = {}
        for collection_name in collections:
            try:
                docs = db.collection(collection_name).limit(1).stream()
                doc_count = len(list(docs))
                collection_info[collection_name] = {
                    "exists": True,
                    "document_count": "N/A",  # Would need to count all docs for accurate count
                    "accessible": True
                }
            except Exception as e:
                collection_info[collection_name] = {
                    "exists": False,
                    "document_count": 0,
                    "accessible": False,
                    "error": str(e)
                }
        
        return {
            "collections": collection_info,
            "total_collections": len(collections),
            "accessible_collections": sum(1 for info in collection_info.values() if info["accessible"])
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch collection info: {str(e)}"
        )
