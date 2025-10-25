from fastapi import APIRouter, HTTPException, status, Depends
from app.core.firebase import db
from app.models.schemas import (
    EmbassyCheckRequest, EmbassyCheckResponse
)
from app.services.security import get_current_user, UserInDB
from datetime import datetime, timedelta
import uuid

router = APIRouter()


@router.post("/integrations/embassy-check", response_model=EmbassyCheckResponse, status_code=status.HTTP_201_CREATED)
async def check_embassy_status(
    embassy_request: EmbassyCheckRequest,
    current_user: UserInDB = Depends(get_current_user)
):
    """
    Check embassy appointment availability and requirements
    """
    try:
        check_id = str(uuid.uuid4())
        now = datetime.utcnow()
        
        # Simulate embassy check (in production, integrate with embassy APIs)
        embassy_data = simulate_embassy_check(embassy_request)
        
        embassy_check_doc = {
            "check_id": check_id,
            "user_id": current_user.uid,
            "embassy_name": embassy_request.embassy_name,
            "country_code": embassy_request.country_code,
            "check_type": embassy_request.check_type,
            "status": embassy_data['status'],
            "available_dates": embassy_data['available_dates'],
            "requirements": embassy_data['requirements'],
            "processing_time": embassy_data['processing_time'],
            "contact_info": embassy_data['contact_info'],
            "last_updated": now
        }
        
        # Save embassy check to Firestore
        db.collection('EMBASSY_CHECK').document(check_id).set(embassy_check_doc)
        
        return EmbassyCheckResponse(
            check_id=check_id,
            embassy_name=embassy_request.embassy_name,
            country_code=embassy_request.country_code,
            check_type=embassy_request.check_type,
            status=embassy_data['status'],
            available_dates=embassy_data['available_dates'],
            requirements=embassy_data['requirements'],
            processing_time=embassy_data['processing_time'],
            contact_info=embassy_data['contact_info'],
            last_updated=now
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to check embassy status: {str(e)}"
        )


def simulate_embassy_check(request: EmbassyCheckRequest) -> dict:
    """
    Simulate embassy check
    In production, this would integrate with embassy APIs or web scraping
    """
    embassy_name = request.embassy_name.lower()
    country_code = request.country_code.upper()
    check_type = request.check_type.lower()
    
    # Simulate different embassy responses based on country
    if country_code in ['DE', 'FR', 'IT', 'ES', 'NL']:  # Schengen countries
        if check_type == "appointment":
            available_dates = generate_available_dates(7, 14)  # Next 7-14 days
            status = "appointments_available"
            processing_time = "2-4 weeks"
        elif check_type == "status":
            available_dates = []
            status = "processing_normal"
            processing_time = "2-4 weeks"
        else:  # requirements
            available_dates = []
            status = "requirements_updated"
            processing_time = "2-4 weeks"
        
        requirements = [
            "Valid passport with at least 6 months validity",
            "Completed visa application form",
            "Recent passport-sized photographs",
            "Proof of financial means",
            "Travel insurance",
            "Accommodation proof"
        ]
        
        contact_info = {
            "phone": "+49 30 12345678",
            "email": f"visa@{embassy_name}.gov",
            "website": f"https://{embassy_name}.gov/visa",
            "address": f"{embassy_name.title()} Embassy, Visa Section"
        }
    
    elif country_code in ['US', 'CA', 'AU', 'GB']:  # English-speaking countries
        if check_type == "appointment":
            available_dates = generate_available_dates(14, 30)  # Next 14-30 days
            status = "appointments_limited"
            processing_time = "4-8 weeks"
        elif check_type == "status":
            available_dates = []
            status = "processing_delayed"
            processing_time = "4-8 weeks"
        else:
            available_dates = []
            status = "requirements_updated"
            processing_time = "4-8 weeks"
        
        requirements = [
            "Valid passport with at least 6 months validity",
            "Completed visa application form",
            "Recent passport-sized photographs",
            "Proof of financial means",
            "Travel itinerary",
            "Purpose of visit documentation"
        ]
        
        contact_info = {
            "phone": "+1 555 1234567",
            "email": f"visa@{embassy_name}.gov",
            "website": f"https://{embassy_name}.gov/visa",
            "address": f"{embassy_name.title()} Embassy, Visa Section"
        }
    
    else:  # Other countries
        if check_type == "appointment":
            available_dates = generate_available_dates(3, 7)  # Next 3-7 days
            status = "appointments_available"
            processing_time = "1-3 weeks"
        elif check_type == "status":
            available_dates = []
            status = "processing_normal"
            processing_time = "1-3 weeks"
        else:
            available_dates = []
            status = "requirements_updated"
            processing_time = "1-3 weeks"
        
        requirements = [
            "Valid passport with at least 6 months validity",
            "Completed visa application form",
            "Recent passport-sized photographs",
            "Proof of financial means"
        ]
        
        contact_info = {
            "phone": "+90 312 1234567",
            "email": f"visa@{embassy_name}.gov",
            "website": f"https://{embassy_name}.gov/visa",
            "address": f"{embassy_name.title()} Embassy, Visa Section"
        }
    
    return {
        "status": status,
        "available_dates": available_dates,
        "requirements": requirements,
        "processing_time": processing_time,
        "contact_info": contact_info
    }


