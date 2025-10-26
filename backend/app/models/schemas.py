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
    VALIDATED = "VALIDATED"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"


class ApplicationStatus(str, Enum):
    DRAFT = "DRAFT"
    SUBMITTED = "SUBMITTED"
    UNDER_REVIEW = "UNDER_REVIEW"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"


class Gender(str, Enum):
    MALE = "MALE"
    FEMALE = "FEMALE"
    OTHER = "OTHER"


class TeamType(str, Enum):
    FAMILY = "FAMILY"
    BUSINESS = "BUSINESS"
    STUDENT = "STUDENT"


# DocumentType enum moved to later in file for consistency


class NotificationType(str, Enum):
    INFO = "INFO"
    WARNING = "WARNING"
    SUCCESS = "SUCCESS"
    ERROR = "ERROR"


# Request Models
class UserLogin(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=6)


class UserCreate(BaseModel):
    """Create user request model"""
    email: str = Field(..., description="User email address")
    name: str = Field(..., min_length=2, max_length=100)
    surname: str = Field(..., min_length=2, max_length=100)
    profile_type: str = Field(..., description="User profile type (e.g., 'STUDENT', 'WORKER')")
    passport_type: str = Field(..., description="Passport type (e.g., 'BORDO', 'YESIL')")
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
    """
    Application Create Model - For creating new visa applications
    """
    application_name: str = Field(..., description="User's custom name for the application")
    country_code: str = Field(..., description="Two-letter country code (e.g., 'US', 'DE')")
    travel_purpose: str = Field(..., description="Purpose of travel (e.g., 'Tourism', 'Education', 'Business')")
    application_start_date: Optional[datetime] = Field(None, description="Start date of application period")
    application_end_date: Optional[datetime] = Field(None, description="End date of application period")
    application_steps: List[Dict[str, Any]] = Field(default_factory=list, description="Array of application steps")


class ApplicationUpdate(BaseModel):
    """
    Application Update Model - For updating visa applications
    """
    application_name: Optional[str] = None
    country_code: Optional[str] = None
    travel_purpose: Optional[str] = None  # e.g., "Tourism", "Education", "Business"
    application_start_date: Optional[datetime] = None
    application_end_date: Optional[datetime] = None
    status: Optional[str] = None
    application_steps: Optional[List[Dict[str, Any]]] = None


class ApplicationSubmit(BaseModel):
    submit_notes: Optional[str] = None


class TaskUpdate(BaseModel):
    status: Optional[TaskStatus] = None
    notes: Optional[str] = None


class TaskComplete(BaseModel):
    completion_notes: Optional[str] = None






class UserResponse(BaseModel):
    """
    User Response Model - Matches the users collection structure
    """
    uid: str
    email: str
    name: str
    surname: str
    profile_type: str
    passport_type: str
    gender: Optional[str] = None  # e.g., "MALE", "FEMALE", "OTHER"
    phone: Optional[str] = None
    date_of_birth: Optional[str] = None
    nationality: Optional[str] = None
    address: Optional[str] = None  # User's address
    has_schengen_before: Optional[bool] = False  # Has the user had a Schengen visa before
    token: Optional[str] = None  # Authentication token
    last_login_at: Optional[datetime] = None  # Last login timestamp
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class UserUpdate(BaseModel):
    """Update user request model"""
    name: Optional[str] = Field(None, min_length=2, max_length=100)
    surname: Optional[str] = Field(None, min_length=2, max_length=100)
    profile_type: Optional[str] = None
    passport_type: Optional[str] = None
    gender: Optional[str] = None
    phone: Optional[str] = None
    date_of_birth: Optional[str] = None
    nationality: Optional[str] = None
    address: Optional[str] = None
    has_schengen_before: Optional[bool] = None


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse
    expires_in: int = 3600  # Token expires in 1 hour

    class Config:
        from_attributes = True


# class UserDashboard(BaseModel):
#     user: UserResponse
#     total_applications: int
#     active_applications: int
#     completed_tasks: int
#     pending_tasks: int
#     recent_applications: List["ApplicationResponse"]
#     upcoming_deadlines: List[Dict[str, Any]]
#     progress_summary: Dict[str, Any]


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


