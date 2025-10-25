# Users API Endpoints

## Available Endpoints

Note: Login is handled by `/api/v1/auth/login` endpoint

### 1. POST `/api/v1/users/users` - Create User
**Request Body:**
```json
{
  "email": "user@example.com",
  "name": "John",
  "surname": "Doe",
  "profile_type": "STUDENT",
  "passport_type": "BORDO",
  "phone": "+1234567890",
  "date_of_birth": "1990-01-01",
  "nationality": "TR"
}
```

**Response:**
```json
{
  "uid": "generated-uuid",
  "email": "user@example.com",
  "name": "John",
  "surname": "Doe",
  "profile_type": "STUDENT",
  "passport_type": "BORDO",
  "phone": "+1234567890",
  "date_of_birth": "1990-01-01",
  "nationality": "TR",
  "token": null,
  "last_login_at": null,
  "created_at": "2024-01-01T00:00:00",
  "updated_at": "2024-01-01T00:00:00"
}
```

**Features:**
- Creates user in Firestore `users` collection
- Checks for duplicate email
- Generates unique UID
- Initializes token fields as null

---

### 2. GET `/api/v1/users/me` - Get Current User (Requires Authentication)
**Headers:**
```
Authorization: Bearer <token>
```

**Response:**
```json
{
  "uid": "user-id",
  "email": "user@example.com",
  "name": "John",
  "surname": "Doe",
  "profile_type": "STUDENT",
  "passport_type": "BORDO",
  "phone": "+1234567890",
  "date_of_birth": "1990-01-01",
  "nationality": "TR",
  "token": "stored_token",
  "last_login_at": "2024-01-01T00:00:00",
  "created_at": "2024-01-01T00:00:00",
  "updated_at": "2024-01-01T00:00:00"
}
```

**Features:**
- Returns authenticated user's profile
- Includes token and last login info
- Requires valid authentication token

---

### 3. PUT `/api/v1/users/me` - Update Current User (Requires Authentication)
**Headers:**
```
Authorization: Bearer <token>
```

**Request Body (all fields optional):**
```json
{
  "name": "Jane",
  "surname": "Smith",
  "profile_type": "WORKER",
  "passport_type": "YESIL",
  "phone": "+9876543210",
  "date_of_birth": "1995-05-15",
  "nationality": "US"
}
```

**Response:**
```json
{
  "uid": "user-id",
  "email": "user@example.com",
  "name": "Jane",
  "surname": "Smith",
  "profile_type": "WORKER",
  "passport_type": "YESIL",
  "phone": "+9876543210",
  "date_of_birth": "1995-05-15",
  "nationality": "US",
  "token": "stored_token",
  "last_login_at": "2024-01-01T00:00:00",
  "created_at": "2024-01-01T00:00:00",
  "updated_at": "2024-01-01T12:00:00"
}
```

**Features:**
- Updates only provided fields
- Returns updated user data
- Updates timestamp automatically

---

## Notes

1. **Login handled by auth**: Use `/api/v1/auth/login` for authentication
2. **Registration handled by auth**: Use `/api/v1/auth/register` for registration with Firebase Auth
3. **Users endpoint**: For creating Firestore user records only (no Firebase Auth)
4. **Token management**: Tokens are automatically stored and managed when users log in via `/api/v1/auth/login`
5. **Collection**: All data stored in Firebase `users` collection (lowercase)

