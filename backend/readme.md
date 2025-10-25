# Backend - VisaPrep AI

A FastAPI-based backend service for the VisaPrep AI application, providing intelligent visa application assistance with Firebase integration.

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Firebase project with Firestore and Storage enabled
- Firebase service account credentials

### Installation & Setup

1. **Install Dependencies**
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

2. **Test Firebase Connection**
   ```bash
   python test_firebase.py
   ```

3. **Start the Server**
   ```bash
   python start_server.py
   ```
   
   Or manually:
   ```bash
   python -m uvicorn app.main:app --reload
   ```

4. **Access API Documentation**
   - Open http://127.0.0.1:8000/docs in your browser
   - Interactive API documentation with Swagger UI

## 📁 Project Structure

```
backend/
├── app/
│   ├── api/
│   │   ├── v1/
│   │   │   └── endpoints/
│   │   │       ├── auth.py          # Authentication endpoints
│   │   │       ├── users.py         # User management
│   │   │       ├── applications.py # Visa applications (core logic)
│   │   │       └── documents.py     # File uploads
│   │   └── api.py                   # API router
│   ├── core/
│   │   ├── config.py                # App configuration
│   │   └── firebase.py              # Firebase initialization
│   ├── models/
│   │   └── schemas.py               # Pydantic models
│   ├── services/
│   │   └── security.py              # Authentication & security
│   └── main.py                      # FastAPI app
├── .env                             # Environment variables
├── requirements.txt                 # Python dependencies
├── test_firebase.py                 # Firebase connection test
├── start_server.py                  # Server startup script
└── visa-a05d3-firebase-adminsdk-fbsvc-f627f00882.json  # Firebase credentials
```

## 🔧 Configuration

### Environment Variables (.env)
```env
FIREBASE_SERVICE_ACCOUNT_KEY_PATH="visa-a05d3-firebase-adminsdk-fbsvc-f627f00882.json"
FIREBASE_STORAGE_BUCKET="visa-a05d3.appspot.com"
FIREBASE_PROJECT_ID="visa-a05d3"
APP_NAME="VisaPrep AI"
APP_VERSION="1.0.0"
DEBUG=True
```

## 🔐 Authentication

The API uses Firebase Authentication with JWT tokens:

1. **Client-side**: Users authenticate with Firebase Auth SDK
2. **Backend**: Validates Firebase ID tokens from Authorization header
3. **Security**: Automatic user verification and authorization

### Example Authentication Flow
```python
# Client sends request with Firebase ID token
headers = {
    "Authorization": "Bearer <firebase_id_token>"
}
```

## 📊 Database Collections

### Core Collections

#### USER Collection
```python
{
    "uid": "firebase_user_id",        # Primary Key
    "email": "user@example.com",
    "name": "John",
    "surname": "Doe",
    "profile_type": "STUDENT",        # STUDENT | WORKER | TOURIST | BUSINESS
    "passport_type": "BORDO",         # BORDO | YESIL
    "phone": "+1234567890",
    "date_of_birth": "1990-01-01",
    "nationality": "TR",
    "created_at": datetime,
    "updated_at": datetime
}
```

#### APPLICATION Collection
```python
{
    "app_id": "uuid",                 # Primary Key
    "user_id": "firebase_user_id",    # FK to USER
    "requirement_id": "tr_de_all",     # FK to VISA_REQUIREMENT
    "status": "DRAFT",                # DRAFT | SUBMITTED | UNDER_REVIEW | APPROVED | REJECTED
    "ai_filled_form_data": {...},     # AI-generated form data
    "created_at": datetime,
    "updated_at": datetime
}
```

#### TASK Collection
```python
{
    "task_id": "uuid",                # Primary Key
    "application_id": "uuid",         # FK to APPLICATION
    "user_id": "firebase_user_id",    # FK to USER
    "template_id": "template_id",     # FK to CHECKLIST_TEMPLATE
    "title": "Passport Copy",
    "description": "Upload a clear copy of your passport",
    "status": "PENDING",              # PENDING | IN_PROGRESS | DONE | REJECTED
    "notes": "Optional notes",
    "created_at": datetime,
    "updated_at": datetime
}
```

