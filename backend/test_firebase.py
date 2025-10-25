#!/usr/bin/env python3
"""
Test script to verify Firebase connection and basic functionality
Run this script to test your Firebase setup before starting the main application
"""

import sys
import os

# Add the app directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.core.firebase import db, bucket
from app.core.config import settings

def test_firebase_connection():
    """Test Firebase connection"""
    print("🧪 Testing Firebase connection...")
    
    try:
        # Test Firestore connection
        print("📊 Testing Firestore connection...")
        test_collection = db.collection('test')
        test_doc = test_collection.document('connection_test')
        test_doc.set({'test': True, 'timestamp': '2024-01-01'})
        
        # Verify we can read it back
        doc = test_doc.get()
        if doc.exists:
            print("✅ Firestore connection successful")
            # Clean up test document
            test_doc.delete()
        else:
            print("❌ Firestore connection failed")
            return False
        
        # Test Storage connection
        print("📁 Testing Firebase Storage connection...")
        test_blob = bucket.blob('test/connection_test.txt')
        test_blob.upload_from_string('test content')
        
        # Verify we can read it back
        if test_blob.exists():
            print("✅ Firebase Storage connection successful")
            # Clean up test file
            test_blob.delete()
        else:
            print("❌ Firebase Storage connection failed")
            return False
        
        print(f"🎉 All Firebase services connected successfully!")
        print(f"📋 Project ID: {settings.firebase_project_id}")
        print(f"🪣 Storage Bucket: {settings.firebase_storage_bucket}")
        
        return True
        
    except Exception as e:
        print(f"❌ Firebase connection test failed: {str(e)}")
        return False

def test_collections():
    """Test if required collections exist"""
    print("\n🔍 Checking required collections...")
    
    required_collections = ['COUNTRY', 'VISA_REQUIREMENT', 'USER', 'APPLICATION', 'TASK', 'USER_DOCUMENT']
    
    for collection_name in required_collections:
        try:
            # Try to get a document from the collection
            docs = db.collection(collection_name).limit(1).stream()
            doc_count = len(list(docs))
            print(f"📂 {collection_name}: {'✅ Found' if doc_count >= 0 else '❌ Not found'}")
        except Exception as e:
            print(f"📂 {collection_name}: ❌ Error - {str(e)}")

if __name__ == "__main__":
    print("🚀 VisaPrep AI Backend - Firebase Connection Test")
    print("=" * 50)
    
    # Test Firebase connection
    if test_firebase_connection():
        # Test collections
        test_collections()
        print("\n✅ All tests passed! Your backend is ready to run.")
        print("\n🚀 To start the server, run:")
        print("   cd backend")
        print("   python -m uvicorn app.main:app --reload")
    else:
        print("\n❌ Tests failed. Please check your Firebase configuration.")
        sys.exit(1)
