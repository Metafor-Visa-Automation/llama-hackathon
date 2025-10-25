# Firebase Collections Setup Guide

This guide explains how to set up Firebase collections according to the ER diagram for the visa application system.

## Prerequisites

1. **Firebase Project**: Ensure you have a Firebase project set up
2. **Service Account Key**: Download the Firebase service account key file
3. **Python Dependencies**: Install required Python packages

## Quick Setup

### 1. Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 2. Place Firebase Service Account Key

Place your Firebase service account key file in the `backend` directory with the name:
```
visa-a05d3-firebase-adminsdk-fbsvc-f627f00882.json
```

### 3. Run Setup Script

```bash
python setup_firebase.py
```

The script will guide you through:
- Initializing new collections (for fresh setup)
- Migrating existing collections (for existing data)
- Both (initialize then migrate)

## Manual Setup

### Option 1: Fresh Installation

If you're setting up Firebase collections for the first time:

```bash
python firebase_init.py
```

This will:
- Create all required collections
- Populate static data (countries, visa requirements, templates)
- Create sample user and team data

### Option 2: Migration from Existing Data

If you have existing data that needs to be migrated:

```bash
python firebase_migration.py
```

This will:
- Migrate existing collections to new structure
- Update field names and add new fields
- Clean up old collection names

## Collection Structure

The setup creates the following collections:

### Main Collections
- `users` - User profiles and authentication data
- `teams` - Team management for collaborative applications
- `applications` - Visa applications with progress tracking
- `user_documents` - Document management with OCR results
- `tasks` - Individual tasks for applications
- `countries` - Country information and Schengen membership
- `visa_requirements` - Visa requirements for different countries
- `notifications` - User notifications and system messages

### Subcollections
- `visa_requirements/{req_id}/checklist_templates` - Document templates for specific visa requirements

## Sample Data Included

### Countries
- Turkey, Germany, France, Italy, Spain, Netherlands, Austria, Belgium, Switzerland, Andorra, USA, UK
- Schengen membership flags

### Visa Requirements
- Turkey → Germany (Business)
- Turkey → France (Tourism)
- Turkey → USA (Business)

### Checklist Templates
- Passport validation
- Bank statement requirements
- Travel insurance
- Hotel reservations
- Employment letters
- Flight reservations

## Verification

After running the setup, verify in Firebase Console:

1. **Collections**: Check that all collections are created
2. **Documents**: Verify sample data is populated
3. **Subcollections**: Check checklist templates under visa requirements
4. **Indexes**: Ensure composite indexes are created

## Security Rules

After setup, configure Firestore security rules:

```javascript
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    // Users can only access their own data
    match /users/{userId} {
      allow read, write: if request.auth != null && request.auth.uid == userId;
    }
    
    // Team members can access team data
    match /teams/{teamId} {
      allow read, write: if request.auth != null && 
        (resource.data.owner_id == request.auth.uid || 
         request.auth.uid in resource.data.members);
    }
    
    // Applications accessible by user or team members
    match /applications/{appId} {
      allow read, write: if request.auth != null && 
        (resource.data.user_id == request.auth.uid ||
         (resource.data.team_id != null && 
          exists(/databases/$(database)/documents/teams/$(resource.data.team_id)) &&
          request.auth.uid in get(/databases/$(database)/documents/teams/$(resource.data.team_id)).data.members));
    }
    
    // User documents accessible by owner
    match /user_documents/{docId} {
      allow read, write: if request.auth != null && 
        resource.data.user_id == request.auth.uid;
    }
    
    // Tasks accessible by assigned user
    match /tasks/{taskId} {
      allow read, write: if request.auth != null && 
        resource.data.user_id == request.auth.uid;
    }
    
    // Notifications accessible by recipient
    match /notifications/{notificationId} {
      allow read, write: if request.auth != null && 
        resource.data.user_id == request.auth.uid;
    }
    
    // Public read access for static data
    match /countries/{countryId} {
      allow read: if true;
    }
    
    match /visa_requirements/{reqId} {
      allow read: if true;
    }
    
    match /visa_requirements/{reqId}/checklist_templates/{templateId} {
      allow read: if true;
    }
  }
}
```

## Indexes

Create the following composite indexes in Firebase Console:

### Applications
- `user_id` (Ascending), `status` (Ascending), `created_at` (Descending)
- `team_id` (Ascending), `status` (Ascending), `created_at` (Descending)

### User Documents
- `user_id` (Ascending), `doc_type` (Ascending), `uploaded_at` (Descending)
- `user_id` (Ascending), `status` (Ascending), `uploaded_at` (Descending)

### Tasks
- `user_id` (Ascending), `status` (Ascending), `created_at` (Descending)
- `application_id` (Ascending), `status` (Ascending), `created_at` (Descending)

### Notifications
- `user_id` (Ascending), `is_read` (Ascending), `created_at` (Descending)
- `user_id` (Ascending), `type` (Ascending), `created_at` (Descending)

### Visa Requirements
- `origin_country` (Ascending), `destination_code` (Ascending)

## Testing

After setup, test the API endpoints:

```bash
# Test countries endpoint
curl -X GET "http://localhost:8000/api/v1/countries"

# Test visa requirements
curl -X GET "http://localhost:8000/api/v1/visa-requirements"

# Test user creation (with authentication)
curl -X POST "http://localhost:8000/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "password": "password123", "name": "Test", "surname": "User"}'
```

## Troubleshooting

### Common Issues

1. **Firebase Key Not Found**
   - Ensure the service account key file is in the backend directory
   - Check the filename matches exactly

2. **Permission Denied**
   - Verify Firebase project permissions
   - Check service account has Firestore access

3. **Collection Already Exists**
   - Use migration script instead of initialization
   - Or delete existing collections first

4. **Index Errors**
   - Create required composite indexes in Firebase Console
   - Wait for indexes to build (can take time)

### Logs

Check the console output for detailed error messages. The scripts provide verbose logging to help identify issues.

## Next Steps

After successful setup:

1. **Configure Authentication**: Set up Firebase Authentication
2. **Test API Endpoints**: Verify all endpoints work correctly
3. **Set Up Monitoring**: Configure Firebase monitoring and alerts
4. **Backup Strategy**: Implement regular backups
5. **Performance Optimization**: Monitor and optimize queries

## Support

For issues or questions:
1. Check Firebase Console for errors
2. Review API logs
3. Verify collection structure matches documentation
4. Test with sample data first
