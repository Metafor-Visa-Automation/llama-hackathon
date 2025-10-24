"""
Simple script to test Firebase connection
Run this to verify Firebase is properly configured
"""

from app.core.firebase import initialize_firebase, get_firestore_db

def test_firebase():
    """Test Firebase initialization and connection"""
    try:
        print("Testing Firebase connection...")
        
        # Initialize Firebase
        initialize_firebase()
        print("[OK] Firebase initialized successfully")
        
        # Get Firestore instance
        db = get_firestore_db()
        print("[OK] Firestore database connected")
        
        # Test write operation
        test_doc = {
            "message": "Firebase connection test",
            "timestamp": "2024-01-01T00:00:00Z"
        }
        
        db.collection("test").document("connection_test").set(test_doc)
        print("[OK] Test document written successfully")
        
        # Test read operation
        doc_ref = db.collection("test").document("connection_test").get()
        if doc_ref.exists:
            print(f"[OK] Test document read successfully: {doc_ref.to_dict()}")
        
        # Clean up test document
        db.collection("test").document("connection_test").delete()
        print("[OK] Test document deleted successfully")
        
        print("\n[SUCCESS] All Firebase tests passed!")
        
    except Exception as e:
        print(f"[ERROR] Firebase test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_firebase()

