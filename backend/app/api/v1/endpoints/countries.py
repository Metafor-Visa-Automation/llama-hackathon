from fastapi import APIRouter, HTTPException, status, Query
from app.core.firebase import db
from typing import List, Optional
from pydantic import BaseModel

router = APIRouter()


class CountryResponse(BaseModel):
    country_code: str
    name: str
    schengen_member: bool


@router.get("/", response_model=List[CountryResponse])
async def get_countries(
    schengen_only: Optional[bool] = Query(None, description="Filter only Schengen countries"),
    search: Optional[str] = Query(None, description="Search by country name"),
    limit: int = Query(50, ge=1, le=200, description="Number of results to return")
):
    """
    Get list of countries with optional filtering
    """
    try:
        query = db.collection('COUNTRY')
        
        # Apply filters
        if schengen_only is not None:
            query = query.where('schengenMember', '==', schengen_only)
        
        # Execute query
        docs = query.limit(limit).stream()
        
        countries = []
        for doc in docs:
            data = doc.to_dict()
            
            # Apply search filter if provided
            if search:
                if search.lower() not in data['name'].lower():
                    continue
            
            countries.append(CountryResponse(
                country_code=data['countryCode'],
                name=data['name'],
                schengen_member=data['schengenMember']
            ))
        
        return countries
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch countries: {str(e)}"
        )


@router.get("/schengen", response_model=List[CountryResponse])
async def get_schengen_countries():
    """
    Get all Schengen countries
    """
    try:
        docs = db.collection('COUNTRY').where('schengenMember', '==', True).stream()
        
        countries = []
        for doc in docs:
            data = doc.to_dict()
            countries.append(CountryResponse(
                country_code=data['countryCode'],
                name=data['name'],
                schengen_member=data['schengenMember']
            ))
        
        return countries
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch Schengen countries: {str(e)}"
        )


@router.get("/{country_code}", response_model=CountryResponse)
async def get_country(country_code: str):
    """
    Get a specific country by country code
    """
    try:
        doc = db.collection('COUNTRY').document(country_code.upper()).get()
        if not doc.exists:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Country not found"
            )
        
        data = doc.to_dict()
        return CountryResponse(
            country_code=data['countryCode'],
            name=data['name'],
            schengen_member=data['schengenMember']
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch country: {str(e)}"
        )
