# VisaPrep AI Backend

A FastAPI-based backend service for intelligent visa application assistance with Firebase integration.

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
│   ├── api/v1/endpoints/     # API endpoints
│   │   ├── auth.py           # Authentication
│   │   ├── users.py          # User management
│   │   ├── applications.py   # Visa applications (core logic)
│   │   ├── documents.py      # File uploads
│   │   ├── tasks.py          # Task management
│   │   ├── countries.py      # Country data
│   │   ├── visa_requirements.py # Visa requirements
│   │   ├── social_media_audit.py # Social media audits
│   │   └── admin.py          # Admin endpoints
│   ├── core/                 # Core configuration
│   │   ├── config.py         # App settings
│   │   └── firebase.py       # Firebase initialization
│   ├── models/               # Data models
│   │   └── schemas.py        # Pydantic schemas
│   ├── services/             # Business logic
│   │   └── security.py       # Authentication & security
│   └── main.py              # FastAPI application
├── requirements.txt         # Dependencies
├── test_firebase.py         # Firebase connection test
├── start_server.py          # Server startup script
└── visa-a05d3-firebase-adminsdk-fbsvc-f627f00882.json # Firebase credentials
```

## 🔧 Configuration

### Environment Variables (.env)
```env
FIREBASE_SERVICE_ACCOUNT_KEY_PATH="visa-a05d3-firebase-adminsdk-fbsvc-f627f00882.json"
FIREBASE_STORAGE_BUCKET="visa-a05d3.firebasestorage.app"
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
    "requirement_id": "tr_de_all",    # FK to VISA_REQUIREMENT
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
- `POST /api/v1/auth/login` - Login user (returns Firebase token)
- `GET /api/v1/auth/me` - Get current user info

### Users
- `GET /api/v1/users/me` - Get user profile
- `PUT /api/v1/users/me` - Update user profile
- `GET /api/v1/users/me/dashboard` - Get user dashboard with statistics
- `GET /api/v1/users/me/notifications` - Get user notifications
- `POST /api/v1/users/me/notifications/read` - Mark notifications as read

### Applications (Core Logic)
- `POST /api/v1/applications/applications` - Create new application
- `GET /api/v1/applications/applications` - Get user's applications
- `GET /api/v1/applications/applications/{app_id}/tasks` - Get application tasks
- `GET /api/v1/applications/{app_id}` - Get specific application
- `PUT /api/v1/applications/{app_id}` - Update application
- `POST /api/v1/applications/{app_id}/submit` - Submit application for review

### Documents
- `POST /api/v1/docs/task/{task_id}/upload` - Upload document
- `GET /api/v1/docs/task/{task_id}` - Get task documents
- `DELETE /api/v1/docs/{doc_id}` - Delete document

### Visa Requirements
- `GET /api/v1/visa-requirements` - Get visa requirements (with filtering)
- `GET /api/v1/visa-requirements/{req_id}` - Get specific visa requirement
- `GET /api/v1/visa-requirements/search` - Search visa requirements
- `GET /api/v1/visa-requirements/{req_id}/checklist-templates` - Get checklist templates

### Countries
- `GET /api/v1/countries` - Get countries (with filtering)
- `GET /api/v1/countries/{country_code}` - Get specific country
- `GET /api/v1/countries/schengen` - Get Schengen countries

### Task Management
- `GET /api/v1/tasks` - Get user tasks (with filtering)
- `GET /api/v1/tasks/{task_id}` - Get specific task
- `PUT /api/v1/tasks/{task_id}` - Update task
- `GET /api/v1/tasks/statistics` - Get task statistics
- `POST /api/v1/tasks/{task_id}/complete` - Mark task as completed
- `GET /api/v1/tasks/dashboard` - Get comprehensive task dashboard

