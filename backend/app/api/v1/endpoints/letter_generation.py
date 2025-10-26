"""
Letter Generation API Endpoints
Generate visa application letters using AI
"""

from fastapi import APIRouter, HTTPException, status, Depends
from app.core.firebase import db
from app.models.schemas import LetterGenerationRequest, LetterGenerationResponse
from app.services.security import get_current_user, UserInDB
from app.services.letter_generation_service import LetterGenerationService
from datetime import datetime
from typing import List, Dict
import uuid
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

# Initialize letter generation service
letter_service = LetterGenerationService()


@router.post("/generate", response_model=LetterGenerationResponse, status_code=status.HTTP_201_CREATED)
async def generate_visa_letter(
    request: LetterGenerationRequest,
    current_user: UserInDB = Depends(get_current_user)
):
    """
    Generate a visa application letter using AI
    
    Generates a professional letter based on user profile and application data
    in the specified language and letter type.
    """
    try:
        # Check if service is available
        if not letter_service.is_available():
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Letter generation service is not available"
            )
        
        # Get user data
        user_ref = db.collection("users").document(current_user.uid)
        user_doc = user_ref.get()
        
        if not user_doc.exists:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User profile not found"
            )
        
        user_data = user_doc.to_dict()
        
        # Get application data if application_id is provided
        application_data = {}
        if request.application_id:
            app_ref = db.collection("applications").document(request.application_id)
            app_doc = app_ref.get()
            
            if not app_doc.exists:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Application not found"
                )
            
            app_data = app_doc.to_dict()
            
            # Verify ownership
            if app_data.get("user_id") != current_user.uid:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Access denied: Application does not belong to current user"
                )
            
            application_data = app_data
        else:
            # Use custom application data
            application_data = request.application_data or {}
        
        # Generate letter
        result = letter_service.generate_letter(
            user_data=user_data,
            application_data=application_data,
            letter_type=request.letter_type,
            language=request.language,
            custom_instructions=request.custom_instructions
        )
        
        if not result.get("success"):
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=result.get("error", "Failed to generate letter")
            )
        
        # Save generated letter to database
        letter_id = str(uuid.uuid4())
        now = datetime.utcnow()
        
        letter_doc = {
            "letter_id": letter_id,
            "user_id": current_user.uid,
            "application_id": request.application_id,
            "letter_type": request.letter_type,
            "language": request.language,
            "letter_content": result["letter"],
            "word_count": result["metadata"]["word_count"],
            "model": result["metadata"]["model"],
            "created_at": now,
            "custom_instructions": request.custom_instructions,
            "metadata": result["metadata"]
        }
        
        db.collection("generated_letters").document(letter_id).set(letter_doc)
        
        logger.info(f"Generated letter {letter_id} for user {current_user.uid}")
        
        return LetterGenerationResponse(
            letter_id=letter_id,
            letter_content=result["letter"],
            letter_type=request.letter_type,
            language=request.language,
            word_count=result["metadata"]["word_count"],
            created_at=now,
            metadata=result["metadata"]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating letter: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate letter: {str(e)}"
        )


@router.get("/languages", response_model=Dict[str, str])
async def get_supported_languages(
    current_user: UserInDB = Depends(get_current_user)
):
    """
    Get list of supported languages for letter generation
    """
    return letter_service.get_supported_languages()


@router.get("/types", response_model=Dict[str, str])
async def get_letter_types(
    current_user: UserInDB = Depends(get_current_user)
):
    """
    Get list of supported letter types
    """
    return letter_service.get_letter_types()


@router.get("/preview-context", response_model=Dict[str, str])
async def preview_letter_context(
    application_id: str = None,
    current_user: UserInDB = Depends(get_current_user)
):
    """
    Preview the context that will be used for letter generation
    Useful for users to see what information will be included
    """
    try:
        # Get user data
        user_ref = db.collection("users").document(current_user.uid)
        user_doc = user_ref.get()
        
        if not user_doc.exists:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User profile not found"
            )
        
        user_data = user_doc.to_dict()
        
        # Get application data if application_id is provided
        application_data = {}
        if application_id:
            app_ref = db.collection("applications").document(application_id)
            app_doc = app_ref.get()
            
            if app_doc.exists:
                app_data = app_doc.to_dict()
                if app_data.get("user_id") == current_user.uid:
                    application_data = app_data
        
        # Get preview
        preview = letter_service.preview_context(user_data, application_data)
        
        return preview
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error previewing context: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to preview context: {str(e)}"
        )


@router.get("/history", response_model=List[LetterGenerationResponse])
async def get_letter_history(
    limit: int = 10,
    current_user: UserInDB = Depends(get_current_user)
):
    """
    Get history of generated letters for current user
    """
    try:
        letters_query = db.collection("generated_letters").where(
            "user_id", "==", current_user.uid
        ).order_by("created_at", direction="DESCENDING").limit(limit)
        
        letters = []
        for doc in letters_query.stream():
            letter_data = doc.to_dict()
            letters.append(LetterGenerationResponse(
                letter_id=letter_data["letter_id"],
                letter_content=letter_data["letter_content"],
                letter_type=letter_data["letter_type"],
                language=letter_data["language"],
                word_count=letter_data["word_count"],
                created_at=letter_data["created_at"],
                metadata=letter_data.get("metadata", {})
            ))
        
        return letters
        
    except Exception as e:
        logger.error(f"Error getting letter history: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get letter history"
        )


@router.get("/{letter_id}", response_model=LetterGenerationResponse)
async def get_letter(
    letter_id: str,
    current_user: UserInDB = Depends(get_current_user)
):
    """
    Get a specific generated letter by ID
    """
    try:
        letter_ref = db.collection("generated_letters").document(letter_id)
        letter_doc = letter_ref.get()
        
        if not letter_doc.exists:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Letter not found"
            )
        
        letter_data = letter_doc.to_dict()
        
        # Verify ownership
        if letter_data["user_id"] != current_user.uid:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied: Letter does not belong to current user"
            )
        
        return LetterGenerationResponse(
            letter_id=letter_data["letter_id"],
            letter_content=letter_data["letter_content"],
            letter_type=letter_data["letter_type"],
            language=letter_data["language"],
            word_count=letter_data["word_count"],
            created_at=letter_data["created_at"],
            metadata=letter_data.get("metadata", {})
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting letter: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get letter"
        )


@router.delete("/{letter_id}")
async def delete_letter(
    letter_id: str,
    current_user: UserInDB = Depends(get_current_user)
):
    """
    Delete a generated letter
    """
    try:
        letter_ref = db.collection("generated_letters").document(letter_id)
        letter_doc = letter_ref.get()
        
        if not letter_doc.exists:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Letter not found"
            )
        
        letter_data = letter_doc.to_dict()
        
        # Verify ownership
        if letter_data["user_id"] != current_user.uid:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied: Letter does not belong to current user"
            )
        
        letter_ref.delete()
        
        return {"message": "Letter deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting letter: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete letter"
        )
