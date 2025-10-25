from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


# Enums
class ProfileType(str, Enum):
    STUDENT = "STUDENT"
    WORKER = "WORKER"
    TOURIST = "TOURIST"
    BUSINESS = "BUSINESS"


class PassportType(str, Enum):
    BORDO = "BORDO"  # Red/Purple passport
    YESIL = "YESIL"  # Green passport


class VisaRequirementType(str, Enum):
    VISA_REQUIRED = "VISA_REQUIRED"
    VISA_NOT_REQUIRED = "VISA_NOT_REQUIRED"
    EVISA = "EVISA"
    VISA_ON_ARRIVAL = "VISA_ON_ARRIVAL"


class TaskStatus(str, Enum):
    PENDING = "PENDING"
    IN_PROGRESS = "IN_PROGRESS"
    DONE = "DONE"
    REJECTED = "REJECTED"


class DocumentStatus(str, Enum):
    PENDING_VALIDATION = "PENDING_VALIDATION"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"


class ApplicationStatus(str, Enum):
    DRAFT = "DRAFT"
    SUBMITTED = "SUBMITTED"
    UNDER_REVIEW = "UNDER_REVIEW"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"


# Request Models
class UserLogin(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=6)


class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=6)
    name: str = Field(..., min_length=2, max_length=100)
    surname: str = Field(..., min_length=2, max_length=100)
    profile_type: ProfileType
    passport_type: PassportType
    phone: Optional[str] = None
    date_of_birth: Optional[str] = None
    nationality: Optional[str] = None


class UserUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=100)
    surname: Optional[str] = Field(None, min_length=2, max_length=100)
    profile_type: Optional[ProfileType] = None
    passport_type: Optional[PassportType] = None
    phone: Optional[str] = None
    date_of_birth: Optional[str] = None
    nationality: Optional[str] = None


class ApplicationCreate(BaseModel):
    requirement_id: str = Field(..., description="Visa requirement ID (e.g., 'tr_de_all')")
    ai_filled_form_data: Dict[str, Any] = Field(..., description="AI-generated form data")


class ApplicationUpdate(BaseModel):
    status: Optional[ApplicationStatus] = None
    ai_filled_form_data: Optional[Dict[str, Any]] = None


class ApplicationSubmit(BaseModel):
    submit_notes: Optional[str] = None


class TaskUpdate(BaseModel):
    status: Optional[TaskStatus] = None
    notes: Optional[str] = None


class TaskComplete(BaseModel):
    completion_notes: Optional[str] = None


class UserResponse(BaseModel):
    uid: str
    email: str
    name: str
    surname: str
    profile_type: ProfileType
    passport_type: PassportType
    phone: Optional[str] = None
    date_of_birth: Optional[str] = None
    nationality: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ApplicationResponse(BaseModel):
    app_id: str
    user_id: str
    requirement_id: str
    status: ApplicationStatus
    ai_filled_form_data: Dict[str, Any]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class UserDashboard(BaseModel):
    user: UserResponse
    total_applications: int
    active_applications: int
    completed_tasks: int
    pending_tasks: int
    recent_applications: List[ApplicationResponse]
    upcoming_deadlines: List[Dict[str, Any]]
    progress_summary: Dict[str, Any]


class NotificationResponse(BaseModel):
    notification_id: str
    user_id: str
    title: str
    message: str
    type: str  # "info", "warning", "success", "error"
    is_read: bool
    created_at: datetime
    read_at: Optional[datetime] = None


class DocumentAnalysisRequest(BaseModel):
    task_id: str
    analysis_type: str = "general"  # "general", "passport", "financial", "academic"


class DocumentAnalysisResponse(BaseModel):
    analysis_id: str
    task_id: str
    document_type: str
    confidence_score: float
    findings: List[str]
    recommendations: List[str]
    issues: List[str]
    status: str
    created_at: datetime


class TaskDashboard(BaseModel):
    total_tasks: int
    pending_tasks: int
    in_progress_tasks: int
    completed_tasks: int
    rejected_tasks: int
    tasks_by_application: Dict[str, Dict[str, int]]
    recent_activity: List[Dict[str, Any]]
    upcoming_deadlines: List[Dict[str, Any]]


class SupportTicketCreate(BaseModel):
    subject: str
    description: str
    priority: str = "medium"  # "low", "medium", "high", "urgent"
    category: str = "general"  # "general", "technical", "billing", "feature_request"


class SupportTicketResponse(BaseModel):
    ticket_id: str
    user_id: str
    subject: str
    description: str
    priority: str
    category: str
    status: str  # "open", "in_progress", "resolved", "closed"
    created_at: datetime
    updated_at: datetime
    resolved_at: Optional[datetime] = None


