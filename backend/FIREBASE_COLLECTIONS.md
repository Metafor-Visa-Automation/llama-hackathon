# Firebase Collections

This application uses **only 3 Firestore collections**:

## 1. users Collection

Stores user profile information.

**Collection Name:** `users` (lowercase)

**Schema:**
```json
{
  "uid": "string",              // Primary Key - Firebase user ID
  "email": "string",
  "name": "string",
  "surname": "string",
  "profile_type": "string",     // e.g., "STUDENT", "WORKER"
  "passport_type": "string",     // e.g., "BORDO", "YESIL"
  "gender": "string",            // Optional - "MALE", "FEMALE", "OTHER"
  "phone": "string",             // Optional
  "date_of_birth": "string",     // Optional
  "nationality": "string",       // Optional - country code
  "address": "string",           // Optional - user's address
  "has_schengen_before": "boolean", // Optional - has the user had a Schengen visa before
  "token": "string",             // Optional - Authentication token (set on login)
  "last_login_at": "timestamp",  // Optional - Last login time (set on login)
  "created_at": "timestamp",
  "updated_at": "timestamp"
}
```

## 2. applications Collection

Stores visa applications created by users.

**Collection Name:** `applications` (lowercase)

**Schema:**
```json
{
  "app_id": "string",                    // Primary Key - UUID
  "user_id": "string",                   // Foreign Key to users
  "application_name": "string",           // User's custom name
  "country_code": "string",              // Two-letter code (e.g., "US", "DE")
  "travel_purpose": "string",             // "Tourism", "Education", "Business"
  "application_start_date": "timestamp", // Optional - Start date
  "application_end_date": "timestamp",    // Optional - End date
  "status": "string",                    // "DRAFT", "SUBMITTED", "APPROVED"
  "application_steps": [                 // Array of step objects
    {
      "step_name": "string",
      "step_details": {}
    }
  ],
  "created_at": "timestamp",
  "updated_at": "timestamp"
}
```

## 3. documents Collection

Stores user's uploaded documents.

**Collection Name:** `documents` (lowercase)

**Schema:**
```json
{
  "doc_id": "string",            // Primary Key - UUID
  "user_id": "string",            // Foreign Key to users
  "storage_path": "string",       // Firebase Storage path
  "status": "string",             // "PENDING_VALIDATION", "APPROVED", "REJECTED"
  "created_at": "timestamp",
  "updated_at": "timestamp"
}
```

## API Endpoints

### Authentication
- POST `/api/v1/auth/register` - Register new user (creates Firebase Auth user)
- POST `/api/v1/auth/login` - Login user (generates and stores token in user document)

### Users
- POST `/api/v1/users/users` - Create new user (Firestore only)
- GET `/api/v1/users/me` - Get current user
- PUT `/api/v1/users/me` - Update current user

### Applications
- POST `/api/v1/applications/applications` - Create application
- GET `/api/v1/applications/applications` - Get all applications
- GET `/api/v1/applications/applications/{app_id}` - Get specific application
- PUT `/api/v1/applications/applications/{app_id}` - Update application
- DELETE `/api/v1/applications/applications/{app_id}` - Delete application

### Documents
- POST `/api/v1/documents/documents` - Create document record
- GET `/api/v1/documents/documents` - Get all documents
- GET `/api/v1/documents/documents/{doc_id}` - Get specific document
- PUT `/api/v1/documents/documents/{doc_id}` - Update document
- DELETE `/api/v1/documents/documents/{doc_id}` - Delete document

## Notes

- All collection names are in lowercase
- No other collections are used
- All foreign keys are properly maintained
- Authentication uses the `users` collection

