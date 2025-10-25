"""
Checklist Template Management API Endpoints
Handles checklist templates for visa applications
"""

from fastapi import APIRouter, HTTPException, status, Depends, Query
from app.core.firebase import db
from app.models.schemas import ChecklistTemplateResponse
from app.services.security import get_current_user, UserInDB
from typing import List, Optional
import logging

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/checklist-templates", response_model=List[ChecklistTemplateResponse])
async def get_checklist_templates(
    current_user: UserInDB = Depends(get_current_user),
    category: Optional[str] = Query(None, description="Filter by template category"),
    mandatory_only: Optional[bool] = Query(None, description="Filter only mandatory templates"),
    required_for: Optional[str] = Query(None, description="Filter by required for (e.g., TOURIST, BUSINESS)"),
    limit: int = Query(50, ge=1, le=100, description="Number of results to return")
):
    """
    Get all checklist templates with optional filtering
    """
    try:
        # Build query
        templates_query = db.collection("CHECKLIST_TEMPLATE")
        
        # Apply filters
        if category:
            templates_query = templates_query.where("category", "==", category)
        
        if mandatory_only:
            templates_query = templates_query.where("mandatory", "==", True)
        
        # Execute query
        docs = templates_query.limit(limit).stream()
        
        templates = []
        for doc in docs:
            template_data = doc.to_dict()
            template_data["checkId"] = doc.id
            
            # Apply required_for filter if provided
            if required_for:
                required_for_list = template_data.get("requiredFor", [])
                if (required_for.upper() not in required_for_list and 
                    "ALL" not in required_for_list and 
                    required_for_list):  # If required_for is not empty
                    continue
            
            templates.append(ChecklistTemplateResponse(**template_data))
        
        # Sort by priority
        templates.sort(key=lambda x: x.priority)
        
        return templates
        
    except Exception as e:
        logger.error(f"Error getting checklist templates: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get checklist templates"
        )


@router.get("/checklist-templates/{template_id}", response_model=ChecklistTemplateResponse)
async def get_checklist_template(
    template_id: str,
    current_user: UserInDB = Depends(get_current_user)
):
    """
    Get a specific checklist template by ID
    """
    try:
        # Get template document
        template_doc = db.collection("CHECKLIST_TEMPLATE").document(template_id).get()
        
        if not template_doc.exists:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Checklist template not found"
            )
        
        template_data = template_doc.to_dict()
        template_data["checkId"] = template_doc.id
        
        return ChecklistTemplateResponse(**template_data)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting checklist template: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get checklist template"
        )


@router.get("/checklist-templates/categories", response_model=List[str])
async def get_template_categories(
    current_user: UserInDB = Depends(get_current_user)
):
    """
    Get all available template categories
    """
    try:
        # Get all templates
        docs = db.collection("CHECKLIST_TEMPLATE").stream()
        
        categories = set()
        for doc in docs:
            template_data = doc.to_dict()
            category = template_data.get("category")
            if category:
                categories.add(category)
        
        return sorted(list(categories))
        
    except Exception as e:
        logger.error(f"Error getting template categories: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get template categories"
        )


@router.get("/checklist-templates/by-category/{category}", response_model=List[ChecklistTemplateResponse])
async def get_templates_by_category(
    category: str,
    current_user: UserInDB = Depends(get_current_user),
    mandatory_only: Optional[bool] = Query(None, description="Filter only mandatory templates")
):
    """
    Get checklist templates by category
    """
    try:
        # Build query
        templates_query = db.collection("CHECKLIST_TEMPLATE").where("category", "==", category)
        
        if mandatory_only:
            templates_query = templates_query.where("mandatory", "==", True)
        
        # Execute query
        docs = templates_query.stream()
        
        templates = []
        for doc in docs:
            template_data = doc.to_dict()
            template_data["checkId"] = doc.id
            templates.append(ChecklistTemplateResponse(**template_data))
        
        # Sort by priority
        templates.sort(key=lambda x: x.priority)
        
        return templates
        
    except Exception as e:
        logger.error(f"Error getting templates by category: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get templates by category"
        )


@router.get("/checklist-templates/stats", response_model=dict)
async def get_template_stats(
    current_user: UserInDB = Depends(get_current_user)
):
    """
    Get checklist template statistics
    """
    try:
        # Get all templates
        docs = db.collection("CHECKLIST_TEMPLATE").stream()
        
        stats = {
            "total_templates": 0,
            "by_category": {},
            "mandatory_templates": 0,
            "optional_templates": 0,
            "by_required_for": {}
        }
        
        for doc in docs:
            template_data = doc.to_dict()
            stats["total_templates"] += 1
            
            # Count by category
            category = template_data.get("category", "unknown")
            stats["by_category"][category] = stats["by_category"].get(category, 0) + 1
            
            # Count mandatory/optional
            if template_data.get("mandatory", False):
                stats["mandatory_templates"] += 1
            else:
                stats["optional_templates"] += 1
            
            # Count by required_for
            required_for_list = template_data.get("requiredFor", [])
            for req in required_for_list:
                stats["by_required_for"][req] = stats["by_required_for"].get(req, 0) + 1
        
        return stats
        
    except Exception as e:
        logger.error(f"Error getting template stats: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get template statistics"
        )