### Social Media Audit
- `POST /api/v1/social-audits` - Create social media audit
- `GET /api/v1/social-audits` - Get user's social media audits
- `GET /api/v1/social-audits/{audit_id}` - Get specific audit
- `PUT /api/v1/social-audits/{audit_id}` - Update audit
- `DELETE /api/v1/social-audits/{audit_id}` - Delete audit

### AI Features
- `POST /api/v1/ai/analyze-document` - AI document analysis
- `POST /api/v1/ai/visa-recommendation` - AI visa recommendations

### Analytics & Reporting
- `GET /api/v1/analytics/user-stats` - User analytics and statistics
- `GET /api/v1/analytics/application-trends` - Application trends analysis
- `GET /api/v1/analytics/success-rates` - Success rate analytics
- `POST /api/v1/reports/export` - Export user data
- `GET /api/v1/reports/export/{export_id}` - Download exported data
- `GET /api/v1/reports/user-summary` - User summary report

### Integrations
- `POST /api/v1/integrations/embassy-check` - Embassy appointment check
- `GET /api/v1/integrations/visa-status` - Check visa status
- `POST /api/v1/integrations/email-notify` - Email notifications
- `GET /api/v1/integrations/calendar` - Calendar integration

### Support System
- `POST /api/v1/support/tickets` - Create support ticket
- `GET /api/v1/support/tickets` - Get user's support tickets
- `GET /api/v1/support/tickets/{ticket_id}` - Get specific support ticket
- `GET /api/v1/support/faq` - Get frequently asked questions

### Admin
- `GET /api/v1/admin/stats` - Get system statistics
- `GET /api/v1/admin/users` - Get all users
- `GET /api/v1/admin/users/{user_id}` - Get user details
- `GET /api/v1/admin/system-health` - Get system health
- `GET /api/v1/admin/collections` - Get collection info

## 🚀 **New Priority 1 Features**

### **Enhanced Application Management**
- **Update Applications**: Modify application data and status
- **Submit Applications**: Submit completed applications for review with validation
- **Smart Validation**: Ensures all tasks are completed before submission

### **User Dashboard**
- **Comprehensive Overview**: Total applications, active applications, task statistics
- **Progress Tracking**: Completion rates and document upload counts
- **Upcoming Deadlines**: Track application deadlines and status
- **Recent Activity**: Latest applications and progress summary

### **Task Completion**
- **Smart Completion**: Mark tasks as complete with validation
- **Document Verification**: Ensures required documents are uploaded
- **Progress Tracking**: Automatic status updates and completion timestamps

### **Example Usage**

#### **Update Application**
```bash
PUT /api/v1/applications/{app_id}
{
  "status": "DRAFT",
  "ai_filled_form_data": {
    "updated_field": "new_value"
  }
}
```

#### **Submit Application**
```bash
POST /api/v1/applications/{app_id}/submit
{
  "submit_notes": "Ready for review"
}
```

#### **Get User Dashboard**
```bash
GET /api/v1/users/me/dashboard
# Returns comprehensive user statistics and progress
```

#### **Complete Task**
```bash
POST /api/v1/tasks/{task_id}/complete
{
  "completion_notes": "Document uploaded successfully"
}
```

## 🎯 **New Priority 2 Features**

### **Enhanced User Experience**
- **Smart Notifications**: Real-time notifications with read/unread status
- **AI Document Analysis**: Intelligent document validation and recommendations
- **Task Dashboard**: Comprehensive task overview with progress tracking
- **Support System**: Complete ticketing system with FAQ

### **AI-Powered Document Analysis**
- **Intelligent Validation**: AI analyzes uploaded documents for compliance
- **Type-Specific Analysis**: Different analysis for passports, financial docs, academic records
- **Confidence Scoring**: AI provides confidence scores for document quality
- **Smart Recommendations**: Automated suggestions for document improvements

### **Advanced Task Management**
- **Task Dashboard**: Overview of all tasks with statistics and deadlines
- **Application Grouping**: Tasks organized by application with progress tracking
- **Recent Activity**: Timeline of task updates and completions
- **Deadline Tracking**: Upcoming deadlines with priority indicators

