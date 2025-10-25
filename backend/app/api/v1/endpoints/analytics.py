from fastapi import APIRouter, HTTPException, status, Depends, Query
from app.core.firebase import db
from app.models.schemas import UserAnalyticsResponse
from app.services.security import get_current_user, UserInDB
from datetime import datetime, timedelta
from typing import List, Dict, Any
from collections import Counter

router = APIRouter()


@router.get("/analytics/user-stats", response_model=UserAnalyticsResponse)
async def get_user_analytics(
    current_user: UserInDB = Depends(get_current_user),
    period: str = Query("6months", description="Analytics period: 1month, 3months, 6months, 1year")
):
    """
    Get comprehensive user analytics and statistics
    """
    try:
        # Calculate date range based on period
        now = datetime.utcnow()
        if period == "1month":
            start_date = now - timedelta(days=30)
        elif period == "3months":
            start_date = now - timedelta(days=90)
        elif period == "6months":
            start_date = now - timedelta(days=180)
        elif period == "1year":
            start_date = now - timedelta(days=365)
        else:
            start_date = now - timedelta(days=180)  # Default to 6 months
        
        # Get user's applications
        applications_query = db.collection('APPLICATION').where(
            'user_id', '==', current_user.uid
        ).where('created_at', '>=', start_date).stream()
        
        applications = []
        for app_doc in applications_query:
            app_data = app_doc.to_dict()
            applications.append(app_data)
        
        # Get user's tasks
        tasks_query = db.collection('TASK').where(
            'user_id', '==', current_user.uid
        ).where('created_at', '>=', start_date).stream()
        
        tasks = []
        for task_doc in tasks_query:
            task_data = task_doc.to_dict()
            tasks.append(task_data)
        
        # Get user's documents
        docs_query = db.collection('USER_DOCUMENT').where(
            'user_id', '==', current_user.uid
        ).where('created_at', '>=', start_date).stream()
        
        documents = []
        for doc_doc in docs_query:
            doc_data = doc_doc.to_dict()
            documents.append(doc_data)
        
        # Calculate basic statistics
        total_applications = len(applications)
        successful_applications = len([app for app in applications if app['status'] == 'APPROVED'])
        success_rate = (successful_applications / total_applications * 100) if total_applications > 0 else 0
        
        # Calculate average processing time (simplified)
        processing_times = []
        for app in applications:
            if app['status'] in ['APPROVED', 'REJECTED']:
                # Simulate processing time calculation
                created_at = app['created_at']
                if isinstance(created_at, str):
                    created_at = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                
                processing_days = (now - created_at).days
                processing_times.append(processing_days)
        
        average_processing_time = sum(processing_times) / len(processing_times) if processing_times else 0
        
        # Most common destinations
        destinations = [app['requirement_id'].split('_')[1] for app in applications if '_' in app['requirement_id']]
        destination_counts = Counter(destinations)
        most_common_destinations = [
            {"country": country, "count": count} 
            for country, count in destination_counts.most_common(5)
        ]
        
        # Application trends (by month)
        application_trends = {}
        for app in applications:
            month_key = app['created_at'].strftime('%Y-%m') if isinstance(app['created_at'], datetime) else app['created_at'][:7]
            application_trends[month_key] = application_trends.get(month_key, 0) + 1
        
        # Task completion statistics
        task_completion_stats = {
            "total_tasks": len(tasks),
            "completed_tasks": len([t for t in tasks if t['status'] == 'DONE']),
            "pending_tasks": len([t for t in tasks if t['status'] == 'PENDING']),
            "in_progress_tasks": len([t for t in tasks if t['status'] == 'IN_PROGRESS']),
            "rejected_tasks": len([t for t in tasks if t['status'] == 'REJECTED']),
            "completion_rate": 0
        }
        
        if task_completion_stats["total_tasks"] > 0:
            task_completion_stats["completion_rate"] = round(
                (task_completion_stats["completed_tasks"] / task_completion_stats["total_tasks"]) * 100, 2
            )
        
        # Document upload statistics
        document_upload_stats = {
            "total_documents": len(documents),
            "approved_documents": len([d for d in documents if d['status'] == 'APPROVED']),
            "pending_documents": len([d for d in documents if d['status'] == 'PENDING_VALIDATION']),
            "rejected_documents": len([d for d in documents if d['status'] == 'REJECTED']),
            "approval_rate": 0
        }
        
        if document_upload_stats["total_documents"] > 0:
            document_upload_stats["approval_rate"] = round(
                (document_upload_stats["approved_documents"] / document_upload_stats["total_documents"]) * 100, 2
            )
        
        # Monthly activity breakdown
        monthly_activity = []
        current_month = start_date.replace(day=1)
        
        while current_month <= now:
            month_key = current_month.strftime('%Y-%m')
            month_apps = len([app for app in applications if app['created_at'].strftime('%Y-%m') == month_key])
            month_tasks = len([task for task in tasks if task['created_at'].strftime('%Y-%m') == month_key])
            month_docs = len([doc for doc in documents if doc['created_at'].strftime('%Y-%m') == month_key])
            
            monthly_activity.append({
                "month": month_key,
                "applications": month_apps,
                "tasks_completed": month_tasks,
                "documents_uploaded": month_docs
            })
            
            # Move to next month
            if current_month.month == 12:
                current_month = current_month.replace(year=current_month.year + 1, month=1)
            else:
                current_month = current_month.replace(month=current_month.month + 1)
        
        return UserAnalyticsResponse(
            user_id=current_user.uid,
            total_applications=total_applications,
            successful_applications=successful_applications,
            success_rate=round(success_rate, 2),
            average_processing_time=round(average_processing_time, 1),
            most_common_destinations=most_common_destinations,
            application_trends=application_trends,
            task_completion_stats=task_completion_stats,
            document_upload_stats=document_upload_stats,
            monthly_activity=monthly_activity
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch user analytics: {str(e)}"
        )


