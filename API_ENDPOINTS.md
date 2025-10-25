# API Endpoints Documentation

## Available API Endpoints

### ✅ Checklist Templates API (`/api/v1/checklist-templates`)

**Base URL:** `http://localhost:8000/api/v1/checklist-templates`

#### Endpoints:

1. **GET** `/checklist-templates`
   - Get all checklist templates
   - Query params: `category`, `mandatory_only`, `required_for`, `limit`
   - Returns: List of `ChecklistTemplateResponse`

2. **GET** `/checklist-templates/{template_id}`
   - Get specific template by ID
   - Returns: `ChecklistTemplateResponse`

3. **GET** `/checklist-templates/categories`
   - Get all available template categories
   - Returns: List of category names

4. **GET** `/checklist-templates/by-category/{category}`
   - Get templates by specific category
   - Query params: `mandatory_only`
   - Returns: List of `ChecklistTemplateResponse`

5. **GET** `/checklist-templates/stats`
   - Get template statistics
   - Returns: Statistics object

---

### ✅ Notifications API (`/api/v1/notifications`)

**Base URL:** `http://localhost:8000/api/v1/notifications`

#### Endpoints:

1. **GET** `/notifications`
   - Get user's notifications
   - Query params: `unread_only`, `notification_type`, `limit`, `offset`
   - Returns: List of `NotificationResponse`

2. **GET** `/notifications/{notification_id}`
   - Get specific notification
   - Returns: `NotificationResponse`

3. **POST** `/notifications`
   - Create a new notification
   - Body: `NotificationCreate`
   - Returns: `NotificationResponse`

4. **PUT** `/notifications/{notification_id}/read`
   - Mark specific notification as read
   - Returns: `NotificationResponse`

5. **PUT** `/notifications/mark-read`
   - Mark multiple notifications as read
   - Body: `NotificationMarkRead`
   - Returns: Status object

6. **PUT** `/notifications/mark-all-read`
   - Mark all user notifications as read
   - Returns: Status object

7. **DELETE** `/notifications/{notification_id}`
   - Delete a specific notification
   - Returns: Status object

8. **GET** `/notifications/stats`
   - Get notification statistics
   - Returns: Statistics object

---

### ✅ Countries API (`/api/v1/countries`)

**Base URL:** `http://localhost:8000/api/v1/countries`

#### Endpoints:

1. **GET** `/countries`
   - Get all countries
   - Query params: `schengen_only`, `search`, `limit`
   - Returns: List of `CountryResponse`

2. **GET** `/countries/{country_code}`
   - Get specific country
   - Returns: `CountryResponse`

3. **GET** `/countries/schengen/list`
   - Get Schengen countries
   - Returns: List of `CountryResponse`

4. **GET** `/countries/stats`
   - Get country statistics
   - Returns: Statistics object

---

### ✅ Visa Requirements API (`/api/v1/visa-requirements`)

**Base URL:** `http://localhost:8000/api/v1/visa-requirements`

#### Endpoints:

1. **GET** `/visa-requirements`
   - Get all visa requirements
   - Query params: `origin_country`, `destination_country`, `limit`
   - Returns: List of `VisaRequirementResponse`

2. **GET** `/visa-requirements/{req_id}`
   - Get specific visa requirement
   - Returns: `VisaRequirementResponse`

3. **GET** `/visa-requirements/{req_id}/templates`
   - Get checklist templates for a visa requirement
   - Query params: `category`, `mandatory_only`, `profile_type`
   - Returns: List of `ChecklistTemplateResponse`

4. **GET** `/visa-requirements/{req_id}/templates/{template_id}`
   - Get specific checklist template
   - Returns: `ChecklistTemplateResponse`

5. **GET** `/visa-requirements/search`
   - Search visa requirements
   - Query params: `origin_country`, `destination_country`, `passport_type`
   - Returns: List of `VisaRequirementResponse`

6. **GET** `/visa-requirements/{req_id}/letter-templates`
   - Get letter templates for a visa requirement
   - Returns: List of letter templates

7. **GET** `/visa-requirements/stats`
   - Get visa requirement statistics
   - Returns: Statistics object

---

## Authentication

All endpoints except `/api/v1/auth/*` require authentication via Bearer token.

**Example:**
```bash
curl -H "Authorization: Bearer YOUR_TOKEN" http://localhost:8000/api/v1/notifications
```

---

## Response Format

All endpoints return JSON with the following structure:

### Success Response:
```json
{
  "data": [...],
  "message": "Success"
}
```

### Error Response:
```json
{
  "detail": "Error message",
  "status_code": 400
}
```

---

## Example Usage

### Get all checklist templates:
```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
  http://localhost:8000/api/v1/checklist-templates
```

### Get mandatory templates for tourists:
```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
  "http://localhost:8000/api/v1/checklist-templates?mandatory_only=true&required_for=TOURIST"
```

### Get user notifications:
```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
  http://localhost:8000/api/v1/notifications
```

### Mark notification as read:
```bash
curl -X PUT \
  -H "Authorization: Bearer YOUR_TOKEN" \
  http://localhost:8000/api/v1/notifications/{notification_id}/read
```

---

## Mock Data

The system includes mock data for testing:
- 5 users with different profile types
- 3 teams (family, business, student)
- 3 applications in different statuses
- 5 tasks with various completion states
- 4 user documents with OCR results
- 5 notifications with different types
- 37 checklist templates (already in your Firebase)

---

## Interactive API Documentation

Once the server is running, visit:
- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

These provide interactive documentation and testing interface for all endpoints.

