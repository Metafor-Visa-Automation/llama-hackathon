from fastapi import APIRouter, HTTPException, status, Depends, Response
from app.core.firebase import db
from app.models.schemas import (
    DataExportRequest, DataExportResponse
)
from app.services.security import get_current_user, UserInDB
from datetime import datetime, timedelta
from typing import Dict, Any, List
import uuid
import json
import csv
import io

router = APIRouter()


@router.post("/reports/export", response_model=DataExportResponse, status_code=status.HTTP_201_CREATED)
async def export_user_data(
    export_request: DataExportRequest,
    current_user: UserInDB = Depends(get_current_user)
):
    """
    Export user data in various formats
    """
    try:
        export_id = str(uuid.uuid4())
        now = datetime.utcnow()
        expires_at = now + timedelta(hours=24)  # Export expires in 24 hours
        
        # Calculate date range if provided
        start_date = None
        end_date = None
        if export_request.date_range:
            start_date = datetime.fromisoformat(export_request.date_range['start'])
            end_date = datetime.fromisoformat(export_request.date_range['end'])
        
        # Collect data based on export type
        export_data = collect_export_data(
            current_user.uid, 
            export_request.export_type, 
            start_date, 
            end_date
        )
        
        # Generate file based on format
        file_content, file_size, record_count = generate_export_file(
            export_data, 
            export_request.format
        )
        
        # In production, upload to cloud storage and return URL
        file_url = f"https://storage.example.com/exports/{export_id}.{export_request.format}"
        
        # Save export record
        export_doc = {
            "export_id": export_id,
            "user_id": current_user.uid,
            "export_type": export_request.export_type,
            "format": export_request.format,
            "file_url": file_url,
            "file_size": file_size,
            "record_count": record_count,
            "created_at": now,
            "expires_at": expires_at
        }
        
        db.collection('DATA_EXPORT').document(export_id).set(export_doc)
        
        return DataExportResponse(
            export_id=export_id,
            user_id=current_user.uid,
            export_type=export_request.export_type,
            format=export_request.format,
            file_url=file_url,
            file_size=file_size,
            record_count=record_count,
            created_at=now,
            expires_at=expires_at
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to export data: {str(e)}"
        )


