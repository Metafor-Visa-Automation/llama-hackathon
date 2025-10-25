from fastapi import APIRouter, HTTPException, status, Depends, Query
from app.core.firebase import db
from app.models.schemas import (
    SupportTicketCreate, SupportTicketResponse
)
from app.services.security import get_current_user, UserInDB
from datetime import datetime
from typing import List, Optional
import uuid

router = APIRouter()


@router.post("/support/tickets", response_model=SupportTicketResponse, status_code=status.HTTP_201_CREATED)
async def create_support_ticket(
    ticket_data: SupportTicketCreate,
    current_user: UserInDB = Depends(get_current_user)
):
    """
    Create a new support ticket
    """
    try:
        ticket_id = str(uuid.uuid4())
        now = datetime.utcnow()
        
        ticket_doc = {
            "ticket_id": ticket_id,
            "user_id": current_user.uid,
            "subject": ticket_data.subject,
            "description": ticket_data.description,
            "priority": ticket_data.priority,
            "category": ticket_data.category,
            "status": "open",
            "created_at": now,
            "updated_at": now,
            "resolved_at": None
        }
        
        # Save to Firestore
        db.collection('SUPPORT_TICKET').document(ticket_id).set(ticket_doc)
        
        return SupportTicketResponse(
            ticket_id=ticket_id,
            user_id=current_user.uid,
            subject=ticket_data.subject,
            description=ticket_data.description,
            priority=ticket_data.priority,
            category=ticket_data.category,
            status="open",
            created_at=now,
            updated_at=now,
            resolved_at=None
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create support ticket: {str(e)}"
        )


@router.get("/support/tickets", response_model=List[SupportTicketResponse])
async def get_support_tickets(
    current_user: UserInDB = Depends(get_current_user),
    status_filter: Optional[str] = Query(None, description="Filter by ticket status"),
    priority_filter: Optional[str] = Query(None, description="Filter by priority"),
    category_filter: Optional[str] = Query(None, description="Filter by category"),
    limit: int = Query(50, ge=1, le=100, description="Number of results to return")
):
    """
    Get user's support tickets
    """
    try:
        query = db.collection('SUPPORT_TICKET').where('user_id', '==', current_user.uid)
        
        # Apply filters
        if status_filter:
            query = query.where('status', '==', status_filter)
        if priority_filter:
            query = query.where('priority', '==', priority_filter)
        if category_filter:
            query = query.where('category', '==', category_filter)
        
        # Execute query
        docs = query.limit(limit).order_by('created_at', direction='DESCENDING').stream()
        
        tickets = []
        for doc in docs:
            data = doc.to_dict()
            tickets.append(SupportTicketResponse(
                ticket_id=data['ticket_id'],
                user_id=data['user_id'],
                subject=data['subject'],
                description=data['description'],
                priority=data['priority'],
                category=data['category'],
                status=data['status'],
                created_at=data['created_at'],
                updated_at=data['updated_at'],
                resolved_at=data.get('resolved_at')
            ))
        
        return tickets
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch support tickets: {str(e)}"
        )


@router.get("/support/tickets/{ticket_id}", response_model=SupportTicketResponse)
async def get_support_ticket(
    ticket_id: str,
    current_user: UserInDB = Depends(get_current_user)
):
    """
    Get a specific support ticket
    """
    try:
        doc = db.collection('SUPPORT_TICKET').document(ticket_id).get()
        if not doc.exists:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Support ticket not found"
            )
        
        data = doc.to_dict()
        
        # Verify ticket belongs to current user
        if data['user_id'] != current_user.uid:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied: Ticket does not belong to current user"
            )
        
        return SupportTicketResponse(
            ticket_id=data['ticket_id'],
            user_id=data['user_id'],
            subject=data['subject'],
            description=data['description'],
            priority=data['priority'],
            category=data['category'],
            status=data['status'],
            created_at=data['created_at'],
            updated_at=data['updated_at'],
            resolved_at=data.get('resolved_at')
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch support ticket: {str(e)}"
        )


@router.get("/support/faq")
async def get_faq():
    """
    Get frequently asked questions
    """
    try:
        # Static FAQ data - in production, this could come from a database
        faq_data = [
            {
                "id": "1",
                "question": "How do I upload documents?",
                "answer": "Go to your tasks, select the task you want to complete, and click 'Upload Document'. Make sure the file is in PDF, JPG, or PNG format.",
                "category": "documents"
            },
            {
                "id": "2", 
                "question": "What documents do I need for a student visa?",
                "answer": "Typically you need: passport copy, academic transcripts, financial statements, acceptance letter, and health insurance. Check your specific visa requirements.",
                "category": "visa_requirements"
            },
            {
                "id": "3",
                "question": "How long does the application process take?",
                "answer": "Processing times vary by country and visa type. Student visas typically take 2-8 weeks, while tourist visas may take 1-4 weeks.",
                "category": "timeline"
            },
            {
                "id": "4",
                "question": "Can I track my application status?",
                "answer": "Yes! Use your dashboard to see real-time updates on your application and task progress.",
                "category": "tracking"
            },
            {
                "id": "5",
                "question": "What if my document is rejected?",
                "answer": "You'll receive a notification explaining why it was rejected. You can upload a new document or contact support for assistance.",
                "category": "documents"
            }
        ]
        
        return {
            "faq": faq_data,
            "total": len(faq_data),
            "categories": ["documents", "visa_requirements", "timeline", "tracking"]
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch FAQ: {str(e)}"
        )
