from fastapi import APIRouter, HTTPException, status, Depends
from app.core.firebase import db
from app.models.schemas import UserUpdate, UserResponse, UserInDB
from app.services.security import get_current_user
from datetime import datetime

router = APIRouter()


@router.get("/me", response_model=UserResponse)
async def get_user_profile(current_user: UserInDB = Depends(get_current_user)):
    """
    Get current user's profile
    """
    # We need to fetch the latest user data from DB to construct the response
    user_doc = db.collection('USER').document(current_user.uid).get()
    if not user_doc.exists:
        raise HTTPException(status_code=404, detail="User not found")
    
    user_data = user_doc.to_dict()

    return UserResponse(
        uid=current_user.uid,
        email=current_user.email,
        name=user_data.get("name"),
        surname=user_data.get("surname"),
        profile_type=user_data.get("profile_type"),
        passport_type=user_data.get("passport_type"),
        phone=user_data.get("phone"),
        date_of_birth=user_data.get("date_of_birth"),
        nationality=user_data.get("nationality"),
        created_at=user_data.get("created_at"),
        updated_at=user_data.get("updated_at")
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
        update_data = user_update.dict(exclude_unset=True)
        
        # Always update the timestamp
        update_data["updated_at"] = datetime.utcnow()
        
        # Update in Firestore
        user_ref = db.collection('USER').document(current_user.uid)
        user_ref.update(update_data)
        
        # Fetch updated user data
        updated_doc = user_ref.get()
        updated_data = updated_doc.to_dict()
        
        return UserResponse(**updated_data)
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update profile: {str(e)}"
        )
