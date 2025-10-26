"""
Pydantic models for Unified HTTP REST API requests and responses.
Defines the contract between API and clients for all 9 endpoints.
"""

from typing import Optional, List, Dict, Any, Union
from pydantic import BaseModel, Field, field_validator
from models.user_profile import UnifiedUserProfile, VisaType


# === Visa Endpoints Models ===

class GenerateChecklistRequest(BaseModel):
    """Request for visa checklist generation."""
    nationality: str = Field(..., description="Applicant's nationality", example="Turkey")
    destination_country: str = Field(..., description="Target country", example="France")
    target_url: Optional[str] = Field(None, description="Single URL (deprecated, use target_urls or rely on country mapping)", example="https://travel.state.gov/content/travel/en/us-visas/tourism-visit/visitor.html")
    target_urls: Optional[List[str]] = Field(None, description="Multiple URLs for comprehensive checklist. If not provided, URLs will be determined from destination_country", example=["https://france-visas.gouv.fr", "https://www.schengenvisainfo.com/france-visa/"])
    visa_type: VisaType = Field(..., description="Type of visa")
    occupation: Optional[str] = Field(None, description="Occupation", example="Software Engineer")
    travel_purpose: Optional[str] = Field(None, description="Purpose of travel")
    use_rag: bool = Field(True, description="Use RAG for similar cases")
    force_refresh: bool = Field(False, description="Force fresh scraping, bypass cache")
    temperature: float = Field(0.7, ge=0.0, le=1.0, description="LLM temperature")
    # External Matching Parameters
    enable_external_matching: bool = Field(False, description="Enable external title matching")
    external_titles_url: Optional[str] = Field(None, description="URL to fetch external titles", example="http://external-ip:port/api/titles")
    external_submit_url: Optional[str] = Field(None, description="URL to submit matched pairs", example="http://external-ip:port/api/submit-matches")
    matching_threshold: float = Field(0.7, ge=0.0, le=1.0, description="Minimum similarity score for matching")
    
    @field_validator('target_urls', mode='before')
    @classmethod
    def ensure_target_urls_list(cls, v, info):
        """Ensure target_urls is always a list. Falls back to country mapping if not provided."""
        # If target_urls provided, validate and return
        if v is not None:
            if isinstance(v, str):
                return [v]
            if isinstance(v, list) and len(v) == 0:
                raise ValueError("target_urls cannot be empty")
            return v
        
        # If target_url provided (legacy), convert to list
        target_url = info.data.get('target_url')
        if target_url:
            return [target_url]
        
        # Otherwise, will be resolved from destination_country in the endpoint
        # Return None to signal that country mapping should be used
        return None


class ScrapeVisaInfoRequest(BaseModel):
    """Request for scraping visa information from single or multiple sources."""
    country: str = Field(..., description="Country code", example="france")
    target_url: Optional[str] = Field(None, description="Single URL (deprecated, use target_urls)", example="https://france-visas.gouv.fr")
    target_urls: Optional[List[str]] = Field(None, description="Multiple URLs for comprehensive scraping", example=["https://france-visas.gouv.fr", "https://www.schengenvisainfo.com/france-visa/"])
    visa_type: VisaType = Field(..., description="Visa type")
    nationality: Optional[str] = Field(None, description="Applicant nationality")
    force_refresh: bool = Field(False, description="Force fresh scraping, bypass cache")
    
    @field_validator('target_urls', mode='before')
    @classmethod
    def ensure_target_urls_list(cls, v, info):
        """Ensure target_urls is always a list. Provides backward compatibility."""
        # If target_urls not provided, check for target_url
        if v is None:
            target_url = info.data.get('target_url')
            if target_url:
                return [target_url]  # Convert single URL to list
            raise ValueError("Either target_url or target_urls must be provided")
        
        # If target_urls is a string, convert to list
        if isinstance(v, str):
            return [v]
        
        # Validate list is not empty
        if isinstance(v, list) and len(v) == 0:
            raise ValueError("target_urls cannot be empty")
        
        return v


# === Cover Letter Endpoints Models ===

class GenerateCoverLetterRequest(BaseModel):
    """Request for cover letter generation with visa requirements context."""
    user_profile: UnifiedUserProfile = Field(..., description="Complete user profile")
    use_visa_requirements: bool = Field(True, description="Use visa requirements RAG (RECOMMENDED)")
    use_examples: bool = Field(True, description="Use example letters RAG")
    max_word_count: int = Field(500, ge=200, le=1000, description="Max words")
    temperature: float = Field(0.7, ge=0.0, le=1.0, description="LLM temperature")


# === Unified Endpoint Models ===

class CompletePackageRequest(BaseModel):
    """Request for complete application package (checklist + cover letter)."""
    user_profile: UnifiedUserProfile = Field(..., description="Complete user profile")
    target_url: str = Field(..., description="Official visa website URL", example="https://travel.state.gov/content/travel/en/us-visas/tourism-visit/visitor.html")
    generate_checklist: bool = Field(True, description="Generate visa checklist")
    generate_cover_letter: bool = Field(True, description="Generate cover letter")
    use_rag: bool = Field(True, description="Use RAG for both generations")
    force_refresh: bool = Field(False, description="Force fresh scraping, bypass cache")
    temperature: float = Field(0.7, ge=0.0, le=1.0, description="LLM temperature")


class CompletePackageResponse(BaseModel):
    """Response for complete application package."""
    success: bool = Field(..., description="Overall success status")
    checklist: Optional[Dict[str, Any]] = Field(None, description="Generated checklist")
    cover_letter: Optional[Dict[str, Any]] = Field(None, description="Generated cover letter")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Metadata")
    warnings: List[str] = Field(default_factory=list, description="Warnings")
    error_message: Optional[str] = Field(None, description="Error if failed")


# === Generic Response Models ===

class APIResponse(BaseModel):
    """Generic API response wrapper."""
    success: bool = Field(..., description="Request success status")
    data: Optional[Dict[str, Any]] = Field(None, description="Response data")
    error: Optional[str] = Field(None, description="Error message")
    error_type: Optional[str] = Field(None, description="Error type")


__all__ = [
    'GenerateChecklistRequest',
    'ScrapeVisaInfoRequest',
    'GenerateCoverLetterRequest',
    'CompletePackageRequest',
    'CompletePackageResponse',
    'APIResponse',
]

