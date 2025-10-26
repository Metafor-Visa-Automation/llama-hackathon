"""
Data models for Unified Visa AI System.
"""

from .user_profile import UnifiedUserProfile, VisaType, TravelDates
from .visa_models import (
    VisaRequirement,
    ActionStep,
    StepsResponse,
    ScrapedData
)
from .cover_letter_models import (
    CoverLetterResponse,
    CoverLetterGenerationResponse,
    ExampleCoverLetter,
    GenerationMetadata
)

__all__ = [
    # User Profile
    'UnifiedUserProfile',
    'VisaType',
    'TravelDates',
    
    # Visa Models
    'VisaRequirement',
    'ActionStep',
    'StepsResponse',
    'ScrapedData',
    
    # Cover Letter Models
    'CoverLetterResponse',
    'CoverLetterGenerationResponse',
    'ExampleCoverLetter',
    'GenerationMetadata',
]