# OCR-specific schemas
class OCRValidationRule(BaseModel):
    enabled: bool
    description: str


class BankStatementValidationRules(OCRValidationRule):
    check_account_balance: bool = True
    check_bank_stamp: bool = True
    check_statement_period: bool = True
    min_months: int = 3
    min_balance_threshold: float = 1000.0


class PassportValidationRules(OCRValidationRule):
    check_expiry_date: bool = True
    check_issuance_date: bool = True
    check_passport_number: bool = True
    min_pages: int = 2
    validity_months: int = 3


class BiometricPhotoValidationRules(OCRValidationRule):
    check_background_color: bool = True
    check_face_visible: bool = True
    check_photo_size: bool = True
    check_recent_photo: bool = True
    photo_count: int = 2
    required_width_mm: int = 35
    required_height_mm: int = 45
    max_photo_age_months: int = 6
    check_face_centered: bool = True
    check_neutral_expression: bool = True
    check_eyes_open: bool = True
    check_no_glasses: bool = True
    check_no_headwear: bool = True
    check_proper_lighting: bool = True
    check_high_resolution: bool = True
    min_resolution_width: int = 600
    min_resolution_height: int = 600
    max_file_size_mb: int = 5


class BirthCertificateValidationRules(OCRValidationRule):
    check_birth_date: bool = True
    check_official_stamp: bool = True
    check_parents_names: bool = True


class DocumentTypeConfig(BaseModel):
    checkId: str
    docDescription: str
    docName: str
    ocrValidationRules: Dict[str, Any]
    requiredFor: List[str]


class OCRProcessRequest(BaseModel):
    document_type: str
    extracted_text: str
    file_metadata: Optional[Dict[str, Any]] = None


class OCRValidationResult(BaseModel):
    valid: bool
    issues: List[str]
    recommendations: List[str]
    details: Dict[str, Any]


class OCRProcessResponse(BaseModel):
    document_type: str
    confidence_score: float
    extracted_text: str
    validation_results: Dict[str, OCRValidationResult]
    issues: List[str]
    recommendations: List[str]
    metadata: Dict[str, Any]


class OCRDocumentAnalysisRequest(BaseModel):
    task_id: str
    document_type: str
    extracted_text: str
    file_metadata: Optional[Dict[str, Any]] = None


class OCRDocumentAnalysisResponse(BaseModel):
    analysis_id: str
    task_id: str
    document_type: str
    confidence_score: float
    validation_results: Dict[str, OCRValidationResult]
    issues: List[str]
    recommendations: List[str]
    status: str
    created_at: datetime
    metadata: Dict[str, Any]


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


# Form Filling Schemas
class FormFillingRequest(BaseModel):
    user_data: Dict[str, Any] = Field(..., description="User data to fill in the form")
    template_pdf_path: Optional[str] = Field(None, description="Path to template PDF (optional)")
    include_preview: bool = Field(False, description="Include form preview in response")


class FormFillingResponse(BaseModel):
    filled_form_id: str
    user_id: str
    form_type: str
    filled_form_url: Optional[str] = None
    filled_form_data: bytes = Field(..., description="Filled PDF as bytes")
    validation_results: Dict[str, Any]
    preview: Optional[Dict[str, Any]] = None
    created_at: datetime


class FormPreviewRequest(BaseModel):
    user_data: Dict[str, Any] = Field(..., description="User data for preview")


class FormPreviewResponse(BaseModel):
    form_type: str
    filled_fields: Dict[str, Any]
    validation_results: Dict[str, Any]
    recommendations: List[str] = []


