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
    Requires authentication
    """
    try:
        user_doc = db.collection('users').document(current_user.uid).get()
        if not user_doc.exists:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        data = user_doc.to_dict()
        return UserResponse(
            uid=data['uid'],
            email=data['email'],
            name=data['name'],
            surname=data['surname'],
            profile_type=data['profile_type'],
            passport_type=data['passport_type'],
            gender=data.get('gender'),
            phone=data.get('phone'),
            date_of_birth=data.get('date_of_birth'),
            nationality=data.get('nationality'),
            address=data.get('address'),
            has_schengen_before=data.get('has_schengen_before', False),
            token=data.get('token'),
            last_login_at=data.get('last_login_at'),
            created_at=data['created_at'],
            updated_at=data['updated_at']
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get user profile: {str(e)}"
        )


@router.put("/me", response_model=UserResponse)
async def update_user_profile(
    user_update: UserUpdate,
    current_user: UserInDB = Depends(get_current_user)
):
    """
    Update current user's profile
    Requires authentication
    """
    try:
        # Prepare update data (only include non-None values)
        update_data = {}
        if user_update.name is not None:
            update_data["name"] = user_update.name
        if user_update.surname is not None:
            update_data["surname"] = user_update.surname
        if user_update.profile_type is not None:
            update_data["profile_type"] = user_update.profile_type
        if user_update.passport_type is not None:
            update_data["passport_type"] = user_update.passport_type
        if user_update.gender is not None:
            update_data["gender"] = user_update.gender
        if user_update.phone is not None:
            update_data["phone"] = user_update.phone
        if user_update.date_of_birth is not None:
            update_data["date_of_birth"] = user_update.date_of_birth
        if user_update.nationality is not None:
            update_data["nationality"] = user_update.nationality
        if user_update.address is not None:
            update_data["address"] = user_update.address
        if user_update.has_schengen_before is not None:
            update_data["has_schengen_before"] = user_update.has_schengen_before
        
        # Always update the timestamp
        update_data["updated_at"] = datetime.utcnow()
        
        # Update in Firestore
        db.collection('users').document(current_user.uid).update(update_data)
        
        # Fetch updated user data
        updated_doc = db.collection('users').document(current_user.uid).get()
        updated_data = updated_doc.to_dict()
        
        return UserResponse(
            uid=updated_data["uid"],
            email=updated_data["email"],
            name=updated_data["name"],
            surname=updated_data["surname"],
            profile_type=updated_data["profile_type"],
            passport_type=updated_data["passport_type"],
            gender=updated_data.get("gender"),
            phone=updated_data.get("phone"),
            date_of_birth=updated_data.get("date_of_birth"),
            nationality=updated_data.get("nationality"),
            address=updated_data.get("address"),
            has_schengen_before=updated_data.get("has_schengen_before", False),
            token=updated_data.get("token"),
            last_login_at=updated_data.get("last_login_at"),
            created_at=updated_data["created_at"],
            updated_at=updated_data["updated_at"]
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update profile: {str(e)}"
        )


@router.delete("/me")
async def delete_user_profile(current_user: UserInDB = Depends(get_current_user)):
    """
    Delete current user's account
    Requires authentication
    """
    try:
        # Delete from Firestore
        db.collection('users').document(current_user.uid).delete()
        
        # Optionally delete from Firebase Auth (requires admin privilege)
        # from firebase_admin import auth
        # auth.delete_user(current_user.uid)
        
        return {"message": "User account deleted successfully"}
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete user account: {str(e)}"
        )

