"""
Visa-related models for checklist generation.
Adapted from MCP project.
"""

from datetime import datetime
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

# Import shared types from user_profile (DRY principle)
from .user_profile import VisaType, TravelDates


class VisaRequirement(BaseModel):
    """A single visa requirement."""
    requirement_id: str = Field(..., description="Unique requirement identifier")
    title: str = Field(..., description="Requirement title")
    description: str = Field(..., description="Detailed description")
    category: str = Field(..., description="Category (e.g., 'documents', 'financial', 'personal')")
    mandatory: bool = Field(True, description="Whether this requirement is mandatory")
    applicable_to: Optional[List[str]] = Field(
        default_factory=list,
        description="Specific cases this applies to (e.g., certain visa types)"
    )
    notes: Optional[str] = Field(None, description="Additional notes or tips")
    
    class Config:
        json_schema_extra = {
            "example": {
                "requirement_id": "req_001",
                "title": "Valid Passport",
                "description": "Passport valid for at least 3 months beyond intended stay",
                "category": "documents",
                "mandatory": True,
                "notes": "Must have at least 2 blank pages"
            }
        }


class ActionStep(BaseModel):
    """An actionable step for a visa requirement (simplified - only 6 fields)."""
    step_id: str = Field(..., description="Unique step identifier (e.g., 'step_001')")
    title: str = Field(..., description="Short, clear title of the action step (max 100 chars)")
    description: str = Field(
        ..., 
        description="Detailed 1-2 sentence description explaining what needs to be done"
    )
    priority_score: int = Field(
        ...,
        ge=1,
        le=5,
        description="Priority score 1-5: 5=urgent/first priority, 1=optional"
    )
    requires_document: bool = Field(
        ...,
        description="Whether this step requires PDF/document upload (drag-and-drop)"
    )
    source_urls: List[str] = Field(
        default_factory=list,
        description="URLs where this requirement information was found"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "step_id": "step_001",
                "title": "Pasaport Geçerlilik Kontrolü",
                "description": "Pasaportunuzun hedef ülkeye gidiş tarihinden itibaren en az 6 ay geçerli olması gerekir.",
                "priority_score": 5,
                "requires_document": True,
                "source_urls": ["https://france-visas.gouv.fr"]
            }
        }




class StepsResponse(BaseModel):
    """Response containing actionable visa preparation steps."""
    success: bool = Field(..., description="Whether step generation was successful")
    action_steps: List[ActionStep] = Field(
        default_factory=list,
        description="List of actionable steps sorted by priority"
    )
    total_steps: int = Field(0, description="Total number of steps generated")
    steps_requiring_documents: int = Field(
        0, 
        description="Number of steps that require document handling"
    )
    estimated_total_time: str = Field(
        "N/A", 
        description="Total estimated time to complete all steps"
    )
    estimated_total_cost: Optional[str] = Field(
        None, 
        description="Total estimated cost for all steps"
    )
    grouped_by_priority: Dict[str, List[str]] = Field(
        default_factory=dict,
        description="Step IDs grouped by priority score (5: urgent, 4: high, 3: medium, 2: low, 1: optional)"
    )
    grouped_by_category: Optional[Dict[str, List[str]]] = Field(
        default_factory=dict,
        description="Step IDs grouped by category (documents, financial, personal, medical, administrative) - OPTIONAL"
    )
    source_urls: List[str] = Field(
        default_factory=list,
        description="All source URLs where requirements were found"
    )
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Metadata about the generation process"
    )
    warnings: Optional[List[str]] = Field(
        default_factory=list,
        description="Important warnings or notices"
    )
    error_message: Optional[str] = Field(
        None, 
        description="Error message if success=False"
    )
    summary: str = Field(
        "", 
        description="Brief summary of the visa preparation process in Turkish"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "action_steps": [],
                "total_steps": 15,
                "mandatory_steps": 12,
                "optional_steps": 3,
                "steps_requiring_documents": 10,
                "estimated_total_time": "2-3 hafta",
                "estimated_total_cost": "€200-300",
                "grouped_by_priority": {
                    "5": ["step_001", "step_002"],
                    "4": ["step_003", "step_004", "step_005"]
                },
                "grouped_by_category": {
                    "documents": ["step_001", "step_002"],
                    "financial": ["step_003"]
                },
                "source_urls": [
                    "https://france-visas.gouv.fr",
                    "https://www.vizesizgezi.com/fransa"
                ],
                "metadata": {
                    "generation_time": 2.5,
                    "model_used": "llama3.1:8b",
                    "data_source": "scraped_live"
                },
                "summary": "Fransa turist vizesi için 15 adım belirlendi. Toplam süre 2-3 hafta, maliyet €200-300 arası."
            }
        }




class ScrapedData(BaseModel):
    """Data scraped from visa website."""
    country: str = Field(..., description="Country code (e.g., 'france')")
    visa_type: str = Field(..., description="Visa type")
    requirements: List[VisaRequirement] = Field(
        default_factory=list,
        description="List of requirements"
    )
    application_steps: Optional[List[str]] = Field(
        default_factory=list,
        description="Step-by-step application process"
    )
    processing_time: Optional[str] = Field(None, description="Expected processing time")
    fees: Optional[Dict[str, Any]] = Field(None, description="Visa fees information")
    source_url: str = Field(..., description="Source URL of the data")
    scraped_at: datetime = Field(
        default_factory=datetime.now,
        description="Timestamp of scraping"
    )
    data_source: str = Field(
        default="scraped_live",
        description="Data source: 'scraped_live', 'cached', 'scraping_failed_no_data', 'scraping_failed_error', 'scraping_failed_exception'"
    )
    scraping_warnings: List[str] = Field(
        default_factory=list,
        description="Warnings or issues encountered during scraping"
    )
    additional_info: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description="Additional scraped information"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "country": "france",
                "visa_type": "tourist",
                "requirements": [],
                "application_steps": [
                    "Complete online application",
                    "Book appointment",
                    "Submit documents"
                ],
                "processing_time": "15 days",
                "source_url": "https://france-visas.gouv.fr",
                "scraped_at": "2024-01-15T10:30:00"
            }
        }

