from fastapi import APIRouter, HTTPException, status, Depends
from app.core.firebase import db
from app.services.security import get_current_user, UserInDB
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime
import uuid

router = APIRouter()


class SocialMediaAuditCreate(BaseModel):
    platform: str  # LinkedIn, Facebook, Instagram, Twitter, etc.
    profile_url: str
    audit_type: str  # "visa_application", "general", "professional"
    notes: Optional[str] = None


class SocialMediaAuditResponse(BaseModel):
    audit_id: str
    user_id: str
    platform: str
    profile_url: str
    audit_type: str
    status: str  # "pending", "in_progress", "completed", "failed"
    findings: Optional[Dict[str, Any]] = None
    recommendations: Optional[List[str]] = None
    risk_score: Optional[int] = None  # 0-100
    notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime] = None


class SocialMediaAuditUpdate(BaseModel):
    status: Optional[str] = None
    findings: Optional[Dict[str, Any]] = None
    recommendations: Optional[List[str]] = None
    risk_score: Optional[int] = None
    notes: Optional[str] = None


@router.post("/", response_model=SocialMediaAuditResponse, status_code=status.HTTP_201_CREATED)
async def create_social_media_audit(
    audit_data: SocialMediaAuditCreate,
    current_user: UserInDB = Depends(get_current_user)
):
    """
    Create a new social media audit request
    """
    try:
        audit_id = str(uuid.uuid4())
        now = datetime.utcnow()
        
        audit_doc = {
            "audit_id": audit_id,
            "user_id": current_user.uid,
            "platform": audit_data.platform,
            "profile_url": audit_data.profile_url,
            "audit_type": audit_data.audit_type,
            "status": "pending",
            "findings": None,
            "recommendations": None,
            "risk_score": None,
            "notes": audit_data.notes,
            "created_at": now,
            "updated_at": now,
            "completed_at": None
        }
        
        # Save to Firestore
        db.collection('SOCIAL_MEDIA_AUDIT').document(audit_id).set(audit_doc)
        
        return SocialMediaAuditResponse(
            audit_id=audit_id,
            user_id=current_user.uid,
            platform=audit_data.platform,
            profile_url=audit_data.profile_url,
            audit_type=audit_data.audit_type,
            status="pending",
            findings=None,
            recommendations=None,
            risk_score=None,
            notes=audit_data.notes,
            created_at=now,
            updated_at=now,
            completed_at=None
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create social media audit: {str(e)}"
        )


@router.get("/", response_model=List[SocialMediaAuditResponse])
async def get_social_media_audits(
    current_user: UserInDB = Depends(get_current_user),
    status_filter: Optional[str] = None,
    platform_filter: Optional[str] = None,
    limit: int = 50
):
    """
    Get all social media audits for the current user
    """
    try:
        query = db.collection('SOCIAL_MEDIA_AUDIT').where('user_id', '==', current_user.uid)
        
        # Apply filters
        if status_filter:
            query = query.where('status', '==', status_filter)
        if platform_filter:
            query = query.where('platform', '==', platform_filter)
        
        # Execute query
        docs = query.limit(limit).order_by('created_at', direction='DESCENDING').stream()
        
        audits = []
        for doc in docs:
            data = doc.to_dict()
            audits.append(SocialMediaAuditResponse(
                audit_id=data['audit_id'],
                user_id=data['user_id'],
                platform=data['platform'],
                profile_url=data['profile_url'],
                audit_type=data['audit_type'],
                status=data['status'],
                findings=data.get('findings'),
                recommendations=data.get('recommendations'),
                risk_score=data.get('risk_score'),
                notes=data.get('notes'),
                created_at=data['created_at'],
                updated_at=data['updated_at'],
                completed_at=data.get('completed_at')
            ))
        
        return audits
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch social media audits: {str(e)}"
        )


@router.get("/{audit_id}", response_model=SocialMediaAuditResponse)
async def get_social_media_audit(
    audit_id: str,
    current_user: UserInDB = Depends(get_current_user)
):
    """
    Get a specific social media audit by ID
    """
    try:
        doc = db.collection('SOCIAL_MEDIA_AUDIT').document(audit_id).get()
        if not doc.exists:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Social media audit not found"
            )
        
        data = doc.to_dict()
        
        # Verify audit belongs to current user
        if data['user_id'] != current_user.uid:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied: Audit does not belong to current user"
            )
        
        return SocialMediaAuditResponse(
            audit_id=data['audit_id'],
            user_id=data['user_id'],
            platform=data['platform'],
            profile_url=data['profile_url'],
            audit_type=data['audit_type'],
            status=data['status'],
            findings=data.get('findings'),
            recommendations=data.get('recommendations'),
            risk_score=data.get('risk_score'),
            notes=data.get('notes'),
            created_at=data['created_at'],
            updated_at=data['updated_at'],
            completed_at=data.get('completed_at')
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch social media audit: {str(e)}"
        )


@router.put("/{audit_id}", response_model=SocialMediaAuditResponse)
async def update_social_media_audit(
    audit_id: str,
    audit_update: SocialMediaAuditUpdate,
    current_user: UserInDB = Depends(get_current_user)
):
    """
    Update a social media audit
    """
    try:
        # Verify audit exists and belongs to current user
        doc_ref = db.collection('SOCIAL_MEDIA_AUDIT').document(audit_id)
        doc = doc_ref.get()
        
        if not doc.exists:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Social media audit not found"
            )
        
        data = doc.to_dict()
        if data['user_id'] != current_user.uid:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied: Audit does not belong to current user"
            )
        
        # Prepare update data
        update_data = {"updated_at": datetime.utcnow()}
        if audit_update.status is not None:
            update_data["status"] = audit_update.status
            if audit_update.status == "completed":
                update_data["completed_at"] = datetime.utcnow()
        if audit_update.findings is not None:
            update_data["findings"] = audit_update.findings
        if audit_update.recommendations is not None:
            update_data["recommendations"] = audit_update.recommendations
        if audit_update.risk_score is not None:
            update_data["risk_score"] = audit_update.risk_score
        if audit_update.notes is not None:
            update_data["notes"] = audit_update.notes
        
        # Update audit
        doc_ref.update(update_data)
        
        # Fetch updated data
        updated_doc = doc_ref.get()
        updated_data = updated_doc.to_dict()
        
        return SocialMediaAuditResponse(
            audit_id=updated_data['audit_id'],
            user_id=updated_data['user_id'],
            platform=updated_data['platform'],
            profile_url=updated_data['profile_url'],
            audit_type=updated_data['audit_type'],
            status=updated_data['status'],
            findings=updated_data.get('findings'),
            recommendations=updated_data.get('recommendations'),
            risk_score=updated_data.get('risk_score'),
            notes=updated_data.get('notes'),
            created_at=updated_data['created_at'],
            updated_at=updated_data['updated_at'],
            completed_at=updated_data.get('completed_at')
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update social media audit: {str(e)}"
        )


@router.delete("/{audit_id}")
async def delete_social_media_audit(
    audit_id: str,
    current_user: UserInDB = Depends(get_current_user)
):
    """
    Delete a social media audit
    """
    try:
        # Verify audit exists and belongs to current user
        doc_ref = db.collection('SOCIAL_MEDIA_AUDIT').document(audit_id)
        doc = doc_ref.get()
        
        if not doc.exists:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Social media audit not found"
            )
        
        data = doc.to_dict()
        if data['user_id'] != current_user.uid:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied: Audit does not belong to current user"
            )
        
        # Delete audit
        doc_ref.delete()
        
        return {"message": "Social media audit deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete social media audit: {str(e)}"
        )
