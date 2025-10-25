"""
Notification Management API Endpoints
Handles user notifications and system messages
"""

from fastapi import APIRouter, HTTPException, status, Depends, Query
from app.core.firebase import db
from app.models.schemas import (
    NotificationCreate, NotificationResponse, NotificationMarkRead, NotificationInDB
)
from app.services.security import get_current_user, UserInDB
from typing import List, Optional
from datetime import datetime
import uuid
import logging

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/notifications", response_model=List[NotificationResponse])
async def get_user_notifications(
    current_user: UserInDB = Depends(get_current_user),
    unread_only: Optional[bool] = Query(None, description="Filter only unread notifications"),
    notification_type: Optional[str] = Query(None, description="Filter by notification type"),
    limit: int = Query(50, ge=1, le=100, description="Number of results to return"),
    offset: int = Query(0, ge=0, description="Number of results to skip")
):
    """
    Get user's notifications with optional filtering
    """
    try:
        # Build query
        query = db.collection("notifications").where("user_id", "==", current_user.uid)
        
        # Apply filters
        if unread_only:
            query = query.where("is_read", "==", False)
        
        if notification_type:
            query = query.where("type", "==", notification_type)
        
        # Order by creation date (newest first)
        query = query.order_by("created_at", direction="DESCENDING")
        
        # Apply pagination
        query = query.offset(offset).limit(limit)
        
        # Execute query
        docs = query.stream()
        
        notifications = []
        for doc in docs:
            notification_data = doc.to_dict()
            notifications.append(NotificationResponse(**notification_data))
        
        return notifications
        
    except Exception as e:
        logger.error(f"Error getting user notifications: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get notifications"
        )


@router.get("/notifications/{notification_id}", response_model=NotificationResponse)
async def get_notification(
    notification_id: str,
    current_user: UserInDB = Depends(get_current_user)
):
    """
    Get a specific notification by ID
    """
    try:
        # Get notification document
        notification_doc = db.collection("notifications").document(notification_id).get()
        
        if not notification_doc.exists:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Notification not found"
            )
        
        notification_data = notification_doc.to_dict()
        
        # Check if notification belongs to current user
        if notification_data.get("user_id") != current_user.uid:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to access this notification"
            )
        
        return NotificationResponse(**notification_data)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting notification: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get notification"
        )


@router.post("/notifications", response_model=NotificationResponse, status_code=status.HTTP_201_CREATED)
async def create_notification(
    notification_data: NotificationCreate,
    current_user: UserInDB = Depends(get_current_user)
):
    """
    Create a new notification (admin/system use)
    """
    try:
        notification_id = str(uuid.uuid4())
        now = datetime.utcnow()
        
        # Determine target user ID
        target_user_id = notification_data.user_id or current_user.uid
        
        notification_doc = {
            "notification_id": notification_id,
            "user_id": target_user_id,
            "title": notification_data.title,
            "message": notification_data.message,
            "type": notification_data.type.value,
            "is_read": False,
            "created_at": now,
            "read_at": None
        }
        
        # Save to Firestore
        db.collection("notifications").document(notification_id).set(notification_doc)
        
        return NotificationResponse(**notification_doc)
        
    except Exception as e:
        logger.error(f"Error creating notification: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create notification"
        )


@router.put("/notifications/{notification_id}/read", response_model=NotificationResponse)
async def mark_notification_read(
    notification_id: str,
    current_user: UserInDB = Depends(get_current_user)
):
    """
    Mark a specific notification as read
    """
    try:
        # Check if notification exists
        notification_ref = db.collection("notifications").document(notification_id)
        notification_doc = notification_ref.get()
        
        if not notification_doc.exists:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Notification not found"
            )
        
        notification_data = notification_doc.to_dict()
        
        # Check if notification belongs to current user
        if notification_data.get("user_id") != current_user.uid:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to modify this notification"
            )
        
        # Check if already read
        if notification_data.get("is_read", False):
            return NotificationResponse(**notification_data)
        
        # Mark as read
        now = datetime.utcnow()
        notification_ref.update({
            "is_read": True,
            "read_at": now
        })
        
        # Get updated notification data
        updated_doc = notification_ref.get()
        updated_data = updated_doc.to_dict()
        
        return NotificationResponse(**updated_data)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error marking notification as read: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to mark notification as read"
        )