class VisaRecommendationRequest(BaseModel):
    origin_country: str
    destination_country: str
    passport_type: str
    profile_type: str
    purpose: str  # "study", "work", "tourism", "business"
    duration: Optional[str] = None
    budget: Optional[str] = None


class VisaRecommendationResponse(BaseModel):
    recommendation_id: str
    user_id: str
    origin_country: str
    destination_country: str
    recommended_visa_type: str
    confidence_score: float
    requirements: List[str]
    estimated_processing_time: str
    estimated_cost: str
    success_probability: float
    alternatives: List[Dict[str, Any]]
    tips: List[str]
    created_at: datetime


class UserAnalyticsResponse(BaseModel):
    user_id: str
    total_applications: int
    successful_applications: int
    success_rate: float
    average_processing_time: float
    most_common_destinations: List[Dict[str, Any]]
    application_trends: Dict[str, int]
    task_completion_stats: Dict[str, Any]
    document_upload_stats: Dict[str, Any]
    monthly_activity: List[Dict[str, Any]]


class EmbassyCheckRequest(BaseModel):
    embassy_name: str
    country_code: str
    check_type: str = "appointment"  # "appointment", "status", "requirements"


class EmbassyCheckResponse(BaseModel):
    check_id: str
    embassy_name: str
    country_code: str
    check_type: str
    status: str
    available_dates: List[str]
    requirements: List[str]
    processing_time: str
    contact_info: Dict[str, str]
    last_updated: datetime


class DataExportRequest(BaseModel):
    export_type: str = "all"  # "all", "applications", "tasks", "documents"
    format: str = "json"  # "json", "csv", "pdf"
    date_range: Optional[Dict[str, str]] = None


class DataExportResponse(BaseModel):
    export_id: str
    user_id: str
    export_type: str
    format: str
    file_url: str
    file_size: int
    record_count: int
    created_at: datetime
    expires_at: datetime


# Response Models
class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse
    expires_in: int = 3600  # Token expires in 1 hour

    class Config:
        from_attributes = True


class TaskResponse(BaseModel):
    task_id: str
    application_id: str
    user_id: str
    template_id: str
    title: str
    description: str
    status: TaskStatus
    notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class DocumentResponse(BaseModel):
    doc_id: str
    task_id: str
    user_id: str
    storage_path: str
    status: DocumentStatus
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class VisaRequirementResponse(BaseModel):
    req_id: str
    origin_country: str
    destination_code: str
    applicable_passport_types: List[str]
    visa_requirement_type: VisaRequirementType
    visa_name: str
    visa_fee: Optional[str] = None
    passport_validity: Optional[str] = None
    application_link: Optional[str] = None
    embassy_url: Optional[str] = None
    letter_template: List[str] = []
    created_at: datetime
    updated_at: datetime
    last_verified_at: datetime

    class Config:
        from_attributes = True


# Database Models
class UserInDB(BaseModel):
    uid: str
    email: str
    name: str
    surname: str
    profile_type: ProfileType
    passport_type: PassportType
    phone: Optional[str] = None
    date_of_birth: Optional[str] = None
    nationality: Optional[str] = None
    created_at: datetime
    updated_at: datetime


class ApplicationInDB(BaseModel):
    app_id: str
    user_id: str
    requirement_id: str
    status: ApplicationStatus
    ai_filled_form_data: Dict[str, Any]
    created_at: datetime
    updated_at: datetime


class TaskInDB(BaseModel):
    task_id: str
    application_id: str
    user_id: str
    template_id: str
    title: str
    description: str
    status: TaskStatus
    notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime


class DocumentInDB(BaseModel):
    doc_id: str
    task_id: str
    user_id: str
    storage_path: str
    status: DocumentStatus
    created_at: datetime
    updated_at: datetime


class VisaRequirementInDB(BaseModel):
    req_id: str
    origin_country: str
    destination_code: str
    applicable_passport_types: List[str]
    visa_requirement_type: VisaRequirementType
    visa_name: str
    visa_fee: Optional[str] = None
    passport_validity: Optional[str] = None
    application_link: Optional[str] = None
    embassy_url: Optional[str] = None
    letter_template: List[str] = []
    created_at: datetime
    updated_at: datetime
    last_verified_at: datetime


class ChecklistTemplateInDB(BaseModel):
    template_id: str
    requirement_id: str
    title: str
    description: str
    required_for: List[str]  # ["STUDENT", "WORKER", "ALL", etc.]
    created_at: datetime
    updated_at: datetime


# Error Models
class ErrorResponse(BaseModel):
    detail: str
    error_code: Optional[str] = None


class ValidationErrorResponse(BaseModel):
    detail: List[Dict[str, Any]]
