import firebase_admin
from firebase_admin import credentials, firestore, storage
from app.core.config import settings
import os
from unittest.mock import MagicMock

db = None
bucket = None

def init_firebase():
    """Initialize Firebase Admin SDK"""
    global db, bucket
    try:
        if firebase_admin._apps:
            db = firestore.client()
            bucket = storage.bucket()
            return firebase_admin.get_app()
        
        service_account_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
            settings.firebase_service_account_key_path
        )
        
        if not os.path.exists(service_account_path):
            raise FileNotFoundError(f"Firebase service account key not found at {service_account_path}")

        cred = credentials.Certificate(service_account_path)
        app = firebase_admin.initialize_app(cred, {
            'storageBucket': settings.firebase_storage_bucket,
            'projectId': settings.firebase_project_id
        })
        
        db = firestore.client()
        bucket = storage.bucket()
        print(f"[SUCCESS] Firebase initialized successfully for project: {settings.firebase_project_id}")
        return app
        
    except Exception as e:
        print(f"[WARNING] Error initializing Firebase: {str(e)}")
        print("[WARNING] Firebase connection failed. Using a dummy Firestore client.")
        print("[WARNING] API endpoints requiring database access will fail, but Swagger UI will be available.")
        
        # Create a dummy client if initialization fails
        db = MagicMock()
        bucket = MagicMock()
        # You can further configure the mock if needed, e.g.,
        # db.collection.return_value.document.return_value.get.return_value.exists = False
        return None


# Initialize Firebase when this module is imported
init_firebase()
