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
