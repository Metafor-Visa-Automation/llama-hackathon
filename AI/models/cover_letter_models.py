"""
Cover letter models for generation.
Adapted from Cover-letter project.
"""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, field_validator
from datetime import datetime

# Import shared types from user_profile (DRY principle)
from .user_profile import VisaType


class CoverLetterResponse(BaseModel):
    """Structured response for generated cover letter."""
    
    title: str = Field(
        ...,
        description="Cover letter title",
        min_length=5,
        max_length=200
    )
    
    salutation: str = Field(
        default="Dear Visa Officer,",
        description="Opening salutation"
    )
    
    introduction: str = Field(
        ...,
        description="Introduction paragraph",
        min_length=50
    )
    
    body_paragraphs: List[str] = Field(
        ...,
        description="Main body paragraphs",
        min_length=2,
        max_length=8
    )
    
    conclusion: str = Field(
        ...,
        description="Conclusion paragraph",
        min_length=50
    )
    
    closing: str = Field(
        default="Sincerely,",
        description="Closing phrase"
    )
    
    key_points: Optional[List[str]] = Field(
        default_factory=list,
        description="Key points emphasized in the letter",
        max_length=10
    )
    
    tone: str = Field(
        default="professional",
        description="Overall tone of the letter"
    )
    
    word_count: Optional[int] = Field(
        None,
        description="Total word count"
    )
    
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional metadata"
    )
    
    @field_validator('body_paragraphs')
    @classmethod
    def validate_body_paragraphs(cls, v):
        """Ensure each body paragraph has sufficient content."""
        for paragraph in v:
            if len(paragraph.strip()) < 30:
                raise ValueError("Each body paragraph must be at least 30 characters")
        return v
    
    def to_full_text(self) -> str:
        """Convert structured response to full text format."""
        parts = [
            self.title,
            "",
            self.salutation,
            "",
            self.introduction,
            ""
        ]
        
        for paragraph in self.body_paragraphs:
            parts.append(paragraph)
            parts.append("")
        
        parts.extend([
            self.conclusion,
            "",
            self.closing
        ])
        
        return "\n".join(parts)


class ExampleCoverLetter(BaseModel):
    """Example cover letter retrieved from vector database."""
    
    id: str = Field(..., description="Unique identifier")
    
    content: str = Field(..., description="Cover letter content")
    
    country: str = Field(..., description="Target country")
    
    visa_type: str = Field(..., description="Visa type")
    
    approved: bool = Field(
        default=False,
        description="Whether this example was approved"
    )
    
    similarity_score: Optional[float] = Field(
        None,
        description="Similarity score from vector search"
    )
    
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional metadata"
    )


class GenerationMetadata(BaseModel):
    """Metadata about the generation process."""
    
    timestamp: datetime = Field(
        default_factory=datetime.utcnow,
        description="Generation timestamp"
    )
    
    model_used: str = Field(..., description="LLM model used")
    
    examples_used: int = Field(
        default=0,
        description="Number of example letters used"
    )
    
    visa_requirements_used: int = Field(
        default=0,
        description="Number of visa requirements used as context"
    )
    
    generation_time_seconds: Optional[float] = Field(
        None,
        description="Time taken to generate"
    )
    
    retry_count: int = Field(
        default=0,
        description="Number of retries"
    )
    
    data_sources: Dict[str, Any] = Field(
        default_factory=dict,
        description="Data sources used (RAG collections, etc.)"
    )


class CoverLetterGenerationResponse(BaseModel):
    """Complete response for cover letter generation."""
    
    success: bool = Field(..., description="Whether generation was successful")
    
    cover_letter: Optional[CoverLetterResponse] = Field(
        None,
        description="Generated cover letter"
    )
    
    metadata: GenerationMetadata = Field(
        ...,
        description="Generation metadata"
    )
    
    error_message: Optional[str] = Field(
        None,
        description="Error message if generation failed"
    )
    
    warnings: List[str] = Field(
        default_factory=list,
        description="Any warnings during generation"
    )