class UserFormDataSchema(BaseModel):
    """Schema for user form data validation"""
    # Personal Information
    surname: str = Field(..., min_length=1, max_length=100)
    surname_at_birth: Optional[str] = Field(None, max_length=100)
    first_name: str = Field(..., min_length=1, max_length=100)
    date_of_birth: str = Field(..., description="Format: DD/MM/YYYY")
    place_of_birth: str = Field(..., min_length=1, max_length=100)
    country_of_birth: str = Field(..., min_length=1, max_length=100)
    current_nationality: str = Field(..., min_length=1, max_length=100)
    sex: str = Field(..., pattern="^(Male|Female)$")
    marital_status: str = Field(..., min_length=1, max_length=50)
    
    # Passport Information
    passport_type: str = Field(..., min_length=1, max_length=50)
    passport_number: str = Field(..., min_length=1, max_length=50)
    passport_issue_date: str = Field(..., description="Format: DD/MM/YYYY")
    passport_expiry_date: str = Field(..., description="Format: DD/MM/YYYY")
    passport_issued_by: str = Field(..., min_length=1, max_length=100)
    
    # Address Information
    current_address: str = Field(..., min_length=1, max_length=200)
    city: str = Field(..., min_length=1, max_length=100)
    postal_code: str = Field(..., min_length=1, max_length=20)
    country: str = Field(..., min_length=1, max_length=100)
    phone_number: str = Field(..., min_length=1, max_length=20)
    email: EmailStr
    
    # Travel Information
    purpose_of_journey: str = Field(..., min_length=1, max_length=100)
    intended_arrival_date: str = Field(..., description="Format: DD/MM/YYYY")
    intended_departure_date: str = Field(..., description="Format: DD/MM/YYYY")
    member_state_of_first_entry: str = Field(..., min_length=1, max_length=100)
    number_of_entries_requested: str = Field(..., min_length=1, max_length=50)
    
    # Additional Information
    family_members_in_eu: Optional[str] = Field(None, max_length=200)
    eu_residence_permit: Optional[str] = Field(None, max_length=200)
    previous_schengen_visa: Optional[str] = Field(None, max_length=200)
    fingerprints_taken: Optional[str] = Field(None, max_length=200)
    
    # Emergency Contact
    emergency_contact_name: Optional[str] = Field(None, max_length=100)
    emergency_contact_phone: Optional[str] = Field(None, max_length=20)
    emergency_contact_email: Optional[EmailStr] = None


# Response Models
# class LoginResponse(BaseModel):
#     access_token: str
#     token_type: str = "bearer"
#     user: UserResponse
#     expires_in: int = 3600  # Token expires in 1 hour
#
#     class Config:
#         from_attributes = True




class DocumentCreate(BaseModel):
    """
    Document Create Model - For uploading documents
    """
    storage_path: str = Field(..., description="Path in Firebase Storage")
    status: str = "PENDING_VALIDATION"  # Default status


class DocumentResponse(BaseModel):
    """
    Document Response Model - Matches the documents collection structure
    """
    doc_id: str
    user_id: str
    storage_path: str
    file_name: Optional[str] = None
    file_size: Optional[int] = None
    mime_type: Optional[str] = None
    download_url: Optional[str] = None
    status: str
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


# Database Models - Simplified according to specification
class UserInDB(BaseModel):
    """
    Users Collection - Stores user information
    """
    uid: str  # Primary Key - Firebase user ID
    email: str
    name: str
    surname: str
    profile_type: str  # e.g., "STUDENT", "WORKER"
    passport_type: str  # e.g., "BORDO", "YESIL"
    gender: Optional[str] = None  # e.g., "MALE", "FEMALE", "OTHER"
    phone: Optional[str] = None
    date_of_birth: Optional[str] = None
    nationality: Optional[str] = None  # Country code, e.g., "TR"
    address: Optional[str] = None  # User's address
    has_schengen_before: Optional[bool] = False  # Has the user had a Schengen visa before
    token: Optional[str] = None  # Authentication token
    last_login_at: Optional[datetime] = None  # Last login timestamp
    created_at: datetime
    updated_at: datetime




class DocumentInDB(BaseModel):
    """
    Documents Collection - Stores user's uploaded documents
    """
    doc_id: str  # Primary Key
    user_id: str  # Foreign Key to users table
    storage_path: str  # Full path in Firebase Storage
    status: str  # e.g., "PENDING_VALIDATION", "APPROVED", "REJECTED"
    created_at: datetime
    updated_at: datetime


