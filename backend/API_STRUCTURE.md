# API Structure

This is a fresh, clean API structure with only essential endpoints.

## Authentication (`/api/v1/auth/`)

### POST `/api/v1/auth/register` - Register New User
**Request:**
```json
{
  "email": "user@example.com",
  "password": "password123",
  "name": "John",
  "surname": "Doe",
  "profile_type": "STUDENT",
  "passport_type": "BORDO"
}
```

**Response:**
```json
{
  "uid": "firebase-user-id",
  "email": "user@example.com",
  "name": "John",
  "surname": "Doe",
  "profile_type": "STUDENT",
  "passport_type": "BORDO",
  "token": null,
  "last_login_at": null,
  "created_at": "2024-01-01T00:00:00",
  "updated_at": "2024-01-01T00:00:00"
}
```

### POST `/api/v1/auth/login` - Login User
**Request:**
```json
{
  "email": "user@example.com",
  "password": "password123"
}
```

**Response:**
```json
{
  "access_token": "firebase-custom-token",
  "token_type": "bearer",
  "user": {
    "uid": "firebase-user-id",
    "email": "user@example.com",
    "name": "John",
    "surname": "Doe",
    "profile_type": "STUDENT",
    "passport_type": "BORDO",
    "token": "stored-token",
    "last_login_at": "2024-01-01T12:00:00",
    "created_at": "2024-01-01T00:00:00",
    "updated_at": "2024-01-01T12:00:00"
  },
  "expires_in": 3600
}
```

## Users (`/api/v1/users/`)

### GET `/api/v1/users/me` - Get Current User
**Headers:** `Authorization: Bearer <token>`

### PUT `/api/v1/users/me` - Update Current User
**Headers:** `Authorization: Bearer <token>`

**Request:**
```json
{
  "name": "Jane",
  "phone": "+1234567890"
}
```

### DELETE `/api/v1/users/me` - Delete User Account
**Headers:** `Authorization: Bearer <token>`

## Applications (`/api/v1/applications/`)

### CRUD Operations
- POST `/api/v1/applications/applications` - Create application
- GET `/api/v1/applications/applications` - Get all applications
- GET `/api/v1/applications/applications/{app_id}` - Get specific application
- PUT `/api/v1/applications/applications/{app_id}` - Update application
- DELETE `/api/v1/applications/applications/{app_id}` - Delete application

## Documents (`/api/v1/documents/`)

### CRUD Operations
- POST `/api/v1/documents/documents` - Create document
- GET `/api/v1/documents/documents` - Get all documents
- GET `/api/v1/documents/documents/{doc_id}` - Get specific document
- PUT `/api/v1/documents/documents/{doc_id}` - Update document
- DELETE `/api/v1/documents/documents/{doc_id}` - Delete document

## Firebase Collections

### 1. users (lowercase)
Stores user data with token management

### 2. applications (lowercase)
Stores visa applications

### 3. documents (lowercase)
Stores document records

## Features

- **Clean Architecture**: Fresh implementation from scratch
- **Simple Authentication**: Basic register/login flow
- **Token Management**: Tokens stored in user documents
- **CRUD Operations**: Full CRUD for all 3 collections
- **RESTful Design**: Standard HTTP methods