def collect_export_data(user_id: str, export_type: str, start_date: datetime = None, end_date: datetime = None) -> Dict[str, Any]:
    """
    Collect user data for export
    """
    export_data = {
        "user_info": {},
        "applications": [],
        "tasks": [],
        "documents": [],
        "notifications": [],
        "support_tickets": [],
        "analytics": {}
    }
    
    # Get user info
    user_doc = db.collection('USER').document(user_id).get()
    if user_doc.exists:
        user_data = user_doc.to_dict()
        # Remove sensitive data
        export_data["user_info"] = {
            "uid": user_data.get('uid'),
            "email": user_data.get('email'),
            "name": user_data.get('name'),
            "surname": user_data.get('surname'),
            "profile_type": user_data.get('profile_type'),
            "passport_type": user_data.get('passport_type'),
            "created_at": user_data.get('created_at'),
            "updated_at": user_data.get('updated_at')
        }
    
    # Get applications
    apps_query = db.collection('APPLICATION').where('user_id', '==', user_id)
    if start_date and end_date:
        apps_query = apps_query.where('created_at', '>=', start_date).where('created_at', '<=', end_date)
    
    for app_doc in apps_query.stream():
        app_data = app_doc.to_dict()
        export_data["applications"].append({
            "app_id": app_data.get('app_id'),
            "requirement_id": app_data.get('requirement_id'),
            "status": app_data.get('status'),
            "created_at": app_data.get('created_at'),
            "updated_at": app_data.get('updated_at'),
            "ai_filled_form_data": app_data.get('ai_filled_form_data', {})
        })
    
    # Get tasks
    tasks_query = db.collection('TASK').where('user_id', '==', user_id)
    if start_date and end_date:
        tasks_query = tasks_query.where('created_at', '>=', start_date).where('created_at', '<=', end_date)
    
    for task_doc in tasks_query.stream():
        task_data = task_doc.to_dict()
        export_data["tasks"].append({
            "task_id": task_data.get('task_id'),
            "application_id": task_data.get('application_id'),
            "title": task_data.get('title'),
            "description": task_data.get('description'),
            "status": task_data.get('status'),
            "created_at": task_data.get('created_at'),
            "updated_at": task_data.get('updated_at')
        })
    
    # Get documents
    docs_query = db.collection('USER_DOCUMENT').where('user_id', '==', user_id)
    if start_date and end_date:
        docs_query = docs_query.where('created_at', '>=', start_date).where('created_at', '<=', end_date)
    
    for doc_doc in docs_query.stream():
        doc_data = doc_doc.to_dict()
        export_data["documents"].append({
            "doc_id": doc_data.get('doc_id'),
            "task_id": doc_data.get('task_id'),
            "storage_path": doc_data.get('storage_path'),
            "status": doc_data.get('status'),
            "created_at": doc_data.get('created_at'),
            "updated_at": doc_data.get('updated_at')
        })
    
    # Get notifications
    notifications_query = db.collection('NOTIFICATION').where('user_id', '==', user_id)
    if start_date and end_date:
        notifications_query = notifications_query.where('created_at', '>=', start_date).where('created_at', '<=', end_date)
    
    for notif_doc in notifications_query.stream():
        notif_data = notif_doc.to_dict()
        export_data["notifications"].append({
            "notification_id": notif_data.get('notification_id'),
            "title": notif_data.get('title'),
            "message": notif_data.get('message'),
            "type": notif_data.get('type'),
            "is_read": notif_data.get('is_read'),
            "created_at": notif_data.get('created_at')
        })
    
    # Get support tickets
    tickets_query = db.collection('SUPPORT_TICKET').where('user_id', '==', user_id)
    if start_date and end_date:
        tickets_query = tickets_query.where('created_at', '>=', start_date).where('created_at', '<=', end_date)
    
    for ticket_doc in tickets_query.stream():
        ticket_data = ticket_doc.to_dict()
        export_data["support_tickets"].append({
            "ticket_id": ticket_data.get('ticket_id'),
            "subject": ticket_data.get('subject'),
            "description": ticket_data.get('description'),
            "priority": ticket_data.get('priority'),
            "category": ticket_data.get('category'),
            "status": ticket_data.get('status'),
            "created_at": ticket_data.get('created_at'),
            "updated_at": ticket_data.get('updated_at')
        })
    
    # Calculate basic analytics
    export_data["analytics"] = {
        "total_applications": len(export_data["applications"]),
        "total_tasks": len(export_data["tasks"]),
        "total_documents": len(export_data["documents"]),
        "total_notifications": len(export_data["notifications"]),
        "total_support_tickets": len(export_data["support_tickets"]),
        "export_generated_at": datetime.utcnow().isoformat()
    }
    
    return export_data


def generate_export_file(export_data: Dict[str, Any], format: str) -> tuple:
    """
    Generate export file in specified format
    """
    if format.lower() == "json":
        file_content = json.dumps(export_data, indent=2, default=str)
        file_size = len(file_content.encode('utf-8'))
        record_count = sum(len(v) for v in export_data.values() if isinstance(v, list))
        return file_content, file_size, record_count
    
    elif format.lower() == "csv":
        # Create CSV content
        csv_buffer = io.StringIO()
        writer = csv.writer(csv_buffer)
        
        # Write applications
        if export_data["applications"]:
            writer.writerow(["Type", "ID", "Status", "Created At", "Updated At"])
            for app in export_data["applications"]:
                writer.writerow([
                    "Application",
                    app["app_id"],
                    app["status"],
                    app["created_at"],
                    app["updated_at"]
                ])
        
        # Write tasks
        if export_data["tasks"]:
            writer.writerow(["Type", "ID", "Title", "Status", "Created At", "Updated At"])
            for task in export_data["tasks"]:
                writer.writerow([
                    "Task",
                    task["task_id"],
                    task["title"],
                    task["status"],
                    task["created_at"],
                    task["updated_at"]
                ])
        
        file_content = csv_buffer.getvalue()
        file_size = len(file_content.encode('utf-8'))
        record_count = len(export_data["applications"]) + len(export_data["tasks"])
        return file_content, file_size, record_count
    
    elif format.lower() == "pdf":
        # In production, use a PDF library like ReportLab
        # For now, return a simple text representation
        pdf_content = f"""
VisaPrep AI Data Export Report
Generated: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')}

User Information:
- Name: {export_data['user_info'].get('name', 'N/A')} {export_data['user_info'].get('surname', 'N/A')}
- Email: {export_data['user_info'].get('email', 'N/A')}
- Profile Type: {export_data['user_info'].get('profile_type', 'N/A')}

Summary:
- Total Applications: {export_data['analytics']['total_applications']}
- Total Tasks: {export_data['analytics']['total_tasks']}
- Total Documents: {export_data['analytics']['total_documents']}
- Total Notifications: {export_data['analytics']['total_notifications']}
- Total Support Tickets: {export_data['analytics']['total_support_tickets']}

Applications:
"""
        for app in export_data["applications"]:
            pdf_content += f"- {app['app_id']}: {app['status']} ({app['created_at']})\n"
        
        pdf_content += "\nTasks:\n"
        for task in export_data["tasks"]:
            pdf_content += f"- {task['task_id']}: {task['title']} ({task['status']})\n"
        
        file_content = pdf_content
        file_size = len(file_content.encode('utf-8'))
        record_count = export_data['analytics']['total_applications'] + export_data['analytics']['total_tasks']
        return file_content, file_size, record_count
    
    else:
        raise ValueError(f"Unsupported export format: {format}")