# Additional Enums
class TeamType(str, Enum):
    BUSINESS = "BUSINESS"
    FAMILY = "FAMILY"


class Gender(str, Enum):
    MALE = "MALE"
    FEMALE = "FEMALE"


class DocumentType(str, Enum):
    # Core document types
    PASSPORT = "passport"
    BANK_STATEMENT = "bank_statement"
    BIOMETRIC_PHOTO = "biometric_photo"
    BIRTH_CERTIFICATE = "birth_certificate"
    
    # Business and employment documents
    BUSINESS_LETTER = "business_letter"
    EMPLOYMENT_LETTER = "employment_letter"
    EMPLOYMENT_CERTIFICATE = "employment_certificate"
    PAYSLIP = "payslip"
    
    # Travel and accommodation documents
    HOTEL_RESERVATION = "hotel_reservation"
    FLIGHT_RESERVATION = "flight_reservation"
    TRAVEL_INSURANCE = "travel_insurance"
    INVITATION_LETTER = "invitation_letter"
    PREVIOUS_VISAS = "previous_visas"
    
    # Academic documents
    STUDENT_CERTIFICATE = "student_certificate"
    ACADEMIC_TRANSCRIPT = "academic_transcript"
    
    # Financial and legal documents
    TAX_RETURN = "tax_return"
    PROPERTY_DEED = "property_deed"
    SOCIAL_SECURITY = "social_security"
    
    # Insurance documents
    INSURANCE = "insurance"
    
    # Other
    OTHER = "other"


class NotificationType(str, Enum):
    INFO = "info"
    WARNING = "warning"
    SUCCESS = "success"
    ERROR = "error"


# Team Management Schemas
class TeamCreate(BaseModel):
    team_name: str = Field(..., min_length=2, max_length=100)
    team_type: TeamType


class TeamUpdate(BaseModel):
    team_name: Optional[str] = Field(None, min_length=2, max_length=100)
    team_type: Optional[TeamType] = None


class TeamResponse(BaseModel):
    team_id: str
    team_name: str
    owner_id: str
    members: List[str]
    team_type: TeamType
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class TeamJoinRequest(BaseModel):
    team_id: str


# User Document Management Schemas
class UserDocumentUpload(BaseModel):
    document_type: DocumentType
    document_title: str = Field(..., min_length=1, max_length=100)
    notes: Optional[str] = None
    tags: Optional[List[str]] = None


class UserDocumentUpdate(BaseModel):
    document_title: Optional[str] = Field(None, min_length=1, max_length=100)
    notes: Optional[str] = None
    tags: Optional[List[str]] = None


class UserDocumentResponse(BaseModel):
    doc_id: str
    user_id: str
    storage_path: str
    doc_type: DocumentType
    status: DocumentStatus
    ocr_result: Optional[Dict[str, Any]] = None
    document_title: str
    file_name: str
    file_size: int
    mime_type: str
    uploaded_at: datetime
    updated_at: datetime
    expiry_date: Optional[datetime] = None
    issued_date: Optional[datetime] = None
    issuing_authority: Optional[str] = None
    notes: Optional[str] = None
    tags: Optional[List[str]] = None

    class Config:
        from_attributes = True


# Enhanced Task Management Schemas
class TaskAssignDocument(BaseModel):
    doc_ids: List[str] = Field(..., min_items=1)


class TaskResponse(BaseModel):
    task_id: str
    user_id: str
    application_id: str
    template_id: str
    title: str
    description: str
    status: TaskStatus
    assigned_doc_ids: List[str] = []
    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# Enhanced Application Management Schemas
class ApplicationProgressUpdate(BaseModel):
    completed_items: Optional[int] = None
    selected_templates: Optional[List[str]] = None


class ApplicationGenerateLetter(BaseModel):
    letter_template: Optional[str] = None
    custom_content: Optional[Dict[str, Any]] = None