#### USER_DOCUMENT Collection
```python
{
    "doc_id": "uuid",                 # Primary Key
    "task_id": "uuid",                # FK to TASK
    "user_id": "firebase_user_id",    # FK to USER
    "storage_path": "user_documents/...",  # Firebase Storage path
    "status": "PENDING_VALIDATION",   # PENDING_VALIDATION | APPROVED | REJECTED
    "created_at": datetime,
    "updated_at": datetime
}
```

### Reference Collections

#### COUNTRY Collection
```python
{
    "countryCode": "DE",              # ISO Alpha-2 code (Primary Key)
    "name": "Germany",
    "schengenMember": true
}
```

#### VISA_REQUIREMENT Collection
```python
{
    "reqId": "tr_de_all",             # Primary Key
    "originCountry": "TR",
    "destinationCode": "DE",
    "applicablePassportTypes": ["BORDO", "YESIL"],
    "visaRequirementType": "VISA_REQUIRED",
    "visaName": "Schengen C Visa",
    "visaFee": "80 EUR",
    "passportValidity": "6 months",
    "applicationLink": "https://...",
    "embassyUrl": "https://...",
    "letterTemplate": ["...", "..."],
    "created_at": datetime,
    "updated_at": datetime,
    "last_verified_at": datetime
}
```

## 🔌 API Endpoints

### Authentication
- `POST /api/v1/auth/register` - Register new user
- `GET /api/v1/auth/me` - Get current user info

### Users
- `GET /api/v1/users/me` - Get user profile
- `PUT /api/v1/users/me` - Update user profile

### Applications (Core Logic)
- `POST /api/v1/applications/applications` - Create new application
- `GET /api/v1/applications/applications` - Get user's applications
- `GET /api/v1/applications/applications/{app_id}/tasks` - Get application tasks

### Documents
- `POST /api/v1/docs/task/{task_id}/upload` - Upload document
- `GET /api/v1/docs/task/{task_id}` - Get task documents
- `DELETE /api/v1/docs/{doc_id}` - Delete document

## 🧠 Core Application Logic

### Application Creation Flow
1. **User submits application** with `requirement_id` and `ai_filled_form_data`
2. **System fetches visa requirement** from `VISA_REQUIREMENT` collection
3. **System fetches checklist templates** from sub-collection `CHECKLIST_TEMPLATE`
4. **System generates tasks** based on user's `profile_type` and template `required_for` field
5. **Tasks created atomically** using Firestore batch operations
6. **User can upload documents** for each task

### Task Generation Logic
```python
# For each checklist template:
if (user.profile_type in template.required_for or 
    'ALL' in template.required_for or 
    not template.required_for):
    # Create task for this template
```

## 🛡️ Security Features

- **Firebase Authentication**: JWT token validation
- **User Authorization**: Automatic user verification
- **File Upload Security**: File type and size validation
- **CORS Protection**: Configurable cross-origin policies
- **Error Handling**: Comprehensive error responses

## 📝 Development

### Running Tests
```bash
python test_firebase.py
```

### Code Structure
- **Models**: Pydantic schemas for request/response validation
- **Services**: Business logic and external service integration
- **Endpoints**: FastAPI route handlers
- **Core**: Configuration and Firebase initialization

### Adding New Features
1. Define models in `app/models/schemas.py`
2. Create endpoints in `app/api/v1/endpoints/`
3. Add business logic in `app/services/`
4. Update API router in `app/api/v1/api.py`

## 🚀 Deployment

### Production Considerations
- Set `DEBUG=False` in environment
- Configure specific CORS origins
- Use environment-specific Firebase credentials
- Set up proper logging and monitoring
- Configure reverse proxy (nginx)

### Docker Support
```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## 📚 Additional Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Firebase Admin SDK](https://firebase.google.com/docs/admin)
- [Pydantic Documentation](https://pydantic-docs.helpmanual.io/)
- [Firestore Security Rules](https://firebase.google.com/docs/firestore/security/get-started)