### **Comprehensive Support System**
- **Ticket Management**: Create, track, and manage support requests
- **Priority Levels**: Low, medium, high, and urgent priority support
- **Category System**: Organized support by general, technical, billing, feature requests
- **FAQ Integration**: Built-in frequently asked questions

### **Example Usage**

#### **AI Document Analysis**
```bash
POST /api/v1/ai/analyze-document
{
  "task_id": "task-uuid",
  "analysis_type": "passport"
}
```

#### **Get Notifications**
```bash
GET /api/v1/users/me/notifications?unread_only=true
```

#### **Create Support Ticket**
```bash
POST /api/v1/support/tickets
{
  "subject": "Document Upload Issue",
  "description": "Unable to upload passport photo",
  "priority": "high",
  "category": "technical"
}
```

#### **Get Task Dashboard**
```bash
GET /api/v1/tasks/dashboard
# Returns comprehensive task statistics and activity
```

## 🚀 **New Priority 3 Features**

### **Advanced AI Capabilities**
- **Intelligent Visa Recommendations**: AI-powered visa type suggestions based on user profile
- **Smart Analysis**: Type-specific document analysis with confidence scoring
- **Success Probability**: AI calculates success rates for different visa types
- **Alternative Options**: AI suggests alternative visa types and processing methods

### **Comprehensive Analytics**
- **User Statistics**: Detailed analytics on application success rates and trends
- **Application Trends**: Monthly and yearly application pattern analysis
- **Success Rate Analytics**: Success rates by destination and visa type
- **Performance Metrics**: Task completion rates and document approval statistics

### **Embassy Integration**
- **Appointment Checking**: Real-time embassy appointment availability
- **Status Tracking**: Live visa application status updates
- **Requirements Updates**: Current embassy requirements and processing times
- **Calendar Integration**: Automated deadline and appointment tracking

### **Data Export & Reporting**
- **Multi-Format Export**: JSON, CSV, and PDF export options
- **Comprehensive Reports**: Complete user data export with analytics
- **Summary Reports**: Quick overview of user's visa journey
- **Secure Downloads**: Time-limited, secure file access

### **Example Usage**

#### **AI Visa Recommendation**
```bash
POST /api/v1/ai/visa-recommendation
{
  "origin_country": "TR",
  "destination_country": "DE",
  "passport_type": "BORDO",
  "profile_type": "STUDENT",
  "purpose": "study",
  "duration": "2 years"
}
```

#### **Get User Analytics**
```bash
GET /api/v1/analytics/user-stats?period=6months
```

#### **Check Embassy Status**
```bash
POST /api/v1/integrations/embassy-check
{
  "embassy_name": "German Embassy",
  "country_code": "DE",
  "check_type": "appointment"
}
```

#### **Export User Data**
```bash
POST /api/v1/reports/export
{
  "export_type": "all",
  "format": "json",
  "date_range": {
    "start": "2024-01-01",
    "end": "2024-12-31"
  }
}
```

## 🚀 **Deployment Guide**

### **Production Deployment**

**Live API Endpoint**: http://34.3.90.3:8000/

The API is currently deployed and running on a Google Cloud VM instance.

#### **Access the API**
- **Base URL**: `http://34.3.90.3:8000/`
- **Health Check**: `http://34.3.90.3:8000/health`
- **API Endpoints**: `http://34.3.90.3:8000/api/v1/`

#### **Example API Requests**
```bash
# Health check
curl http://34.3.90.3:8000/health

# Get countries
curl http://34.3.90.3:8000/api/v1/countries

# Login
curl -X POST http://34.3.90.3:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "password": "password123"}'
```

### **Docker Deployment**

#### **Local Development**
```bash
# Build and run with Docker Compose
docker-compose up -d --build

# View logs
docker-compose logs -f

# Stop the application
docker-compose down
```

