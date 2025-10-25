from fastapi import APIRouter, HTTPException, status, Depends
from app.core.firebase import db
from app.models.schemas import (
    DocumentAnalysisRequest, DocumentAnalysisResponse,
    VisaRecommendationRequest, VisaRecommendationResponse
)
from app.services.security import get_current_user, UserInDB
from datetime import datetime
import uuid

router = APIRouter()


@router.post("/ai/analyze-document", response_model=DocumentAnalysisResponse, status_code=status.HTTP_201_CREATED)
async def analyze_document(
    analysis_request: DocumentAnalysisRequest,
    current_user: UserInDB = Depends(get_current_user)
):
    """
    Analyze uploaded document using AI
    """
    try:
        # Verify task exists and belongs to current user
        task_doc = db.collection('TASK').document(analysis_request.task_id).get()
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
        
        # Check if documents are uploaded for this task
        docs_query = db.collection('USER_DOCUMENT').where(
            'task_id', '==', analysis_request.task_id
        ).where('user_id', '==', current_user.uid).stream()
        
        documents = list(docs_query)
        if not documents:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No documents found for this task"
            )
        
        # Create analysis record
        analysis_id = str(uuid.uuid4())
        now = datetime.utcnow()
        
        # Simulate AI analysis (in production, integrate with actual AI service)
        analysis_result = simulate_document_analysis(
            analysis_request.analysis_type,
            task_data['title'],
            len(documents)
        )
        
        analysis_doc = {
            "analysis_id": analysis_id,
            "task_id": analysis_request.task_id,
            "user_id": current_user.uid,
            "document_type": analysis_request.analysis_type,
            "confidence_score": analysis_result['confidence_score'],
            "findings": analysis_result['findings'],
            "recommendations": analysis_result['recommendations'],
            "issues": analysis_result['issues'],
            "status": "completed",
            "created_at": now,
            "updated_at": now
        }
        
        # Save analysis to Firestore
        db.collection('DOCUMENT_ANALYSIS').document(analysis_id).set(analysis_doc)
        
        return DocumentAnalysisResponse(
            analysis_id=analysis_id,
            task_id=analysis_request.task_id,
            document_type=analysis_request.analysis_type,
            confidence_score=analysis_result['confidence_score'],
            findings=analysis_result['findings'],
            recommendations=analysis_result['recommendations'],
            issues=analysis_result['issues'],
            status="completed",
            created_at=now
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to analyze document: {str(e)}"
        )


def simulate_document_analysis(analysis_type: str, task_title: str, document_count: int) -> dict:
    """
    Simulate AI document analysis
    In production, this would integrate with actual AI services like OpenAI, Google Vision, etc.
    """
    base_findings = [
        "Document appears to be clear and readable",
        "All required information is present",
        "Document format is acceptable"
    ]
    
    base_recommendations = [
        "Ensure document is not expired",
        "Verify all personal information is correct",
        "Keep a digital copy for your records"
    ]
    
    base_issues = []
    
    # Type-specific analysis
    if analysis_type == "passport":
        base_findings.extend([
            "Passport photo meets requirements",
            "Personal details are clearly visible",
            "Passport appears to be valid"
        ])
        base_recommendations.extend([
            "Ensure passport has at least 6 months validity",
            "Check that passport is not damaged"
        ])
        base_issues.extend([
            "Passport photo may be too dark" if "photo" in task_title.lower() else None
        ])
    
    elif analysis_type == "financial":
        base_findings.extend([
            "Financial documents show sufficient funds",
            "Bank statements are recent and complete",
            "Account information is clearly visible"
        ])
        base_recommendations.extend([
            "Ensure statements cover required period",
            "Verify account balance meets requirements"
        ])
    
    elif analysis_type == "academic":
        base_findings.extend([
            "Academic credentials are properly certified",
            "Institution information is clearly stated",
            "Degree information is complete"
        ])
        base_recommendations.extend([
            "Ensure transcripts are official",
            "Verify institution accreditation"
        ])
    
    # Filter out None values
    base_issues = [issue for issue in base_issues if issue is not None]
    
    # Calculate confidence score based on document count and type
    confidence_score = min(0.95, 0.7 + (document_count * 0.05) + (0.1 if analysis_type != "general" else 0))
    
    return {
        "confidence_score": round(confidence_score, 2),
        "findings": base_findings,
        "recommendations": base_recommendations,
        "issues": base_issues
    }