class ApplicationResponse(BaseModel):
    """
    Application Response Model - Matches the applications collection structure
    """
    app_id: str
    user_id: str
    application_name: str
    country_code: str
    travel_purpose: str  # e.g., "Tourism", "Education", "Business"
    application_start_date: Optional[datetime] = None
    application_end_date: Optional[datetime] = None
    status: str
    application_steps: List[Dict[str, Any]] = []
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Country Management Schemas
class CountryResponse(BaseModel):
    countryCode: str
    name: str
    schengenMember: bool

    class Config:
        from_attributes = True
        alias_generator = lambda field_name: field_name.replace('_', '').lower()


# Visa Requirement Management Schemas
class VisaRequirementResponse(BaseModel):
    reqId: str
    originCountry: str
    destinationCode: str
    applicablePassportTypes: List[str]
    visaRequirementTypeBordo: Optional[str] = None
    visaRequirementTypeYesil: Optional[str] = None
    durationBordo: Optional[str] = None
    durationYesil: Optional[str] = None
    passportValidity: Optional[str] = None
    applicationLink: Optional[str] = None
    embassyUrl: Optional[str] = None
    letterTemplate: List[str] = []
    visaWebsites: List[str] = []
    travelWebsites: List[str] = []
    visaFee: Optional[str] = None
    createdAt: datetime
    updatedAt: datetime
    lastVerifiedAt: datetime

    class Config:
        from_attributes = True
        alias_generator = lambda field_name: field_name.replace('_', '').lower()


# Checklist Template Management Schemas
class ChecklistTemplateResponse(BaseModel):
    checkId: str
    docName: str
    docDescription: str
    category: str
    priority: int
    referenceUrl: Optional[str] = None
    isDocumentNeeded: bool
    mandatory: bool
    requiredFor: List[str]
    acceptanceCriteria: List[str]
    validationRules: Dict[str, Any]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
        alias_generator = lambda field_name: field_name.replace('_', '').lower()


# Notification Management Schemas
class NotificationCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    message: str = Field(..., min_length=1, max_length=1000)
    type: NotificationType = NotificationType.INFO
    user_id: Optional[str] = None  # If None, sends to all users


class NotificationResponse(BaseModel):
    notification_id: str
    user_id: str
    title: str
    message: str
    type: NotificationType
    is_read: bool
    created_at: datetime
    read_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class NotificationMarkRead(BaseModel):
    notification_ids: List[str]


# Enhanced User Schemas


# Database Models - Only the 3 core collections
class ApplicationInDB(BaseModel):
    """
    Applications Collection - Stores visa applications
    """
    app_id: str  # Primary Key
    user_id: str  # Foreign Key to users table
    application_name: str  # User's custom name for the application, e.g., "Amerika Turist Vizesi 2025"
    country_code: str  # Two-letter country code, e.g., "US", "DE"
    travel_purpose: str  # e.g., "Tourism", "Education", "Business"
    application_start_date: Optional[datetime] = None  # When the visa application period starts
    application_end_date: Optional[datetime] = None  # When the visa application period ends
    status: str  # e.g., "DRAFT", "SUBMITTED", "APPROVED"
    application_steps: List[Dict[str, Any]] = []  # Array of steps, each step is an object
    created_at: datetime
    updated_at: datetime






# Error Models
class ErrorResponse(BaseModel):
    detail: str
    error_code: Optional[str] = None


class ValidationErrorResponse(BaseModel):
    detail: List[Dict[str, Any]]


# Letter Generation Schemas
class LetterGenerationRequest(BaseModel):
    """Request model for generating visa application letters"""
    application_id: Optional[str] = Field(None, description="Application ID to generate letter for")
    application_data: Optional[Dict[str, Any]] = Field(None, description="Custom application data if no application_id")
    letter_type: str = Field("cover_letter", description="Type of letter (cover_letter, explanation_letter, etc.)")
    language: str = Field("en", description="Language code (en, tr, de, fr, etc.)")
    custom_instructions: Optional[str] = Field(None, description="Additional instructions for letter generation")


class LetterGenerationResponse(BaseModel):
    """Response model for generated letters"""
    letter_id: str
    letter_content: str
    letter_type: str
    language: str
    word_count: int
    created_at: datetime
    metadata: Dict[str, Any]
    
    class Config:
        from_attributes = True
