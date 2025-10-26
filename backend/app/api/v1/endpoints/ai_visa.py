"""
AI Visa Checklist Endpoint
Communicates with external AI service to generate visa checklists
"""
from fastapi import APIRouter, HTTPException, status, Depends, Body
from app.models.schemas import AIVisaChecklistRequest
from app.services.ai_visa_service import ai_visa_service
from app.services.security import get_current_user, UserInDB
from app.core.firebase import db
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post(
    "/visa-checklist",
    response_model=Dict[str, Any],
    status_code=status.HTTP_200_OK,
    summary="Generate AI Visa Checklist",
    description="Generate a visa checklist using external AI service. Takes user info (nationality, occupation, travel purpose) and sends to AI API."
)
async def generate_ai_visa_checklist(
    current_user: UserInDB = Depends(get_current_user),
    request: Optional[AIVisaChecklistRequest] = Body(default=None)
) -> Dict[str, Any]:
    """
    Generate visa checklist using external AI API
    
    This endpoint:
    1. Takes user information from the authenticated user
    2. Gets visa_type, travel_purpose, and occupation from request or user profile
    3. Calls external AI API to generate checklist
    4. Returns the response directly to frontend without modification
    
    Args:
        request: AIVisaChecklistRequest with optional overrides
        current_user: Authenticated user from dependency injection
        
    Returns:
        Dictionary containing the AI-generated checklist (passed through from external API)
    """
    try:
        # Use default values if request is None
        if request is None:
            request = AIVisaChecklistRequest()
        
        # Get user's nationality from their profile
        nationality = current_user.nationality
        if not nationality:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User nationality is not set. Please update your profile."
            )
        
        # Get user's occupation - could be from profile or a separate field
        occupation = request.occupation
        if not occupation:
            # Try to get from user profile or use profile type as fallback
            occupation = current_user.profile_type  # STUDENT, WORKER, etc.
        
        # Get travel purpose - use from request or user's profile type
        travel_purpose = request.travel_purpose
        if not travel_purpose:
            # Map profile type to travel purpose
            profile_to_purpose = {
                "STUDENT": "Education",
                "WORKER": "Employment",
                "TOURIST": "Tourism",
                "BUSINESS": "Business"
            }
            travel_purpose = profile_to_purpose.get(current_user.profile_type, "Tourism")
        
        # Get visa type - use from request or derive from travel purpose
        visa_type = request.visa_type
        if not visa_type:
            # Map travel purpose to visa type
            purpose_to_visa = {
                "Education": "student",
                "Employment": "work",
                "Tourism": "tourist",
                "Business": "business"
            }
            visa_type = purpose_to_visa.get(travel_purpose, "tourist")
        
        # For now, we'll use a default destination country
        # In a real application, this should come from the user's current application
        # or be provided in the request
        destination_country = "Almanya"  # Default to Germany
        
        # You might want to get this from user's active application
        # Example: Get user's most recent application
        try:
            apps_query = db.collection('applications').where(
                'user_id', '==', current_user.uid
            ).order_by('created_at', direction='DESCENDING').limit(1).stream()
            
            apps = list(apps_query)
            if apps:
                latest_app = apps[0].to_dict()
                # Get country name from country_code if available
                country_code = latest_app.get('country_code')
                if country_code:
                    # Try to get country name from countries collection
                    country_doc = db.collection('countries').document(country_code).get()
                    if country_doc.exists:
                        destination_country = country_doc.to_dict().get('name', destination_country)
        except Exception as e:
            logger.warning(f"Could not fetch user's application for destination country: {str(e)}")
        
        logger.info(f"Generating AI visa checklist for user {current_user.uid}")
        logger.info(f"Parameters - Nationality: {nationality}, Destination: {destination_country}, "
                   f"Visa Type: {visa_type}, Occupation: {occupation}, Travel Purpose: {travel_purpose}")
        
        # Call external AI service
        result = await ai_visa_service.generate_checklist(
            nationality=nationality,
            destination_country=destination_country,
            visa_type=visa_type,
            occupation=occupation,
            travel_purpose=travel_purpose,
            force_refresh=request.force_refresh,
            temperature=request.temperature
        )
        
        logger.info(f"Successfully generated AI visa checklist for user {current_user.uid}")
        
        # Return the response directly without modification
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating AI visa checklist: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate visa checklist: {str(e)}"
        )
