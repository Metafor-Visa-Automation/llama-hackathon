import firebase_admin
from firebase_admin import credentials, firestore, storage
from app.core.config import settings
import os


def init_firebase():
    """Initialize Firebase Admin SDK"""
    try:
        # Check if Firebase is already initialized
        if firebase_admin._apps:
            return firebase_admin.get_app()
        
        # Get the path to the service account key
        service_account_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
            settings.firebase_service_account_key_path
        )
        
        # Initialize Firebase Admin SDK
        cred = credentials.Certificate(service_account_path)
        app = firebase_admin.initialize_app(cred, {
            'storageBucket': settings.firebase_storage_bucket,
            'projectId': settings.firebase_project_id
        })
        
        print(f"✅ Firebase initialized successfully for project: {settings.firebase_project_id}")
        return app
        
    except Exception as e:
        print(f"❌ Error initializing Firebase: {str(e)}")
        raise e


def get_firestore_client():
    """Get Firestore database client"""
    return firestore.client()


def get_storage_client():
    """Get Firebase Storage client"""
    return storage.bucket()


# Initialize Firebase when this module is imported
init_firebase()
db = get_firestore_client()
bucket = get_storage_client()