@router.get("/reports/export/{export_id}")
async def download_export(
    export_id: str,
    current_user: UserInDB = Depends(get_current_user)
):
    """
    Download exported data file
    """
    try:
        # Get export record
        export_doc = db.collection('DATA_EXPORT').document(export_id).get()
        if not export_doc.exists:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Export not found"
            )
        
        export_data = export_doc.to_dict()
        
        # Verify ownership
        if export_data['user_id'] != current_user.uid:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied: Export does not belong to current user"
            )
        
        # Check if export has expired
        expires_at = export_data['expires_at']
        if isinstance(expires_at, str):
            expires_at = datetime.fromisoformat(expires_at.replace('Z', '+00:00'))
        
        if datetime.utcnow() > expires_at:
            raise HTTPException(
                status_code=status.HTTP_410_GONE,
                detail="Export has expired"
            )
        
        # In production, download from cloud storage
        # For now, return the export info
        return {
            "export_id": export_id,
            "file_url": export_data['file_url'],
            "file_size": export_data['file_size'],
            "format": export_data['format'],
            "expires_at": export_data['expires_at'],
            "download_url": f"/api/v1/reports/download/{export_id}"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get export: {str(e)}"
        )


@router.get("/reports/user-summary")
async def get_user_summary_report(
    current_user: UserInDB = Depends(get_current_user)
):
    """
    Get a summary report of user's visa application journey
    """
    try:
        # Get user's data
        applications_query = db.collection('APPLICATION').where('user_id', '==', current_user.uid).stream()
        tasks_query = db.collection('TASK').where('user_id', '==', current_user.uid).stream()
        docs_query = db.collection('USER_DOCUMENT').where('user_id', '==', current_user.uid).stream()
        
        applications = [app.to_dict() for app in applications_query]
        tasks = [task.to_dict() for task in tasks_query]
        documents = [doc.to_dict() for doc in docs_query]
        
        # Calculate summary statistics
        total_applications = len(applications)
        successful_applications = len([app for app in applications if app['status'] == 'APPROVED'])
        success_rate = (successful_applications / total_applications * 100) if total_applications > 0 else 0
        
        total_tasks = len(tasks)
        completed_tasks = len([task for task in tasks if task['status'] == 'DONE'])
        completion_rate = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
        
        total_documents = len(documents)
        approved_documents = len([doc for doc in documents if doc['status'] == 'APPROVED'])
        approval_rate = (approved_documents / total_documents * 100) if total_documents > 0 else 0
        
        # Get most common destinations
        destinations = [app['requirement_id'].split('_')[1] for app in applications if '_' in app['requirement_id']]
        from collections import Counter
        destination_counts = Counter(destinations)
        top_destinations = [{"country": country, "count": count} for country, count in destination_counts.most_common(3)]
        
        return {
            "user_id": current_user.uid,
            "generated_at": datetime.utcnow().isoformat(),
            "summary": {
                "total_applications": total_applications,
                "successful_applications": successful_applications,
                "success_rate": round(success_rate, 2),
                "total_tasks": total_tasks,
                "completed_tasks": completed_tasks,
                "completion_rate": round(completion_rate, 2),
                "total_documents": total_documents,
                "approved_documents": approved_documents,
                "approval_rate": round(approval_rate, 2)
            },
            "top_destinations": top_destinations,
            "recent_activity": {
                "last_application": applications[-1]['created_at'] if applications else None,
                "last_task_completion": max([task['updated_at'] for task in tasks if task['status'] == 'DONE'], default=None),
                "last_document_upload": documents[-1]['created_at'] if documents else None
            }
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate summary report: {str(e)}"
        )