def generate_available_dates(min_days: int, max_days: int) -> list:
    """
    Generate simulated available appointment dates
    """
    from datetime import datetime, timedelta
    import random
    
    dates = []
    start_date = datetime.now() + timedelta(days=min_days)
    end_date = datetime.now() + timedelta(days=max_days)
    
    # Generate 3-5 random available dates
    num_dates = random.randint(3, 5)
    for _ in range(num_dates):
        random_days = random.randint(min_days, max_days)
        date = datetime.now() + timedelta(days=random_days)
        dates.append(date.strftime('%Y-%m-%d'))
    
    return sorted(dates)


@router.get("/integrations/visa-status")
async def check_visa_status(
    application_id: str,
    current_user: UserInDB = Depends(get_current_user)
):
    """
    Check visa application status with embassy
    """
    try:
        # Verify application belongs to user
        app_doc = db.collection('APPLICATION').document(application_id).get()
        if not app_doc.exists:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Application not found"
            )
        
        app_data = app_doc.to_dict()
        if app_data['user_id'] != current_user.uid:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied: Application does not belong to current user"
            )
        
        # Simulate visa status check
        status_info = simulate_visa_status_check(app_data)
        
        return {
            "application_id": application_id,
            "current_status": app_data['status'],
            "embassy_status": status_info['embassy_status'],
            "last_updated": status_info['last_updated'],
            "estimated_completion": status_info['estimated_completion'],
            "notes": status_info['notes']
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to check visa status: {str(e)}"
        )


def simulate_visa_status_check(app_data: dict) -> dict:
    """
    Simulate visa status check with embassy
    """
    current_status = app_data['status']
    
    if current_status == 'SUBMITTED':
        embassy_status = 'under_review'
        estimated_completion = '2-4 weeks'
        notes = 'Application is being reviewed by embassy officials'
    elif current_status == 'UNDER_REVIEW':
        embassy_status = 'processing'
        estimated_completion = '1-2 weeks'
        notes = 'Documents are being verified and processed'
    elif current_status == 'APPROVED':
        embassy_status = 'approved'
        estimated_completion = 'Ready for collection'
        notes = 'Visa has been approved and is ready for collection'
    elif current_status == 'REJECTED':
        embassy_status = 'rejected'
        estimated_completion = 'N/A'
        notes = 'Application was rejected. Check embassy for details'
    else:
        embassy_status = 'pending'
        estimated_completion = 'TBD'
        notes = 'Application is pending submission'
    
    return {
        "embassy_status": embassy_status,
        "last_updated": datetime.utcnow().isoformat(),
        "estimated_completion": estimated_completion,
        "notes": notes
    }


@router.post("/integrations/email-notify")
async def send_email_notification(
    notification_data: dict,
    current_user: UserInDB = Depends(get_current_user)
):
    """
    Send email notification (simulated)
    """
    try:
        # Simulate email sending
        email_info = {
            "recipient": current_user.email,
            "subject": notification_data.get('subject', 'VisaPrep AI Notification'),
            "message": notification_data.get('message', ''),
            "sent_at": datetime.utcnow().isoformat(),
            "status": "sent"
        }
        
        # In production, integrate with email service (SendGrid, AWS SES, etc.)
        print(f"Email sent to {current_user.email}: {notification_data.get('subject')}")
        
        return {
            "message": "Email notification sent successfully",
            "email_info": email_info
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to send email notification: {str(e)}"
        )


@router.get("/integrations/calendar")
async def get_calendar_integration(
    current_user: UserInDB = Depends(get_current_user)
):
    """
    Get calendar integration data for appointments and deadlines
    """
    try:
        # Get user's upcoming deadlines and appointments
        now = datetime.utcnow()
        
        # Get applications with deadlines
        applications_query = db.collection('APPLICATION').where(
            'user_id', '==', current_user.uid
        ).where('status', 'in', ['SUBMITTED', 'UNDER_REVIEW']).stream()
        
        calendar_events = []
        
        for app_doc in applications_query:
            app_data = app_doc.to_dict()
            
            # Calculate estimated deadline (30 days from submission)
            if app_data['status'] == 'SUBMITTED':
                deadline = app_data['created_at'] + timedelta(days=30)
                if deadline > now:
                    calendar_events.append({
                        "id": f"deadline_{app_data['app_id']}",
                        "title": f"Visa Decision Deadline - {app_data['requirement_id']}",
                        "date": deadline.isoformat(),
                        "type": "deadline",
                        "description": f"Expected decision for application {app_data['app_id']}"
                    })
        
        # Get embassy checks with appointments
        embassy_checks_query = db.collection('EMBASSY_CHECK').where(
            'user_id', '==', current_user.uid
        ).stream()
        
        for check_doc in embassy_checks_query:
            check_data = check_doc.to_dict()
            
            for date_str in check_data.get('available_dates', []):
                try:
                    appointment_date = datetime.fromisoformat(date_str)
                    if appointment_date > now:
                        calendar_events.append({
                            "id": f"appointment_{check_data['check_id']}_{date_str}",
                            "title": f"Embassy Appointment - {check_data['embassy_name']}",
                            "date": appointment_date.isoformat(),
                            "type": "appointment",
                            "description": f"Available appointment at {check_data['embassy_name']}"
                        })
                except ValueError:
                    continue
        
        # Sort events by date
        calendar_events.sort(key=lambda x: x['date'])
        
        return {
            "user_id": current_user.uid,
            "events": calendar_events[:10],  # Limit to 10 upcoming events
            "total_events": len(calendar_events),
            "last_updated": now.isoformat()
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch calendar data: {str(e)}"
        )
