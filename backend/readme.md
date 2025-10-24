# VisaPrep AI Backend

This is the backend API for VisaPrep AI, an AI-powered visa application automation platform.

## Features

- **User Authentication**: Firebase Auth integration for user management
- **Visa Applications**: CRUD operations for visa applications
- **Document Management**: File upload, OCR processing, and validation
- **Social Media Audit**: Automated social media profile analysis
- **AI Form Filling**: Automated visa form completion
- **Dynamic Document Checklists**: Country and visa-type specific requirements

## Tech Stack

- **Framework**: FastAPI (Python)
- **Database**: Firebase Firestore
- **Authentication**: Firebase Auth
- **File Storage**: Local filesystem (can be extended to cloud storage)
- **AI Integration**: Ready for Ollama/Llama 3 integration

## Setup Instructions

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Firebase Configuration**:
   - ✅ The Firebase SDK JSON file (`visa-a05d3-firebase-adminsdk-fbsvc-f627f00882.json`) is already configured
   - Ensure Firebase project is set up with Firestore enabled
   - Create a `.env` file if you need to customize other settings (optional)

3. **Run the Application**:
   ```bash
   python main.py
   ```
   
   Or with uvicorn:
   ```bash
   uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```

4. **API Documentation**:
   - Swagger UI: http://localhost:8000/docs
   - ReDoc: http://localhost:8000/redoc

## API Endpoints

### Authentication (`/api/auth`)
- `POST /register` - Register new user
- `POST /login` - User login
- `GET /me` - Get current user profile
- `PUT /me` - Update user profile
- `DELETE /me` - Delete user account

### Visa Applications (`/api/visa`)
- `POST /applications` - Create visa application
- `GET /applications` - Get user's applications
- `GET /applications/{id}` - Get specific application
- `PUT /applications/{id}` - Update application
- `DELETE /applications/{id}` - Delete application
- `POST /applications/{id}/submit` - Submit application
- `POST /form-filling` - AI form filling
- `GET /document-checklist` - Get document requirements

### Documents (`/api/documents`)
- `POST /upload` - Upload document
- `GET /` - Get user documents
- `GET /application/{id}` - Get application documents
- `GET /{id}` - Get specific document
- `DELETE /{id}` - Delete document
- `POST /{id}/validate` - Validate document with OCR/AI

### Social Media Audit (`/api/social-media`)
- `POST /audit` - Create audit request
- `GET /audits` - Get user audits
- `GET /audits/{id}` - Get specific audit
- `POST /audits/{id}/start` - Start audit process
- `GET /audits/{id}/report` - Get audit report
- `DELETE /audits/{id}` - Delete audit

## Project Structure

```
backend/
├── app/
│   ├── core/
│   │   ├── config.py          # Configuration settings
│   │   └── firebase.py        # Firebase initialization
│   ├── models/
│   │   └── schemas.py         # Pydantic models
│   └── routes/
│       ├── auth.py            # Authentication routes
│       ├── visa_applications.py # Visa application routes
│       ├── documents.py       # Document management routes
│       └── social_media_audit.py # Social media audit routes
├── uploads/                   # File upload directory
├── visa-a05d3-firebase-adminsdk-fbsvc-f627f00882.json  # Firebase credentials
├── main.py                   # FastAPI application entry point
├── requirements.txt          # Python dependencies
└── env.example              # Environment variables template
```

## Firebase Setup

The backend is configured to use the Firebase Admin SDK JSON file directly. The credentials file (`visa-a05d3-firebase-adminsdk-fbsvc-f627f00882.json`) contains all necessary authentication information.

**Important**: Keep this file secure and never commit it to version control. It's already listed in `.gitignore`.

## Next Steps

1. ✅ **Firebase Setup**: Configure Firebase project and add credentials
2. **AI Integration**: Implement Ollama/Llama 3 integration for form filling
3. **OCR Implementation**: Add Tesseract OCR for document processing
4. **Social Media APIs**: Integrate with social media platforms
5. **Cloud Storage**: Move file storage to cloud (AWS S3, Google Cloud Storage)
6. **Testing**: Add comprehensive test suite
7. **Deployment**: Set up production deployment configuration