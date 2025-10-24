from pydantic import BaseModel, EmailStr
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

class UserRole(str, Enum):
    INDIVIDUAL = "individual"
    FAMILY_HEAD = "family_head"
    COMPANY_ADMIN = "company_admin"
    COMPANY_EMPLOYEE = "company_employee"

class VisaType(str, Enum):
    TOURIST = "tourist"
    BUSINESS = "business"
    STUDENT = "student"
    WORK = "work"
    FAMILY = "family"
    TRANSIT = "transit"

class ApplicationStatus(str, Enum):
    DRAFT = "draft"
    SUBMITTED = "submitted"
    UNDER_REVIEW = "under_review"
    APPROVED = "approved"
    REJECTED = "rejected"
    REQUIRES_DOCUMENTS = "requires_documents"

class DocumentType(str, Enum):
    PASSPORT = "passport"
    PHOTO = "photo"
    BANK_STATEMENT = "bank_statement"
    EMPLOYMENT_LETTER = "employment_letter"
    INVITATION_LETTER = "invitation_letter"
    TRAVEL_INSURANCE = "travel_insurance"
    FLIGHT_RESERVATION = "flight_reservation"
    HOTEL_RESERVATION = "hotel_reservation"
    OTHER = "other"

# User Models
class UserBase(BaseModel):
    email: EmailStr
    first_name: str
    last_name: str
    phone: Optional[str] = None
    role: UserRole = UserRole.INDIVIDUAL

class UserCreate(UserBase):
    password: str

class UserUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None

class User(UserBase):
    id: str
    created_at: datetime
    updated_at: datetime
    is_active: bool = True
    
    class Config:
        from_attributes = True

# Visa Application Models
class VisaApplicationBase(BaseModel):
    visa_type: VisaType
    destination_country: str
    purpose_of_travel: str
    intended_arrival_date: datetime
    intended_departure_date: datetime
    passport_number: str
    passport_expiry_date: datetime

class VisaApplicationCreate(VisaApplicationBase):
    pass

class VisaApplicationUpdate(BaseModel):
    visa_type: Optional[VisaType] = None
    destination_country: Optional[str] = None
    purpose_of_travel: Optional[str] = None
    intended_arrival_date: Optional[datetime] = None
    intended_departure_date: Optional[datetime] = None
    passport_number: Optional[str] = None
    passport_expiry_date: Optional[datetime] = None

class VisaApplication(VisaApplicationBase):
    id: str
    user_id: str
    status: ApplicationStatus = ApplicationStatus.DRAFT
    created_at: datetime
    updated_at: datetime
    form_data: Optional[Dict[str, Any]] = None
    document_checklist: Optional[List[str]] = None
    
    class Config:
        from_attributes = True

# Document Models
class DocumentBase(BaseModel):
    document_type: DocumentType
    filename: str
    file_path: str
    file_size: int
    mime_type: str

class DocumentCreate(DocumentBase):
    visa_application_id: str

class Document(DocumentBase):
    id: str
    user_id: str
    visa_application_id: str
    uploaded_at: datetime
    ocr_data: Optional[Dict[str, Any]] = None
    validation_status: Optional[str] = None
    validation_errors: Optional[List[str]] = None
    
    class Config:
        from_attributes = True

# Social Media Audit Models
class SocialMediaAuditBase(BaseModel):
    platform: str
    username: str
    audit_status: str = "pending"

class SocialMediaAuditCreate(SocialMediaAuditBase):
    visa_application_id: str

class SocialMediaAudit(SocialMediaAuditBase):
    id: str
    user_id: str
    visa_application_id: str
    created_at: datetime
    completed_at: Optional[datetime] = None
    risk_score: Optional[float] = None
    flagged_content: Optional[List[Dict[str, Any]]] = None
    recommendations: Optional[List[str]] = None
    
    class Config:
        from_attributes = True

# AI Form Filling Models
class FormField(BaseModel):
    field_name: str
    field_value: str
    field_type: str
    is_required: bool = True

class FormFillingRequest(BaseModel):
    visa_application_id: str
    form_type: str  # e.g., "DS-160", "Schengen"
    user_responses: Dict[str, str]

class FormFillingResponse(BaseModel):
    filled_form: Dict[str, str]
    confidence_score: float
    warnings: Optional[List[str]] = None

# Document Checklist Models
class DocumentRequirement(BaseModel):
    document_type: DocumentType
    is_required: bool
    description: str
    country_specific_notes: Optional[str] = None

class DocumentChecklistResponse(BaseModel):
    visa_type: VisaType
    destination_country: str
    requirements: List[DocumentRequirement]
    estimated_processing_time: str