@router.put("/notifications/mark-read", response_model=dict)
async def mark_multiple_notifications_read(
    mark_data: NotificationMarkRead,
    current_user: UserInDB = Depends(get_current_user)
):
    """
    Mark multiple notifications as read
    """
    try:
        now = datetime.utcnow()
        updated_count = 0
        
        # Use batch update for efficiency
        batch = db.batch()
        
        for notification_id in mark_data.notification_ids:
            notification_ref = db.collection("notifications").document(notification_id)
            notification_doc = notification_ref.get()
            
            if notification_doc.exists:
                notification_data = notification_doc.to_dict()
                
                # Check if notification belongs to current user
                if notification_data.get("user_id") == current_user.uid:
                    # Only update if not already read
                    if not notification_data.get("is_read", False):
                        batch.update(notification_ref, {
                            "is_read": True,
                            "read_at": now
                        })
                        updated_count += 1
        
        # Commit batch update
        batch.commit()
        
        return {
            "message": f"Successfully marked {updated_count} notifications as read",
            "updated_count": updated_count
        }
        
    except Exception as e:
        logger.error(f"Error marking multiple notifications as read: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to mark notifications as read"
        )


@router.put("/notifications/mark-all-read", response_model=dict)
async def mark_all_notifications_read(
    current_user: UserInDB = Depends(get_current_user)
):
    """
    Mark all user notifications as read
    """
    try:
        now = datetime.utcnow()
        
        # Get all unread notifications for the user
        unread_notifications = db.collection("notifications").where(
            "user_id", "==", current_user.uid
        ).where("is_read", "==", False).stream()
        
        # Use batch update for efficiency
        batch = db.batch()
        updated_count = 0
        
        for notification_doc in unread_notifications:
            notification_ref = db.collection("notifications").document(notification_doc.id)
            batch.update(notification_ref, {
                "is_read": True,
                "read_at": now
            })
            updated_count += 1
        
        # Commit batch update
        batch.commit()
        
        return {
            "message": f"Successfully marked {updated_count} notifications as read",
            "updated_count": updated_count
        }
        
    except Exception as e:
        logger.error(f"Error marking all notifications as read: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to mark all notifications as read"
        )


@router.delete("/notifications/{notification_id}", response_model=dict)
async def delete_notification(
    notification_id: str,
    current_user: UserInDB = Depends(get_current_user)
):
    """
    Delete a specific notification
    """
    try:
        # Check if notification exists
        notification_ref = db.collection("notifications").document(notification_id)
        notification_doc = notification_ref.get()
        
        if not notification_doc.exists:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Notification not found"
            )
        
        notification_data = notification_doc.to_dict()
        
        # Check if notification belongs to current user
        if notification_data.get("user_id") != current_user.uid:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to delete this notification"
            )
        
        # Delete notification
        notification_ref.delete()
        
        return {"message": "Notification deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting notification: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete notification"
        )


@router.get("/notifications/stats", response_model=dict)
async def get_notification_stats(
    current_user: UserInDB = Depends(get_current_user)
):
    """
    Get notification statistics for the user
    """
    try:
        # Get all notifications for the user
        notifications_query = db.collection("notifications").where("user_id", "==", current_user.uid)
        notifications = notifications_query.stream()
        
        stats = {
            "total_notifications": 0,
            "unread_notifications": 0,
            "read_notifications": 0,
            "by_type": {},
            "recent_notifications": 0
        }
        
        now = datetime.utcnow()
        seven_days_ago = datetime(now.year, now.month, now.day - 7)
        
        for notification_doc in notifications:
            notification_data = notification_doc.to_dict()
            stats["total_notifications"] += 1
            
            # Count read/unread
            if notification_data.get("is_read", False):
                stats["read_notifications"] += 1
            else:
                stats["unread_notifications"] += 1
            
            # Count by type
            notification_type = notification_data.get("type", "unknown")
            stats["by_type"][notification_type] = stats["by_type"].get(notification_type, 0) + 1
            
            # Count recent notifications
            created_at = notification_data.get("created_at")
            if created_at and created_at >= seven_days_ago:
                stats["recent_notifications"] += 1
        
        return stats
        
    except Exception as e:
        logger.error(f"Error getting notification stats: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get notification statistics"
        )
