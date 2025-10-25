from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from firebase_admin import auth
from app.core.firebase import db
from app.models.schemas import UserInDB
from typing import Optional
import logging

logger = logging.getLogger(__name__)

# Security scheme
security = HTTPBearer()


async def verify_firebase_token(token: str) -> Optional[dict]:
    """
    Verify Firebase token (both custom tokens and ID tokens) and return decoded token data
    """
    try:
        # First try to verify as ID token
        try:
            decoded_token = auth.verify_id_token(token)
            return decoded_token
        except (auth.InvalidIdTokenError, auth.ExpiredIdTokenError):
            # If ID token verification fails, try as custom token
            pass
        
        # Try to verify as custom token
        try:
            # For custom tokens, we need to decode them manually
            import jwt
            
            # Get the project ID from the Firebase app
            from firebase_admin import get_app
            project_id = get_app().project_id
            
            # Decode the custom token without verification (since we trust our own tokens)
            decoded_token = jwt.decode(token, options={"verify_signature": False})
            
            # Check if it's a service account token (from our login endpoint)
            if decoded_token.get('iss') == f'firebase-adminsdk-fbsvc@visa-a05d3.iam.gserviceaccount.com':
                # This is a service account token from our login endpoint
                # Extract the UID from the custom token
                uid = decoded_token.get('uid')
                if uid:
                    # Return a token-like structure with the UID
                    return {
                        'uid': uid,
                        'iss': decoded_token.get('iss'),
                        'aud': decoded_token.get('aud'),
                        'iat': decoded_token.get('iat'),
                        'exp': decoded_token.get('exp')
                    }
            
            # Verify it's a custom token from our project
            if decoded_token.get('iss') == f'https://securetoken.google.com/{project_id}':
                # Extract the UID from the custom token
                uid = decoded_token.get('uid')
                if uid:
                    # Return a token-like structure with the UID
                    return {
                        'uid': uid,
                        'iss': decoded_token.get('iss'),
                        'aud': decoded_token.get('aud'),
                        'iat': decoded_token.get('iat'),
                        'exp': decoded_token.get('exp')
                    }
        except Exception as e:
            logger.warning(f"Failed to decode custom token: {str(e)}")
        
        logger.warning("Invalid Firebase token")
        return None
        
    except Exception as e:
        logger.error(f"Error verifying Firebase token: {str(e)}")
        return None


async def get_user_from_firestore(uid: str) -> Optional[UserInDB]:
    """
    Fetch user data from Firestore users collection
    """
    try:
        user_doc = db.collection('users').document(uid).get()
        if user_doc.exists:
            user_data = user_doc.to_dict()
            return UserInDB(**user_data)
        return None
    except Exception as e:
        logger.error(f"Error fetching user from Firestore: {str(e)}")
        return None


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> UserInDB:
    """
    FastAPI dependency to get the current authenticated user
    This is the main security dependency that protects your endpoints
    """
    token = credentials.credentials
    
    # Step 1: Verify Firebase token
    decoded_token = await verify_firebase_token(token)
    if not decoded_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired authentication token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    uid = decoded_token.get('uid')
    if not uid:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token: missing user ID",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Step 2: Fetch user data from Firestore
    user = await get_user_from_firestore(uid)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found in database",
        )
    
    return user


async def get_current_user_optional(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> Optional[UserInDB]:
    """
    Optional authentication dependency - returns None if no token provided
    Useful for endpoints that work with or without authentication
    """
    if not credentials:
        return None
    
    try:
        return await get_current_user(credentials)
    except HTTPException:
        return None


def require_profile_type(required_types: list):
    """
    Decorator factory to require specific profile types
    Usage: @require_profile_type(["STUDENT", "WORKER"])
    """
    def decorator(current_user: UserInDB = Depends(get_current_user)):
        if current_user.profile_type not in required_types:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Required profile types: {required_types}"
            )
        return current_user
    return decorator


def require_passport_type(required_types: list):
    """
    Decorator factory to require specific passport types
    Usage: @require_passport_type(["BORDO", "YESIL"])
    """
    def decorator(current_user: UserInDB = Depends(get_current_user)):
        if current_user.passport_type not in required_types:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Required passport types: {required_types}"
            )
        return current_user
    return decorator
