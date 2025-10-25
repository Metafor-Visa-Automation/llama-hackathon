from fastapi import APIRouter, HTTPException, status, Depends, Query
from app.core.firebase import db
from app.models.schemas import (
    VisaRequirementResponse, VisaRequirementInDB,
    ApplicationResponse, ApplicationInDB, ApplicationStatus
)
from app.services.security import get_current_user, UserInDB
from typing import List, Optional
from datetime import datetime

router = APIRouter()


@router.get("/", response_model=List[VisaRequirementResponse])
async def get_visa_requirements(
    origin_country: Optional[str] = Query(None, description="Filter by origin country code"),
    destination_country: Optional[str] = Query(None, description="Filter by destination country code"),
    passport_type: Optional[str] = Query(None, description="Filter by passport type (BORDO/YESIL)"),
    visa_type: Optional[str] = Query(None, description="Filter by visa requirement type"),
    limit: int = Query(50, ge=1, le=100, description="Number of results to return")
):
    """
    Get visa requirements with optional filtering
    """
    try:
        query = db.collection('VISA_REQUIREMENT')
        
        # Apply filters
        if origin_country:
            query = query.where('originCountry', '==', origin_country.upper())
        if destination_country:
            query = query.where('destinationCode', '==', destination_country.upper())
        if passport_type:
            query = query.where('applicablePassportTypes', 'array_contains', passport_type.upper())
        if visa_type:
            query = query.where('visaRequirementType', '==', visa_type.upper())
        
        # Execute query with limit
        docs = query.limit(limit).stream()
        
        requirements = []
        for doc in docs:
            data = doc.to_dict()
            requirements.append(VisaRequirementResponse(
                req_id=data['reqId'],
                origin_country=data.get('originCountry', ''),
                destination_code=data.get('destinationCode', ''),
                applicable_passport_types=data.get('applicablePassportTypes', []),
                visa_requirement_type=data.get('visaRequirementType', 'VISA_REQUIRED'),
                visa_name=data.get('visaName', 'Unknown'),
                visa_fee=data.get('visaFee'),
                passport_validity=data.get('passportValidity'),
                application_link=data.get('applicationLink'),
                embassy_url=data.get('embassyUrl'),
                letter_template=data.get('letterTemplate', []),
                created_at=data.get('createdAt', datetime.utcnow()),
                updated_at=data.get('updatedAt', datetime.utcnow()),
                last_verified_at=data.get('lastVerifiedAt', datetime.utcnow())
            ))
        
        return requirements
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch visa requirements: {str(e)}"
        )


@router.get("/{req_id}", response_model=VisaRequirementResponse)
async def get_visa_requirement(req_id: str):
    """
    Get a specific visa requirement by ID
    """
    try:
        doc = db.collection('VISA_REQUIREMENT').document(req_id).get()
        if not doc.exists:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Visa requirement not found"
            )
        
        data = doc.to_dict()
        return VisaRequirementResponse(
            req_id=data['reqId'],
            origin_country=data['originCountry'],
            destination_code=data['destinationCode'],
            applicable_passport_types=data['applicablePassportTypes'],
            visa_requirement_type=data['visaRequirementType'],
            visa_name=data.get('visaName', 'Unknown'),
            visa_fee=data.get('visaFee'),
            passport_validity=data.get('passportValidity'),
            application_link=data.get('applicationLink'),
            embassy_url=data.get('embassyUrl'),
            letter_template=data.get('letterTemplate', []),
            created_at=data['createdAt'],
            updated_at=data['updatedAt'],
            last_verified_at=data['lastVerifiedAt']
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch visa requirement: {str(e)}"
        )


@router.get("/search", response_model=List[VisaRequirementResponse])
async def search_visa_requirements(
    q: str = Query(..., description="Search query for country names or visa types"),
    limit: int = Query(20, ge=1, le=50, description="Number of results to return")
):
    """
    Search visa requirements by country names or visa types
    """
    try:
        # This is a simplified search - in production, you might want to use
        # a more sophisticated search solution like Algolia or Elasticsearch
        query = db.collection('VISA_REQUIREMENT')
        docs = query.limit(limit).stream()
        
        results = []
        search_terms = q.lower().split()
        
        for doc in docs:
            data = doc.to_dict()
            
            # Simple text matching
            searchable_text = f"{data.get('originCountry', '')} {data.get('destinationCode', '')} {data.get('visaName', '')}".lower()
            
            if any(term in searchable_text for term in search_terms):
                results.append(VisaRequirementResponse(
                    req_id=data.get('reqId', ''),
                    origin_country=data.get('originCountry', ''),
                    destination_code=data.get('destinationCode', ''),
                    applicable_passport_types=data.get('applicablePassportTypes', []),
                    visa_requirement_type=data.get('visaRequirementType', 'VISA_REQUIRED'),
                    visa_name=data.get('visaName', 'Unknown'),
                    visa_fee=data.get('visaFee'),
                    passport_validity=data.get('passportValidity'),
                    application_link=data.get('applicationLink'),
                    embassy_url=data.get('embassyUrl'),
                    letter_template=data.get('letterTemplate', []),
                    created_at=data['createdAt'],
                    updated_at=data['updatedAt'],
                    last_verified_at=data['lastVerifiedAt']
                ))
        
        return results[:limit]
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Search failed: {str(e)}"
        )


@router.get("/{req_id}/checklist-templates")
async def get_checklist_templates(req_id: str):
    """
    Get checklist templates for a specific visa requirement
    """
    try:
        # Verify the requirement exists
        req_doc = db.collection('VISA_REQUIREMENT').document(req_id).get()
        if not req_doc.exists:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Visa requirement not found"
            )
        
        # Get checklist templates
        templates_query = db.collection('VISA_REQUIREMENT').document(req_id).collection('CHECKLIST_TEMPLATE').stream()
        
        templates = []
        for template in templates_query:
            template_data = template.to_dict()
            template_data['template_id'] = template.id
            templates.append(template_data)
        
        return {
            "requirement_id": req_id,
            "templates": templates,
            "count": len(templates)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch checklist templates: {str(e)}"
        )
