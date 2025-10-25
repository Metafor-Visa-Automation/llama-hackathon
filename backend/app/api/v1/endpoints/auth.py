from fastapi import APIRouter, HTTPException, status, Depends
from firebase_admin import auth
from app.core.firebase import db
from app.models.schemas import UserCreate, UserResponse, UserInDB
from app.services.security import get_current_user
from datetime import datetime
import uuid

router = APIRouter()


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register_user(user_data: UserCreate):
    """
    Register a new user
    Creates user in Firebase Auth and corresponding document in Firestore
    """
    try:
        # Step 1: Create user in Firebase Auth
        firebase_user = auth.create_user(
            email=user_data.email,
            password=user_data.password,
            display_name=f"{user_data.name} {user_data.surname}"
        )
        
        # Step 2: Create user document in Firestore
        now = datetime.utcnow()
        user_doc_data = {
            "uid": firebase_user.uid,
            "email": user_data.email,
            "name": user_data.name,
            "surname": user_data.surname,
            "profile_type": user_data.profile_type.value,
            "passport_type": user_data.passport_type.value,
            "phone": user_data.phone,
            "date_of_birth": user_data.date_of_birth,
            "nationality": user_data.nationality,
            "created_at": now,
            "updated_at": now
        }
        
        # Save to Firestore
        db.collection('USER').document(firebase_user.uid).set(user_doc_data)
        
        # Return user response
        return UserResponse(
            uid=firebase_user.uid,
            email=user_data.email,
            name=user_data.name,
            surname=user_data.surname,
            profile_type=user_data.profile_type,
            passport_type=user_data.passport_type,
            phone=user_data.phone,
            date_of_birth=user_data.date_of_birth,
            nationality=user_data.nationality,
            created_at=now,
            updated_at=now
        )
        
    except auth.EmailAlreadyExistsError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    except auth.InvalidEmailError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid email format"
        )
    except auth.WeakPasswordError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Weak password: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Registration failed: {str(e)}"
        )


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: UserInDB = Depends(get_current_user)):
    """
    Get current user information
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
