"""
Country Management API Endpoints
Handles country information and Schengen membership data
"""

from fastapi import APIRouter, HTTPException, status, Depends, Query
from app.core.firebase import db
from app.models.schemas import CountryResponse, CountryInDB
from app.services.security import get_current_user, UserInDB
from typing import List, Optional
import logging

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/countries", response_model=List[CountryResponse])
async def get_countries(
    current_user: UserInDB = Depends(get_current_user),
    schengen_only: Optional[bool] = Query(None, description="Filter only Schengen countries"),
    search: Optional[str] = Query(None, description="Search countries by name"),
    limit: int = Query(100, ge=1, le=200, description="Number of results to return")
):
    """
    Get list of countries with optional filtering
    """
    try:
        # Build query
        query = db.collection("COUNTRY")
        
        # Apply filters
        if schengen_only is not None:
            query = query.where("schengenMember", "==", schengen_only)
        
        # Execute query
        docs = query.limit(limit).stream()
        
        countries = []
        for doc in docs:
            country_data = doc.to_dict()
            
            # Apply search filter if provided
            if search is None or search.lower() in country_data.get("name", "").lower():
                countries.append(CountryResponse(**country_data))
        
        # Sort by name
        countries.sort(key=lambda x: x.name)
        
        return countries
        
    except Exception as e:
        logger.error(f"Error getting countries: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get countries"
        )


@router.get("/countries/{country_code}", response_model=CountryResponse)
async def get_country(
    country_code: str,
    current_user: UserInDB = Depends(get_current_user)
):
    """
    Get a specific country by country code
    """
    try:
        # Get country document
        country_doc = db.collection("COUNTRY").document(country_code.upper()).get()
        
        if not country_doc.exists:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Country not found"
            )
        
        country_data = country_doc.to_dict()
        return CountryResponse(**country_data)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting country: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get country"
        )


@router.get("/countries/schengen/list", response_model=List[CountryResponse])
async def get_schengen_countries(
    current_user: UserInDB = Depends(get_current_user)
):
    """
    Get list of Schengen countries
    """
    try:
        # Query Schengen countries
        docs = db.collection("COUNTRY").where("schengenMember", "==", True).stream()
        
        countries = []
        for doc in docs:
            country_data = doc.to_dict()
            countries.append(CountryResponse(**country_data))
        
        # Sort by name
        countries.sort(key=lambda x: x.name)
        
        return countries
        
    except Exception as e:
        logger.error(f"Error getting Schengen countries: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get Schengen countries"
        )


@router.get("/countries/stats", response_model=dict)
async def get_country_stats(
    current_user: UserInDB = Depends(get_current_user)
):
    """
    Get country statistics
    """
    try:
        # Get all countries
        docs = db.collection("COUNTRY").stream()
        
        total_countries = 0
        schengen_countries = 0
        non_schengen_countries = 0
        
        for doc in docs:
            country_data = doc.to_dict()
            total_countries += 1
            
            if country_data.get("schengenMember", False):
                schengen_countries += 1
            else:
                non_schengen_countries += 1
        
        return {
            "total_countries": total_countries,
            "schengen_countries": schengen_countries,
            "non_schengen_countries": non_schengen_countries,
            "schengen_percentage": round((schengen_countries / total_countries) * 100, 2) if total_countries > 0 else 0
        }
        
    except Exception as e:
        logger.error(f"Error getting country stats: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get country statistics"
        )