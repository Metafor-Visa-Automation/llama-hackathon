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


class TaskUpdate(BaseModel):
    status: Optional[TaskStatus] = None
    notes: Optional[str] = None


# Response Models
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
