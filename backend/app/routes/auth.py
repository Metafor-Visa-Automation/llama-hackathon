from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.models.schemas import UserCreate, User, UserUpdate
from app.core.firebase import get_firestore_db, get_firebase_auth
from datetime import datetime
import uuid

router = APIRouter()
security = HTTPBearer()

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Get current authenticated user"""
    try:
        auth = get_firebase_auth()
        decoded_token = auth.verify_id_token(credentials.credentials)
        return decoded_token
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

@router.post("/register", response_model=dict)
async def register_user(user_data: UserCreate):
    """Register a new user"""
    try:
        auth = get_firebase_auth()
        db = get_firestore_db()
        
        # Create user in Firebase Auth
        user_record = auth.create_user(
            email=user_data.email,
            password=user_data.password,
            display_name=f"{user_data.first_name} {user_data.last_name}"
        )
        
        # Store additional user data in Firestore
        user_doc = {
            "id": user_record.uid,
            "email": user_data.email,
            "first_name": user_data.first_name,
            "last_name": user_data.last_name,
            "phone": user_data.phone,
            "role": user_data.role.value,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "is_active": True
        }
        
        db.collection("users").document(user_record.uid).set(user_doc)
        
        return {
            "message": "User registered successfully",
            "user_id": user_record.uid,
            "email": user_data.email
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Registration failed: {str(e)}"
        )

@router.post("/login", response_model=dict)
async def login_user(email: str, password: str):
    """Login user and return JWT token"""
    try:
        auth = get_firebase_auth()
        
        # Note: In production, you'd use Firebase Auth REST API for login
        # This is a simplified version for the basic structure
        
        return {
            "message": "Login endpoint - implement Firebase Auth REST API",
            "email": email
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Login failed: {str(e)}"
        )

@router.get("/me", response_model=User)
async def get_current_user_profile(current_user: dict = Depends(get_current_user)):
    """Get current user profile"""
    try:
        db = get_firestore_db()
        user_doc = db.collection("users").document(current_user["uid"]).get()
        
        if not user_doc.exists:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User profile not found"
            )
        
        user_data = user_doc.to_dict()
        return User(**user_data)
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get user profile: {str(e)}"
        )

@router.put("/me", response_model=User)
async def update_user_profile(
    user_update: UserUpdate,
    current_user: dict = Depends(get_current_user)
):
    """Update current user profile"""
    try:
        db = get_firestore_db()
        
        # Prepare update data
        update_data = user_update.dict(exclude_unset=True)
        update_data["updated_at"] = datetime.utcnow()
        
        # Update user document
        db.collection("users").document(current_user["uid"]).update(update_data)
        
        # Get updated user data
        user_doc = db.collection("users").document(current_user["uid"]).get()
        user_data = user_doc.to_dict()
        
        return User(**user_data)
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update user profile: {str(e)}"
        )

@router.delete("/me")
async def delete_user_account(current_user: dict = Depends(get_current_user)):
    """Delete user account"""
    try:
        auth = get_firebase_auth()
        db = get_firestore_db()
        
        # Delete user from Firebase Auth
        auth.delete_user(current_user["uid"])
        
        # Delete user document from Firestore
        db.collection("users").document(current_user["uid"]).delete()
        
        return {"message": "User account deleted successfully"}
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete user account: {str(e)}"
        )
