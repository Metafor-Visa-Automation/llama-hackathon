# Firebase Collections Structure

## Current Collection Structure

### 1. **USER** Collection (`USER`)
- **Used in**: Authentication, User Management
- **Documents**: One document per user (document ID = Firebase Auth UID)
- **Created by**: Registration endpoint (`POST /api/v1/auth/register`)
- **Accessed by**: All authenticated endpoints via `get_current_user()`

#### Document Structure:
```json
{
  "uid": "firebase_auth_uid",
  "email": "user@example.com",
  "name": "John",
  "surname": "Doe",
  "profile_type": "STUDENT",
  "passport_type": "BORDO",
  "phone": "+1234567890",
  "date_of_birth": "2000-01-01",
  "nationality": "Turkish",
  "created_at": "2024-01-01T00:00:00",
  "updated_at": "2024-01-01T00:00:00"
}
```

### 2. **CHECKLIST_TEMPLATE** Collection
- **Used in**: Checklist Templates API
- **Documents**: Template documents for visa application checklists
- **Access**: Via `/api/v1/checklist-templates` endpoints
- **Document Structure**: Includes `checkId`, `docName`, `category`, etc.

## How the Flow Works

### Registration Flow:
1. User sends registration data
2. Backend creates user in **Firebase Auth** (authentication system)
3. Backend creates document in **USER** collection (Firestore)
4. Returns user data

### Login Flow:
1. User sends email/password
2. Backend verifies user exists in **Firebase Auth**
3. Backend fetches user data from **USER** collection
4. Returns custom token + user data

### Authentication for Protected Endpoints:
1. User sends JWT token in Authorization header
2. `get_current_user()` verifies token with Firebase Auth
3. Fetches user data from **USER** collection
4. Returns UserInDB object

## Status: ✅ CORRECT

- Both collections are used correctly
- USER collection stores user profile data
- Firebase Auth handles authentication
- The flow is working as designed