@router.get("/analytics/application-trends")
async def get_application_trends(
    current_user: UserInDB = Depends(get_current_user),
    period: str = Query("6months", description="Trend period")
):
    """
    Get detailed application trends and patterns
    """
    try:
        # Calculate date range
        now = datetime.utcnow()
        if period == "1month":
            start_date = now - timedelta(days=30)
        elif period == "3months":
            start_date = now - timedelta(days=90)
        elif period == "6months":
            start_date = now - timedelta(days=180)
        elif period == "1year":
            start_date = now - timedelta(days=365)
        else:
            start_date = now - timedelta(days=180)
        
        # Get applications in date range
        applications_query = db.collection('APPLICATION').where(
            'user_id', '==', current_user.uid
        ).where('created_at', '>=', start_date).stream()
        
        applications = []
        for app_doc in applications_query:
            app_data = app_doc.to_dict()
            applications.append(app_data)
        
        # Analyze trends
        status_trends = {}
        destination_trends = {}
        monthly_trends = {}
        
        for app in applications:
            # Status trends
            status = app['status']
            status_trends[status] = status_trends.get(status, 0) + 1
            
            # Destination trends
            if '_' in app['requirement_id']:
                destination = app['requirement_id'].split('_')[1]
                destination_trends[destination] = destination_trends.get(destination, 0) + 1
            
            # Monthly trends
            month_key = app['created_at'].strftime('%Y-%m') if isinstance(app['created_at'], datetime) else app['created_at'][:7]
            if month_key not in monthly_trends:
                monthly_trends[month_key] = {"total": 0, "approved": 0, "rejected": 0, "pending": 0}
            
            monthly_trends[month_key]["total"] += 1
            if status == "APPROVED":
                monthly_trends[month_key]["approved"] += 1
            elif status == "REJECTED":
                monthly_trends[month_key]["rejected"] += 1
            else:
                monthly_trends[month_key]["pending"] += 1
        
        return {
            "period": period,
            "total_applications": len(applications),
            "status_breakdown": status_trends,
            "destination_breakdown": destination_trends,
            "monthly_trends": monthly_trends,
            "success_rate": round((status_trends.get('APPROVED', 0) / len(applications)) * 100, 2) if applications else 0
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch application trends: {str(e)}"
        )


@router.get("/analytics/success-rates")
async def get_success_rates(
    current_user: UserInDB = Depends(get_current_user)
):
    """
    Get success rate analytics by destination and visa type
    """
    try:
        # Get all user applications
        applications_query = db.collection('APPLICATION').where(
            'user_id', '==', current_user.uid
        ).stream()
        
        applications = []
        for app_doc in applications_query:
            app_data = app_doc.to_dict()
            applications.append(app_data)
        
        # Calculate success rates by destination
        destination_stats = {}
        visa_type_stats = {}
        
        for app in applications:
            # Destination analysis
            if '_' in app['requirement_id']:
                destination = app['requirement_id'].split('_')[1]
                if destination not in destination_stats:
                    destination_stats[destination] = {"total": 0, "approved": 0, "rejected": 0}
                
                destination_stats[destination]["total"] += 1
                if app['status'] == "APPROVED":
                    destination_stats[destination]["approved"] += 1
                elif app['status'] == "REJECTED":
                    destination_stats[destination]["rejected"] += 1
            
            # Visa type analysis (simplified)
            visa_type = "General"
            if "student" in app['requirement_id'].lower():
                visa_type = "Student"
            elif "work" in app['requirement_id'].lower():
                visa_type = "Work"
            elif "tourist" in app['requirement_id'].lower():
                visa_type = "Tourist"
            
            if visa_type not in visa_type_stats:
                visa_type_stats[visa_type] = {"total": 0, "approved": 0, "rejected": 0}
            
            visa_type_stats[visa_type]["total"] += 1
            if app['status'] == "APPROVED":
                visa_type_stats[visa_type]["approved"] += 1
            elif app['status'] == "REJECTED":
                visa_type_stats[visa_type]["rejected"] += 1
        
        # Calculate success rates
        destination_success_rates = {}
        for dest, stats in destination_stats.items():
            if stats["total"] > 0:
                destination_success_rates[dest] = {
                    "total_applications": stats["total"],
                    "success_rate": round((stats["approved"] / stats["total"]) * 100, 2),
                    "rejection_rate": round((stats["rejected"] / stats["total"]) * 100, 2)
                }
        
        visa_type_success_rates = {}
        for visa_type, stats in visa_type_stats.items():
            if stats["total"] > 0:
                visa_type_success_rates[visa_type] = {
                    "total_applications": stats["total"],
                    "success_rate": round((stats["approved"] / stats["total"]) * 100, 2),
                    "rejection_rate": round((stats["rejected"] / stats["total"]) * 100, 2)
                }
        
        return {
            "overall_success_rate": round((len([app for app in applications if app['status'] == 'APPROVED']) / len(applications)) * 100, 2) if applications else 0,
            "destination_success_rates": destination_success_rates,
            "visa_type_success_rates": visa_type_success_rates,
            "total_applications": len(applications)
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch success rates: {str(e)}"
        )