#### **Production Docker**
```bash
# Build the Docker image
docker build -t visa-prep-api .

# Run the container
docker run -d \
  --name visa-prep-api \
  -p 8000:8000 \
  -v $(pwd)/visa-a05d3-firebase-adminsdk-fbsvc-f627f00882.json:/app/visa-a05d3-firebase-adminsdk-fbsvc-f627f00882.json:ro \
  visa-prep-api
```

### **Google Cloud Platform Deployment**

#### **Option 1: Google Cloud VM Instance**

1. **Create a VM Instance**:
   ```bash
   gcloud compute instances create visa-prep-backend \
     --image-family=ubuntu-2004-lts \
     --image-project=ubuntu-os-cloud \
     --machine-type=e2-medium \
     --zone=us-central1-a \
     --tags=http-server,https-server \
     --metadata-from-file startup-script=gcp-startup-script.sh
   ```

2. **Configure Firewall**:
   ```bash
   gcloud compute firewall-rules create allow-visa-prep-api \
     --allow tcp:8000 \
     --source-ranges 0.0.0.0/0 \
     --target-tags http-server
   ```

3. **Access Your Application**:
   - Get the external IP: `gcloud compute instances describe visa-prep-backend --zone=us-central1-a --format='get(networkInterfaces[0].accessConfigs[0].natIP)'`
   - API Documentation: `http://EXTERNAL_IP:8000/docs`

#### **Option 2: Google Cloud Run**

1. **Build and Push Container**:
   ```bash
   # Set your project ID
   export PROJECT_ID=your-project-id
   
   # Build and push
   docker build -t gcr.io/$PROJECT_ID/visa-prep-api .
   docker push gcr.io/$PROJECT_ID/visa-prep-api
   ```

2. **Deploy to Cloud Run**:
   ```bash
   gcloud run deploy visa-prep-api \
     --image gcr.io/$PROJECT_ID/visa-prep-api \
     --platform managed \
     --region us-central1 \
     --allow-unauthenticated \
     --port 8000 \
     --memory 1Gi \
     --cpu 1 \
     --max-instances 10
   ```

#### **Option 3: Google Cloud Build (CI/CD)**

1. **Set up Cloud Build**:
   ```bash
   # Enable Cloud Build API
   gcloud services enable cloudbuild.googleapis.com
   
   # Create build trigger
   gcloud builds triggers create github \
     --repo-name=visa-prep-backend \
     --repo-owner=yourusername \
     --branch-pattern="^main$" \
     --build-config=cloudbuild.yaml
   ```

2. **Automatic Deployment**:
   - Push to main branch triggers automatic build and deployment
   - Uses `cloudbuild.yaml` configuration

### **Environment Configuration**

1. **Copy Environment Template**:
   ```bash
   cp env.example .env
   ```

2. **Update Firebase Configuration**:
   - Replace Firebase service account key
   - Update project ID and credentials
   - Set production security settings

3. **Security Settings**:
   ```bash
   # Generate secret key
   python -c "import secrets; print(secrets.token_urlsafe(32))"
   
   # Update CORS origins for production
   ALLOWED_ORIGINS=["https://yourdomain.com"]
   ```

### **Production Checklist**

- [ ] Firebase service account key configured
- [ ] Environment variables set
- [ ] CORS origins restricted
- [ ] Debug mode disabled
- [ ] SSL/TLS configured (if using custom domain)
- [ ] Monitoring and logging set up
- [ ] Backup strategy implemented
- [ ] Security headers configured

### **Monitoring and Maintenance**

#### **Health Checks**
- Health endpoint: `GET /health`
- API documentation: `GET /docs` (development only)

#### **Logs**
```bash
# Docker logs
docker-compose logs -f

# System logs
journalctl -u visa-prep-api.service -f
```

#### **Updates**
```bash
# Pull latest changes
git pull

# Rebuild and restart
docker-compose up -d --build

# Or restart service
sudo systemctl restart visa-prep-api
```

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