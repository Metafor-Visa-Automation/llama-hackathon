"""
Unified User Profile Model.
Merges VisaProfile and UserProfile into single comprehensive model.
"""

from datetime import datetime
from typing import List, Dict, Any, Optional
from enum import Enum
from pydantic import BaseModel, Field, field_validator


class VisaType(str, Enum):
    """Visa types enum."""
    TOURIST = "tourist"
    BUSINESS = "business"
    STUDENT = "student"
    WORK = "work"
    TRANSIT = "transit"
    FAMILY_VISIT = "family_visit"
    MEDICAL = "medical"
    OTHER = "other"


class TravelDates(BaseModel):
    """Travel date information."""
    start: str = Field(..., description="Travel start date (YYYY-MM-DD)")
    end: str = Field(..., description="Travel end date (YYYY-MM-DD)")
    
    @field_validator('start', 'end')
    @classmethod
    def validate_date_format(cls, v: str) -> str:
        """Validate date format."""
        try:
            datetime.strptime(v, '%Y-%m-%d')
            return v
        except ValueError:
            raise ValueError(f"Date must be in YYYY-MM-DD format, got: {v}")


class UnifiedUserProfile(BaseModel):
    """
    Unified user profile for visa application.
    Combines all information needed for both checklist and cover letter generation.
    """
    
    # Identity
    user_id: str = Field(..., description="Unique user identifier")
    full_name: str = Field(..., description="Full name")
    nationality: str = Field(..., description="Nationality/citizenship")
    
    # Visa Application
    destination_country: str = Field(..., description="Destination country for visa")
    visa_type: VisaType = Field(..., description="Type of visa being applied for")
    travel_purpose: str = Field(..., description="Detailed purpose of travel", min_length=10)
    travel_dates: TravelDates = Field(..., description="Planned travel dates")
    
    # Background
    occupation: str = Field(..., description="Current occupation")
    education: Optional[str] = Field(None, description="Highest education level")
    
    # Travel & Financial
    previous_travel_history: List[str] = Field(
        default_factory=list,
        description="List of previously visited countries"
    )
    financial_status: Optional[str] = Field(
        None,
        description="Financial status description"
    )
    
    # Ties to Home Country
    ties_to_home_country: List[str] = Field(
        default_factory=list,
        description="Ties to home country (employment, property, family)"
    )
    
    # Additional Information
    additional_info: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional relevant information"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "user_id": "user_001",
                "full_name": "John Doe",
                "nationality": "Turkey",
                "destination_country": "France",
                "visa_type": "tourist",
                "travel_purpose": "Tourism and visiting historical landmarks",
                "travel_dates": {
                    "start": "2024-06-15",
                    "end": "2024-06-30"
                },
                "occupation": "Software Engineer",
                "education": "Bachelor's Degree in Computer Science",
                "previous_travel_history": ["Germany", "Italy", "Spain"],
                "financial_status": "Employed with stable income, $15,000 savings",
                "ties_to_home_country": [
                    "Permanent employment",
                    "Owns property",
                    "Family members in home country"
                ],
                "additional_info": {
                    "company": "Tech Company",
                    "years_of_employment": 5
                }
            }
        }
    
    def to_visa_profile_dict(self) -> Dict[str, Any]:
        """Convert to VisaProfile format for checklist generation."""
        return {
            "user_id": self.user_id,
            "nationality": self.nationality,
            "destination_country": self.destination_country,
            "visa_type": self.visa_type,
            "occupation": self.occupation,
            "travel_dates": self.travel_dates.dict(),
            "travel_purpose": self.travel_purpose,
            "previous_travel_history": self.previous_travel_history,
            "financial_status": self.financial_status,
            "ties_to_home_country": self.ties_to_home_country,
            "education": self.education,
            "additional_info": self.additional_info
        }
    
    def to_cover_letter_profile_dict(self) -> Dict[str, Any]:
        """Convert to cover letter profile format."""
        return {
            "user_id": self.user_id,
            "full_name": self.full_name,
            "nationality": self.nationality,
            "destination_country": self.destination_country,
            "visa_type": self.visa_type,
            "travel_purpose": self.travel_purpose,
            "travel_dates": self.travel_dates.dict(),
            "occupation": self.occupation,
            "education": self.education,
            "previous_travel_history": self.previous_travel_history,
            "financial_status": self.financial_status,
            "ties_to_home_country": self.ties_to_home_country,
            "additional_info": self.additional_info
        }

