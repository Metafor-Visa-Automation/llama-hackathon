from fastapi import APIRouter, HTTPException, status, Depends
from firebase_admin import auth
from app.core.firebase import db
from app.models.schemas import UserLogin, UserResponse
from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
import uuid

router = APIRouter()


class UserRegister(BaseModel):
    """Request model for user registration"""
    email: EmailStr
    password: str = Field(..., min_length=6)
    name: str = Field(..., min_length=2, max_length=100)
    surname: str = Field(..., min_length=2, max_length=100)
    profile_type: str = Field(..., description="Profile type (e.g., 'STUDENT', 'WORKER')")
    passport_type: str = Field(..., description="Passport type (e.g., 'BORDO', 'YESIL')")


class LoginResponse(BaseModel):
    """Response model for successful login"""
    access_token: str
    token_type: str = "bearer"
    user: UserResponse
    expires_in: int = 3600


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register_user(user_data: UserRegister):
    """
    Register a new user
    Creates user in Firebase Auth and Firestore
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
            "profile_type": user_data.profile_type,
            "passport_type": user_data.passport_type,
            "token": None,
            "last_login_at": None,
            "created_at": now,
            "updated_at": now
        }
        
        # Save to Firestore
        db.collection('users').document(firebase_user.uid).set(user_doc_data)
        
        return UserResponse(
            uid=firebase_user.uid,
            email=user_data.email,
            name=user_data.name,
            surname=user_data.surname,
            profile_type=user_data.profile_type,
            passport_type=user_data.passport_type,
            phone=None,
            date_of_birth=None,
            nationality=None,
            token=None,
            last_login_at=None,
            created_at=now,
            updated_at=now
        )
        
    except auth.EmailAlreadyExistsError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Registration failed: {str(e)}"
        )


@router.post("/login", response_model=LoginResponse)
async def login_user(login_data: UserLogin):
    """
    Login user with email and password
    Returns token and user information
    """
    try:
        # Step 1: Get user from Firebase Auth
        try:
            firebase_user = auth.get_user_by_email(login_data.email)
        except auth.UserNotFoundError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )
        
        # Step 2: Generate custom token
        custom_token = auth.create_custom_token(firebase_user.uid)
        token_string = custom_token.decode('utf-8')
        
        # Step 3: Get user data from Firestore
        user_doc = db.collection('users').document(firebase_user.uid).get()
        
        if not user_doc.exists:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User profile not found"
            )
        
        user_data = user_doc.to_dict()
        
        # Step 4: Update token and last login
        now = datetime.utcnow()
        db.collection('users').document(firebase_user.uid).update({
            'token': token_string,
            'last_login_at': now,
            'updated_at': now
        })
        
        # Step 5: Get updated user data
        updated_user_doc = db.collection('users').document(firebase_user.uid).get()
        updated_user_data = updated_user_doc.to_dict()
        
        user_response = UserResponse(
            uid=updated_user_data['uid'],
            email=updated_user_data['email'],
            name=updated_user_data['name'],
            surname=updated_user_data['surname'],
            profile_type=updated_user_data['profile_type'],
            passport_type=updated_user_data['passport_type'],
            phone=updated_user_data.get('phone'),
            date_of_birth=updated_user_data.get('date_of_birth'),
            nationality=updated_user_data.get('nationality'),
            token=updated_user_data.get('token'),
            last_login_at=updated_user_data.get('last_login_at'),
            created_at=updated_user_data['created_at'],
            updated_at=updated_user_data['updated_at']
        )
        
        return LoginResponse(
            access_token=token_string,
            token_type="bearer",
            user=user_response,
            expires_in=3600
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Login failed: {str(e)}"
        )

