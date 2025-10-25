"""
Visa Requirement Management API Endpoints
Handles visa requirements and templates for different countries
"""

from fastapi import APIRouter, HTTPException, status, Depends, Query
from app.core.firebase import db
from app.models.schemas import (
    VisaRequirementResponse, VisaRequirementInDB, ChecklistTemplateResponse
)
from app.services.security import get_current_user, UserInDB
from typing import List, Optional
import logging

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/visa-requirements", response_model=List[VisaRequirementResponse])
async def get_visa_requirements(
    current_user: UserInDB = Depends(get_current_user),
    origin_country: Optional[str] = Query(None, description="Filter by origin country"),
    destination_country: Optional[str] = Query(None, description="Filter by destination country"),
    limit: int = Query(50, ge=1, le=100, description="Number of results to return")
):
    """
    Get visa requirements with optional filtering
    """
    try:
        # Build query
        query = db.collection("VISA_REQUIREMENT")
        
        # Apply filters
        if origin_country:
            query = query.where("originCountry", "==", origin_country.upper())
        
        if destination_country:
            query = query.where("destinationCode", "==", destination_country.upper())
        
        # Execute query
        docs = query.limit(limit).stream()
        
        requirements = []
        for doc in docs:
            req_data = doc.to_dict()
            requirements.append(VisaRequirementResponse(**req_data))
        
        return requirements
        
    except Exception as e:
        logger.error(f"Error getting visa requirements: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get visa requirements"
        )


@router.get("/visa-requirements/{req_id}", response_model=VisaRequirementResponse)
async def get_visa_requirement(
    req_id: str,
    current_user: UserInDB = Depends(get_current_user)
):
    """
    Get a specific visa requirement by ID
    """
    try:
        # Get visa requirement document
        req_doc = db.collection("VISA_REQUIREMENT").document(req_id).get()
        
        if not req_doc.exists:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Visa requirement not found"
            )
        
        req_data = req_doc.to_dict()
        return VisaRequirementResponse(**req_data)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting visa requirement: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get visa requirement"
        )


@router.get("/visa-requirements/{req_id}/templates", response_model=List[ChecklistTemplateResponse])
async def get_visa_requirement_templates(
    req_id: str,
    current_user: UserInDB = Depends(get_current_user),
    category: Optional[str] = Query(None, description="Filter by template category"),
    mandatory_only: Optional[bool] = Query(None, description="Filter only mandatory templates"),
    profile_type: Optional[str] = Query(None, description="Filter by profile type")
):
    """
    Get checklist templates for a specific visa requirement
    """
    try:
        # Verify visa requirement exists
        req_doc = db.collection("VISA_REQUIREMENT").document(req_id).get()
        if not req_doc.exists:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Visa requirement not found"
            )
        
        # Get templates from CHECKLIST_TEMPLATE collection
        templates_query = db.collection("CHECKLIST_TEMPLATE")
        
        # Apply filters
        if category:
            templates_query = templates_query.where("category", "==", category)
        
        if mandatory_only:
            templates_query = templates_query.where("mandatory", "==", True)
        
        # Execute query
        docs = templates_query.stream()
        
        templates = []
        for doc in docs:
            template_data = doc.to_dict()
            template_data["check_id"] = doc.id
            
            # Apply profile type filter
            if profile_type:
                required_for = template_data.get("requiredFor", [])
                if (profile_type.upper() not in required_for and 
                    "ALL" not in required_for and 
                    required_for):  # If required_for is not empty
                    continue
            
            templates.append(ChecklistTemplateResponse(**template_data))
        
        # Sort by priority
        templates.sort(key=lambda x: x.priority)
        
        return templates
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting visa requirement templates: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get visa requirement templates"
        )


@router.get("/visa-requirements/{req_id}/templates/{template_id}", response_model=ChecklistTemplateResponse)
async def get_checklist_template(
    req_id: str,
    template_id: str,
    current_user: UserInDB = Depends(get_current_user)
):
    """
    Get a specific checklist template
    """
    try:
        # Verify visa requirement exists
        req_doc = db.collection("VISA_REQUIREMENT").document(req_id).get()
        if not req_doc.exists:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Visa requirement not found"
            )
        
        # Get template document from CHECKLIST_TEMPLATE collection
        template_doc = db.collection("CHECKLIST_TEMPLATE").document(template_id).get()
        
        if not template_doc.exists:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Checklist template not found"
            )
        
        template_data = template_doc.to_dict()
        template_data["check_id"] = template_doc.id
        
        return ChecklistTemplateResponse(**template_data)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting checklist template: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get checklist template"
        )


@router.get("/visa-requirements/search", response_model=List[VisaRequirementResponse])
async def search_visa_requirements(
    current_user: UserInDB = Depends(get_current_user),
    origin_country: str = Query(..., description="Origin country code"),
    destination_country: str = Query(..., description="Destination country code"),
    passport_type: Optional[str] = Query(None, description="Passport type filter")
):
    """
    Search for visa requirements between specific countries
    """
    try:
        # Build query
        query = db.collection("VISA_REQUIREMENT").where(
            "originCountry", "==", origin_country.upper()
        ).where(
            "destinationCode", "==", destination_country.upper()
        )
        
        # Execute query
        docs = query.stream()
        
        requirements = []
        for doc in docs:
            req_data = doc.to_dict()
            
            # Apply passport type filter if provided
            if passport_type:
                applicable_passport_types = req_data.get("applicablePassportTypes", [])
                if passport_type.upper() not in applicable_passport_types:
                    continue
            
            requirements.append(VisaRequirementResponse(**req_data))
        
        return requirements
        
    except Exception as e:
        logger.error(f"Error searching visa requirements: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to search visa requirements"
        )


@router.get("/visa-requirements/{req_id}/letter-templates", response_model=List[str])
async def get_letter_templates(
    req_id: str,
    current_user: UserInDB = Depends(get_current_user)
):
    """
    Get letter templates for a visa requirement
    """
    try:
        # Get visa requirement document
        req_doc = db.collection("VISA_REQUIREMENT").document(req_id).get()
        
        if not req_doc.exists:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Visa requirement not found"
            )
        
        req_data = req_doc.to_dict()
        letter_templates = req_data.get("letterTemplate", [])
        
        return letter_templates
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting letter templates: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get letter templates"
        )


@router.get("/visa-requirements/stats", response_model=dict)
async def get_visa_requirement_stats(
    current_user: UserInDB = Depends(get_current_user)
):
    """
    Get visa requirement statistics
    """
    try:
        # Get all visa requirements
        docs = db.collection("VISA_REQUIREMENT").stream()
        
        total_requirements = 0
        requirements_by_origin = {}
        requirements_by_destination = {}
        
        for doc in docs:
            req_data = doc.to_dict()
            total_requirements += 1
            
            # Count by origin country
            origin = req_data.get("originCountry", "unknown")
            requirements_by_origin[origin] = requirements_by_origin.get(origin, 0) + 1
            
            # Count by destination country
            destination = req_data.get("destinationCode", "unknown")
            requirements_by_destination[destination] = requirements_by_destination.get(destination, 0) + 1
        
        return {
            "total_requirements": total_requirements,
            "requirements_by_origin": requirements_by_origin,
            "requirements_by_destination": requirements_by_destination,
            "top_origins": sorted(requirements_by_origin.items(), key=lambda x: x[1], reverse=True)[:5],
            "top_destinations": sorted(requirements_by_destination.items(), key=lambda x: x[1], reverse=True)[:5]
        }
        
    except Exception as e:
        logger.error(f"Error getting visa requirement stats: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get visa requirement statistics"
        )