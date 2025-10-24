import firebase_admin
from firebase_admin import credentials, firestore, auth as firebase_auth
import os

# Global variables for Firebase services
db = None
auth = None

def initialize_firebase():
    """Initialize Firebase Admin SDK"""
    global db, auth
    
    try:
        # Check if Firebase is already initialized
        if firebase_admin._apps:
            print("Firebase already initialized")
            db = firestore.client()
            auth = firebase_auth
            return
        
        # Path to Firebase service account JSON file
        firebase_credentials_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
            "visa-a05d3-firebase-adminsdk-fbsvc-f627f00882.json"
        )
        
        # Initialize Firebase Admin SDK with JSON file
        cred = credentials.Certificate(firebase_credentials_path)
        firebase_admin.initialize_app(cred)
        
        # Initialize Firestore and Auth
        db = firestore.client()
        auth = firebase_auth
        
        print("Firebase initialized successfully")
        
    except Exception as e:
        print(f"Error initializing Firebase: {e}")
        raise e

def get_firestore_db():
    """Get Firestore database instance"""
    if db is None:
        raise Exception("Firebase not initialized")
    return db

def get_firebase_auth():
    """Get Firebase Auth instance"""
    if auth is None:
        raise Exception("Firebase not initialized")
    return auth