@router.post("/ai/visa-recommendation", response_model=VisaRecommendationResponse, status_code=status.HTTP_201_CREATED)
async def get_visa_recommendation(
    recommendation_request: VisaRecommendationRequest,
    current_user: UserInDB = Depends(get_current_user)
):
    """
    Get AI-powered visa recommendations based on user profile and preferences
    """
    try:
        recommendation_id = str(uuid.uuid4())
        now = datetime.utcnow()
        
        # Generate AI-powered visa recommendation
        recommendation = generate_visa_recommendation(
            recommendation_request,
            current_user
        )
        
        recommendation_doc = {
            "recommendation_id": recommendation_id,
            "user_id": current_user.uid,
            "origin_country": recommendation_request.origin_country,
            "destination_country": recommendation_request.destination_country,
            "recommended_visa_type": recommendation['recommended_visa_type'],
            "confidence_score": recommendation['confidence_score'],
            "requirements": recommendation['requirements'],
            "estimated_processing_time": recommendation['estimated_processing_time'],
            "estimated_cost": recommendation['estimated_cost'],
            "success_probability": recommendation['success_probability'],
            "alternatives": recommendation['alternatives'],
            "tips": recommendation['tips'],
            "created_at": now
        }
        
        # Save recommendation to Firestore
        db.collection('VISA_RECOMMENDATION').document(recommendation_id).set(recommendation_doc)
        
        return VisaRecommendationResponse(
            recommendation_id=recommendation_id,
            user_id=current_user.uid,
            origin_country=recommendation_request.origin_country,
            destination_country=recommendation_request.destination_country,
            recommended_visa_type=recommendation['recommended_visa_type'],
            confidence_score=recommendation['confidence_score'],
            requirements=recommendation['requirements'],
            estimated_processing_time=recommendation['estimated_processing_time'],
            estimated_cost=recommendation['estimated_cost'],
            success_probability=recommendation['success_probability'],
            alternatives=recommendation['alternatives'],
            tips=recommendation['tips'],
            created_at=now
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate visa recommendation: {str(e)}"
        )


def generate_visa_recommendation(request: VisaRecommendationRequest, user: UserInDB) -> dict:
    """
    Generate AI-powered visa recommendation
    In production, this would integrate with actual AI services and visa databases
    """
    # Base recommendation logic based on user profile and preferences
    origin = request.origin_country.upper()
    destination = request.destination_country.upper()
    purpose = request.purpose.lower()
    
    # Determine recommended visa type based on purpose and countries
    if purpose == "study":
        recommended_visa = "Student Visa"
        confidence = 0.85
        processing_time = "2-8 weeks"
        cost = "€80-150"
        success_prob = 0.78
    elif purpose == "work":
        recommended_visa = "Work Visa"
        confidence = 0.80
        processing_time = "4-12 weeks"
        cost = "€100-200"
        success_prob = 0.72
    elif purpose == "tourism":
        recommended_visa = "Tourist Visa"
        confidence = 0.90
        processing_time = "1-4 weeks"
        cost = "€60-100"
        success_prob = 0.85
    elif purpose == "business":
        recommended_visa = "Business Visa"
        confidence = 0.82
        processing_time = "2-6 weeks"
        cost = "€80-120"
        success_prob = 0.80
    else:
        recommended_visa = "General Visa"
        confidence = 0.75
        processing_time = "3-8 weeks"
        cost = "€70-150"
        success_prob = 0.70
    
    # Generate requirements based on visa type and user profile
    requirements = [
        "Valid passport with at least 6 months validity",
        "Completed visa application form",
        "Recent passport-sized photographs",
        "Proof of financial means",
        "Travel itinerary or invitation letter"
    ]
    
    if purpose == "study":
        requirements.extend([
            "Letter of acceptance from educational institution",
            "Academic transcripts and certificates",
            "Proof of language proficiency",
            "Health insurance coverage"
        ])
    elif purpose == "work":
        requirements.extend([
            "Employment contract or job offer",
            "Work permit or authorization",
            "Professional qualifications",
            "Company sponsorship letter"
        ])
    elif purpose == "tourism":
        requirements.extend([
            "Hotel reservations or accommodation proof",
            "Return flight tickets",
            "Travel insurance",
            "Bank statements showing sufficient funds"
        ])
    
    # Generate tips based on user profile and destination
    tips = [
        "Apply well in advance of your intended travel date",
        "Ensure all documents are properly translated if required",
        "Keep copies of all submitted documents",
        "Check embassy website for specific requirements"
    ]
    
    if user.passport_type.value == "YESIL":
        tips.append("Green passport holders may have expedited processing")
    elif user.passport_type.value == "BORDO":
        tips.append("Red passport holders should allow extra processing time")
    
    # Generate alternatives
    alternatives = [
        {
            "visa_type": "eVisa",
            "description": "Electronic visa for faster processing",
            "processing_time": "1-3 days",
            "cost": "€50-80"
        },
        {
            "visa_type": "Visa on Arrival",
            "description": "Available at destination airport",
            "processing_time": "Immediate",
            "cost": "€30-60"
        }
    ]
    
    return {
        "recommended_visa_type": recommended_visa,
        "confidence_score": confidence,
        "requirements": requirements,
        "estimated_processing_time": processing_time,
        "estimated_cost": cost,
        "success_probability": success_prob,
        "alternatives": alternatives,
        "tips": tips
    }
