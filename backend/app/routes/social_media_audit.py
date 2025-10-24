from fastapi import APIRouter, HTTPException, Depends, status
from app.models.schemas import (
    SocialMediaAudit, 
    SocialMediaAuditCreate,
    SocialMediaAuditBase
)
from app.routes.auth import get_current_user
from app.core.firebase import get_firestore_db
from datetime import datetime
import uuid

router = APIRouter()

@router.post("/audit", response_model=SocialMediaAudit)
async def create_social_media_audit(
    audit_data: SocialMediaAuditCreate,
    current_user: dict = Depends(get_current_user)
):
    """Create a new social media audit request"""
    try:
        db = get_firestore_db()
        
        audit_id = str(uuid.uuid4())
        audit_doc = {
            "id": audit_id,
            "user_id": current_user["uid"],
            "visa_application_id": audit_data.visa_application_id,
            "platform": audit_data.platform,
            "username": audit_data.username,
            "audit_status": audit_data.audit_status,
            "created_at": datetime.utcnow(),
            "completed_at": None,
            "risk_score": None,
            "flagged_content": None,
            "recommendations": None
        }
        
        db.collection("social_media_audits").document(audit_id).set(audit_doc)
        
        return SocialMediaAudit(**audit_doc)
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create social media audit: {str(e)}"
        )

@router.get("/audits", response_model=list[SocialMediaAudit])
async def get_user_social_media_audits(current_user: dict = Depends(get_current_user)):
    """Get all social media audits for current user"""
    try:
        db = get_firestore_db()
        
        audits = db.collection("social_media_audits")\
            .where("user_id", "==", current_user["uid"])\
            .order_by("created_at", direction="DESCENDING")\
            .stream()
        
        audit_list = []
        for audit in audits:
            audit_data = audit.to_dict()
            audit_list.append(SocialMediaAudit(**audit_data))
        
        return audit_list
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get social media audits: {str(e)}"
        )

@router.get("/audits/{audit_id}", response_model=SocialMediaAudit)
async def get_social_media_audit(
    audit_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get specific social media audit by ID"""
    try:
        db = get_firestore_db()
        
        audit_doc = db.collection("social_media_audits").document(audit_id).get()
        
        if not audit_doc.exists:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Social media audit not found"
            )
        
        audit_data = audit_doc.to_dict()
        
        # Check if user owns this audit
        if audit_data["user_id"] != current_user["uid"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
        
        return SocialMediaAudit(**audit_data)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get social media audit: {str(e)}"
        )

@router.post("/audits/{audit_id}/start")
async def start_social_media_audit(
    audit_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Start social media audit process"""
    try:
        db = get_firestore_db()
        
        # Check if audit exists and user owns it
        audit_doc = db.collection("social_media_audits").document(audit_id).get()
        if not audit_doc.exists:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Social media audit not found"
            )
        
        audit_data = audit_doc.to_dict()
        if audit_data["user_id"] != current_user["uid"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
        
        # Update audit status to processing
        db.collection("social_media_audits").document(audit_id).update({
            "audit_status": "processing",
            "updated_at": datetime.utcnow()
        })
        
        # This is a placeholder for the actual social media audit process
        # In the actual implementation, this would:
        # 1. Connect to social media APIs
        # 2. Analyze posts, comments, and profile data
        # 3. Use AI to identify potentially problematic content
        # 4. Generate risk score and recommendations
        
        # Simulate audit completion (in real implementation, this would be async)
        audit_result = {
            "audit_status": "completed",
            "completed_at": datetime.utcnow(),
            "risk_score": 0.3,  # Low risk
            "flagged_content": [
                {
                    "post_id": "123456",
                    "content": "Sample flagged content",
                    "risk_level": "low",
                    "recommendation": "Consider removing or making private"
                }
            ],
            "recommendations": [
                "Review and remove posts with political content",
                "Make profile private during application process",
                "Remove posts that contradict travel purpose"
            ]
        }
        
        # Update audit with results
        db.collection("social_media_audits").document(audit_id).update(audit_result)
        
        return {
            "message": "Social media audit completed",
            "audit_id": audit_id,
            "risk_score": audit_result["risk_score"],
            "recommendations_count": len(audit_result["recommendations"])
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to start social media audit: {str(e)}"
        )

@router.get("/audits/{audit_id}/report")
async def get_audit_report(
    audit_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get detailed audit report"""
    try:
        db = get_firestore_db()
        
        # Check if audit exists and user owns it
        audit_doc = db.collection("social_media_audits").document(audit_id).get()
        if not audit_doc.exists:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Social media audit not found"
            )
        
        audit_data = audit_doc.to_dict()
        if audit_data["user_id"] != current_user["uid"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
        
        if audit_data["audit_status"] != "completed":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Audit not completed yet"
            )
        
        # Generate detailed report
        report = {
            "audit_id": audit_id,
            "platform": audit_data["platform"],
            "username": audit_data["username"],
            "risk_score": audit_data["risk_score"],
            "risk_level": "Low" if audit_data["risk_score"] < 0.5 else "Medium" if audit_data["risk_score"] < 0.8 else "High",
            "flagged_content": audit_data["flagged_content"],
            "recommendations": audit_data["recommendations"],
            "audit_summary": {
                "total_posts_analyzed": 150,
                "flagged_posts": len(audit_data["flagged_content"]) if audit_data["flagged_content"] else 0,
                "compliance_score": 85,
                "areas_of_concern": ["Political content", "Travel contradictions"]
            }
        }
        
        return report
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get audit report: {str(e)}"
        )

@router.delete("/audits/{audit_id}")
async def delete_social_media_audit(
    audit_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Delete social media audit"""
    try:
        db = get_firestore_db()
        
        # Check if audit exists and user owns it
        audit_doc = db.collection("social_media_audits").document(audit_id).get()
        if not audit_doc.exists:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Social media audit not found"
            )
        
        audit_data = audit_doc.to_dict()
        if audit_data["user_id"] != current_user["uid"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
        
        # Delete audit
        db.collection("social_media_audits").document(audit_id).delete()
        
        return {"message": "Social media audit deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete social media audit: {str(e)}"
        )
