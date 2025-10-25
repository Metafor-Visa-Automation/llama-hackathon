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


class Gender(str, Enum):
    MALE = "MALE"
    FEMALE = "FEMALE"
    OTHER = "OTHER"


class DocumentType(str, Enum):
    PASSPORT = "PASSPORT"
    BANK_STATEMENT = "BANK_STATEMENT"
    EMPLOYMENT_LETTER = "EMPLOYMENT_LETTER"
    TRAVEL_INSURANCE = "TRAVEL_INSURANCE"
    HOTEL_RESERVATION = "HOTEL_RESERVATION"
    FLIGHT_RESERVATION = "FLIGHT_RESERVATION"


# Application Step Models
class ApplicationStep(BaseModel):
    step_id: str
    title: str
    description: str
    priority_score: int
    requires_document: bool
    document_id: Optional[str] = None
    status: str = "pending"  # e.g., "pending", "completed"
    source_urls: List[str] = []

class ApplicationStepUpdate(BaseModel):
    document_id: Optional[str] = None
    status: Optional[str] = None


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
    application_name: str = Field(..., description="Name of the application")
    country_code: str = Field(..., description="Destination country code (e.g., 'US', 'DE')")


class ApplicationUpdate(BaseModel):
    status: Optional[ApplicationStatus] = None


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
    gender: Optional[Gender] = None
    passport_number: Optional[str] = None
    passport_expiry_date: Optional[str] = None
    passport_issue_date: Optional[str] = None
    preferences: Optional[Dict[str, Any]] = None
    created_at: datetime
    updated_at: datetime
    last_login_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse
    expires_in: int = 3600  # Token expires in 1 hour

    class Config:
        from_attributes = True


class DocumentResponse(BaseModel):
    doc_id: str
    application_id: str
    user_id: str
    storage_path: str
    status: DocumentStatus
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ApplicationResponse(BaseModel):
    app_id: str
    user_id: str
    application_name: str
    country_code: str
    status: ApplicationStatus
    application_steps: List[ApplicationStep] = []
    created_at: datetime
    updated_at: datetime
    submitted_at: Optional[datetime] = None
    approved_at: Optional[datetime] = None

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
    application_name: str
    country_code: str
    status: ApplicationStatus
    application_steps: List[ApplicationStep] = []
    created_at: datetime
    updated_at: datetime


class DocumentInDB(BaseModel):
    doc_id: str
    application_id: str
    user_id: str
    storage_path: str
    status: DocumentStatus
    created_at: datetime
    updated_at: datetime


# Error Models
class ErrorResponse(BaseModel):
    detail: str
    error_code: Optional[str] = None


class ValidationErrorResponse(BaseModel):
    detail: List[Dict[str, Any]]
