"""
Unified HTTP REST API Server with FastAPI.
Exposes 9 endpoints: 5 visa + 3 cover letter + 1 unified.
"""

import time
import asyncio
from contextlib import asynccontextmanager
from typing import Dict, Any, List

from fastapi import FastAPI, HTTPException, status, Query
from fastapi.middleware.cors import CORSMiddleware

from config import ServiceFactory, settings
from config.country_urls import get_country_urls, is_country_supported
from api_models import (
    GenerateChecklistRequest,
    ScrapeVisaInfoRequest,
    GenerateCoverLetterRequest,
    CompletePackageRequest,
    CompletePackageResponse,
    APIResponse
)
from models.user_profile import VisaType
from utils import logger


# Application lifespan management
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize services on startup and cleanup on shutdown."""
    logger.info("🚀 API Server starting up...")
    try:
        # Initialize all services
        ServiceFactory.initialize_all_services()
        logger.info("✅ All services ready")
        yield
    finally:
        logger.info("👋 API Server shutting down...")
        await ServiceFactory.close_all()
        logger.info("✅ Shutdown complete")


# FastAPI app
app = FastAPI(
    title="Unified Visa AI API",
    description="Complete visa application preparation with checklist and cover letter generation",
    version="1.0.1",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.API_CORS_ORIGINS] if settings.API_CORS_ORIGINS != "*" else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# === Health & Info Endpoints ===

@app.get("/health", tags=["System"])
async def health_check():
    """Health check endpoint."""
    return {"status": "ok", "message": "Unified Visa AI API is running"}


@app.get("/", tags=["System"])
async def root():
    """Root endpoint with API information."""
    return {
        "name": "Unified Visa AI API",
        "version": "1.0.1",
        "endpoints": {
            "visa": 6,
            "cover_letter": 3,
            "unified": 1
        },
        "docs": "/docs",
        "health": "/health"
    }


# === VISA ENDPOINTS (5) ===

@app.post("/api/v1/visa/generate-checklist", tags=["Visa"])
async def generate_visa_checklist(request: GenerateChecklistRequest):
    """
    Generate personalized visa checklist with RAG.

    Uses visa requirements RAG to find similar successful applications.
    
    Note: target_urls is now optional. If not provided, URLs will be automatically
    determined based on destination_country from the predefined country mapping.

    Parameters:
    - destination_country: Target country (used to lookup URLs if target_urls not provided)
    - target_urls: Optional list of URLs. If not provided, uses country mapping
    - force_refresh: Set to true to bypass cache and scrape fresh data

    Response includes:
    - metadata.data_source: "scraped_live", "cached", etc.
    - warnings: List of issues encountered during scraping
    """
    try:
        # Resolve target_urls from country mapping if not provided
        target_urls = request.target_urls
        if not target_urls:
            target_urls = get_country_urls(request.destination_country)
            if not target_urls:
                raise HTTPException(
                    status_code=400,
                    detail=f"No predefined URLs found for '{request.destination_country}'. "
                           f"Please provide target_urls explicitly or add the country to the mapping."
                )
            logger.info(f"Using {len(target_urls)} predefined URLs for {request.destination_country}")
        
        generator = ServiceFactory.get_visa_prep_generator()

        result = await generator.generate_checklist(
            nationality=request.nationality,
            destination_country=request.destination_country,
            target_urls=target_urls,
            visa_type=request.visa_type,
            occupation=request.occupation or "Not specified",
            travel_purpose=request.travel_purpose,
            use_rag=request.use_rag,
            force_refresh=request.force_refresh,
            temperature=request.temperature
        )

        return result.model_dump()

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Checklist generation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/visa/generate-checklist/basic", tags=["Visa"])
async def generate_basic_checklist(request: GenerateChecklistRequest):
    """
    Generate simplified visa checklist with basic steps.
    
    Returns minimal format: only step titles and source URLs.
    Perfect for quick overview or mobile apps.
    
    Parameters:
    - force_refresh: Set to true to bypass cache and scrape fresh data
    
    Response format:
    {
      "success": true,
      "steps": [
        {
          "title": "Pasaport fotokopisi hazırlayın",
          "source_urls": ["https://example.com/visa-requirements"]
        }
      ],
      "total_steps": 15,
      "source_urls": ["https://example.com/visa-requirements"],
      "matching_enabled": false,
      "matched_pairs": [...],  // If matching enabled
      "matching_metadata": {...}  // If matching enabled
    }
    """
    try:
        from config.factory import ServiceFactory
        from prompts.visa_templates import BasicChecklistPromptBuilder
        
        # Get services
        scraper_service = ServiceFactory.get_scraper_service()
        llm_client = ServiceFactory.get_ollama_client()
        qdrant_service = ServiceFactory.get_qdrant_service()
        
        # Initialize prompt builder
        prompt_builder = BasicChecklistPromptBuilder()
        
        logger.info(
            f"Generating basic checklist for {request.nationality} -> "
            f"{request.destination_country} ({request.visa_type})"
        )
        
        # Step 1: Scrape visa requirements
        if len(request.target_urls) > 1:
            scraped_data = await scraper_service.get_visa_info_from_multiple_sources(
                country=request.destination_country,
                target_urls=request.target_urls,
                visa_type=request.visa_type,
                nationality=request.nationality,
                force_refresh=request.force_refresh
            )
        else:
            scraped_data = await scraper_service.get_visa_info(
                country=request.destination_country,
                target_url=request.target_urls[0],
                visa_type=request.visa_type,
                nationality=request.nationality,
                force_refresh=request.force_refresh
            )
        
        requirements = scraped_data.requirements or []
        application_steps = scraped_data.application_steps or []
        
        # Collect source URLs
        source_urls = scraped_data.source_urls if hasattr(scraped_data, 'source_urls') and scraped_data.source_urls else (
            [scraped_data.source_url] if scraped_data.source_url else []
        )
        
        # Check if we have any data
        if not requirements:
            logger.warning("No requirements scraped - using minimal data")
        
        logger.info(
            f"✓ Found {len(requirements)} requirements from {len(source_urls)} sources"
        )
        
        # Step 2: Generate with LLM
        messages = prompt_builder.build_messages(
            nationality=request.nationality,
            destination_country=request.destination_country,
            visa_type=request.visa_type,
            occupation=request.occupation or "Not specified",
            travel_purpose=request.travel_purpose,
            requirements=requirements,
            application_steps=application_steps,
            source_urls=source_urls
        )
        
        # JSON schema for basic checklist
        json_schema = {
            "type": "object",
            "properties": {
                "success": {"type": "boolean"},
                "steps": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "title": {"type": "string"},
                            "source_urls": {
                                "type": "array",
                                "items": {"type": "string"}
                            }
                        },
                        "required": ["title", "source_urls"]
                    }
                },
                "total_steps": {"type": "integer"},
                "source_urls": {
                    "type": "array",
                    "items": {"type": "string"}
                }
            },
            "required": ["success", "steps", "total_steps", "source_urls"]
        }
        
        # Generate with LLM
        response = await llm_client.generate_structured(
            messages=messages,
            response_format=json_schema,
            temperature=request.temperature
        )
        
        logger.info("✓ Basic checklist generated successfully")
        
        return response
        
    except Exception as e:
        logger.error(f"Basic checklist generation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/visa/scrape-info", tags=["Visa"])
async def scrape_visa_info(request: ScrapeVisaInfoRequest):
    """
    Scrape visa requirements from single or multiple official websites.

    Supports:
    - Single URL (backward compatible): use target_url
    - Multiple URLs (recommended): use target_urls for comprehensive data

    Results are cached for 24 hours unless force_refresh=true.

    Parameters:
    - target_url: Single URL (deprecated, use target_urls)
    - target_urls: List of URLs for multi-source scraping
    - force_refresh: Set to true to bypass cache and scrape fresh data

    Response includes:
    - data_source: "scraped_live", "scraped_live_merged", "cached", etc.
    - scraping_warnings: List of issues encountered
    - success: true if data was retrieved (even if from cache)
    
    Multiple URL Example:
    {
      "country": "france",
      "target_urls": [
        "https://france-visas.gouv.fr",
        "https://www.vizesizgezi.com/fransa",
        "https://vizepro.com.tr/fransa-vize"
      ],
      "visa_type": "tourist",
      "force_refresh": true
    }
    """
    try:
        scraper_service = ServiceFactory.get_scraper_service()
        
        # Check if multiple URLs provided
        if request.target_urls and len(request.target_urls) > 1:
            logger.info(f"Scraping from {len(request.target_urls)} sources...")
            
            # Use multiple sources method
            scraped_data = await scraper_service.get_visa_info_from_multiple_sources(
                country=request.country,
                target_urls=request.target_urls,
                visa_type=request.visa_type,
                nationality=request.nationality,
                force_refresh=request.force_refresh
            )
        else:
            # Single URL (backward compatible)
            single_url = request.target_urls[0] if request.target_urls else request.target_url
            logger.info(f"Scraping from single source: {single_url}")
            
            scraped_data = await scraper_service.get_visa_info(
                country=request.country,
                target_url=single_url,
                visa_type=request.visa_type,
                nationality=request.nationality,
                force_refresh=request.force_refresh
            )

        return {
            "success": len(scraped_data.requirements) > 0,
            "data": scraped_data.model_dump(),
            "data_source": scraped_data.data_source,
            "warnings": scraped_data.scraping_warnings,
            "sources_count": len(request.target_urls) if request.target_urls else 1
        }

    except Exception as e:
        logger.error(f"Scraping failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/visa/supported-countries", tags=["Visa"])
async def get_supported_countries():
    """Get list of supported countries for visa scraping."""
    from scrapers import ScraperRegistry
    return {
        "success": True,
        "countries": ScraperRegistry.get_supported_countries()
    }


@app.get("/api/v1/visa/types", tags=["Visa"])
async def get_visa_types():
    """Get list of supported visa types."""
    return {
        "success": True,
        "visa_types": [vt.value for vt in VisaType]
    }


@app.get("/api/v1/visa/cache-status", tags=["Visa"])
async def get_cache_status(
    country: str = Query(..., description="Country code"),
    visa_type: VisaType = Query(..., description="Visa type")
):
    """Get cache status for scraped visa data."""
    try:
        scraper_service = ServiceFactory.get_scraper_service()
        status_info = scraper_service.get_cache_status(country, visa_type)
        return {"success": True, "cache_status": status_info}
    except Exception as e:
        logger.error(f"Cache status check failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# === COVER LETTER ENDPOINTS (3) ===

@app.post("/api/v1/cover-letter/generate", tags=["Cover Letter"])
async def generate_cover_letter(request: GenerateCoverLetterRequest):
    """
    Generate professional cover letter with visa requirements context.
    
    KEY FEATURE: Uses visa requirements RAG to ensure cover letter
    specifically addresses what consulates want to see.
    """
    try:
        generator = ServiceFactory.get_cover_letter_generator()
        
        result = await generator.generate_cover_letter(
            user_profile=request.user_profile,
            use_visa_requirements=request.use_visa_requirements,
            use_examples=request.use_examples,
            max_word_count=request.max_word_count,
            temperature=request.temperature
        )
        
        return result.model_dump()
        
    except Exception as e:
        logger.error(f"Cover letter generation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/cover-letter/generate-with-requirements", tags=["Cover Letter"])
async def generate_cover_letter_with_requirements(request: GenerateCoverLetterRequest):
    """
    Enhanced cover letter generation ensuring visa requirements context is used.
    
    This endpoint always uses visa requirements RAG.
    """
    request.use_visa_requirements = True  # Force enable
    return await generate_cover_letter(request)


@app.get("/api/v1/cover-letter/examples", tags=["Cover Letter"])
async def get_cover_letter_examples(
    country: str = Query(..., description="Target country"),
    visa_type: VisaType = Query(..., description="Visa type"),
    limit: int = Query(5, ge=1, le=20, description="Number of examples")
):
    """
    Get example cover letters from database.
    
    Returns approved cover letters for reference.
    """
    try:
        qdrant_service = ServiceFactory.get_qdrant_service()
        await qdrant_service.connect()
        
        query_text = f"{visa_type.value} visa cover letter for {country}"
        examples = await qdrant_service.search_cover_letter_examples(
            query_text=query_text,
            country=country,
            visa_type=visa_type.value,
            limit=limit
        )
        
        return {"success": True, "examples": examples}
        
    except Exception as e:
        logger.error(f"Failed to retrieve examples: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# === UNIFIED ENDPOINT (1) - THE STAR! ===

@app.post("/api/v1/application/complete-package", tags=["Unified"])
async def generate_complete_package(request: CompletePackageRequest):
    """
    Generate COMPLETE visa application package: checklist AND cover letter!

    This is the main endpoint that showcases the full power of the system:
    - Generates personalized visa checklist
    - Generates cover letter with visa requirements context
    - Both use RAG for optimal results
    - Parallel execution for speed

    Parameters:
    - force_refresh: Set to true to bypass cache and scrape fresh data

    Returns everything needed for a visa application including:
    - data_source information
    - warnings from scraping process
    """
    start_time = time.time()
    warnings = []
    
    try:
        logger.info(f"🎯 Generating complete package for {request.user_profile.user_id}")
        
        # Prepare tasks
        tasks = []
        
        # Task 1: Generate checklist
        if request.generate_checklist:
            async def generate_checklist_task():
                try:
                    generator = ServiceFactory.get_visa_prep_generator()
                    return await generator.generate_checklist(
                        nationality=request.user_profile.nationality,
                        destination_country=request.user_profile.destination_country,
                        target_url=request.target_url,
                        visa_type=request.user_profile.visa_type,
                        occupation=request.user_profile.occupation,
                        travel_purpose=request.user_profile.travel_purpose,
                        use_rag=request.use_rag,
                        force_refresh=request.force_refresh,
                        temperature=request.temperature
                    )
                except Exception as e:
                    logger.error(f"Checklist generation error: {e}")
                    warnings.append(f"Checklist generation failed: {str(e)}")
                    return None

            tasks.append(("checklist", generate_checklist_task()))
        
        # Task 2: Generate cover letter
        if request.generate_cover_letter:
            async def generate_cover_letter_task():
                try:
                    generator = ServiceFactory.get_cover_letter_generator()
                    return await generator.generate_cover_letter(
                        user_profile=request.user_profile,
                        use_visa_requirements=True,  # Always use requirements
                        use_examples=True,
                        temperature=request.temperature
                    )
                except Exception as e:
                    logger.error(f"Cover letter generation error: {e}")
                    warnings.append(f"Cover letter generation failed: {str(e)}")
                    return None
            
            tasks.append(("cover_letter", generate_cover_letter_task()))
        
        # Execute tasks in parallel
        logger.info(f"⚡ Executing {len(tasks)} tasks in parallel...")
        results = {}
        
        if tasks:
            task_results = await asyncio.gather(*[task[1] for task in tasks])
            for (name, _), result in zip(tasks, task_results):
                results[name] = result
        
        # Build response
        total_time = time.time() - start_time
        
        checklist_data = None
        cover_letter_data = None
        
        if "checklist" in results and results["checklist"]:
            checklist_data = results["checklist"].model_dump()
        
        if "cover_letter" in results and results["cover_letter"]:
            cover_letter_data = results["cover_letter"].model_dump()
        
        # Check if we have at least one result
        if not checklist_data and not cover_letter_data:
            raise Exception("Both generations failed")
        
        response = CompletePackageResponse(
            success=True,
            checklist=checklist_data,
            cover_letter=cover_letter_data,
            metadata={
                "total_time_seconds": round(total_time, 2),
                "checklist_generated": checklist_data is not None,
                "cover_letter_generated": cover_letter_data is not None,
                "checklist_time": checklist_data.get("metadata", {}).get("generation_time_seconds") if checklist_data else None,
                "cover_letter_time": cover_letter_data.get("metadata", {}).get("generation_time_seconds") if cover_letter_data else None,
                "user_id": request.user_profile.user_id,
                "destination": request.user_profile.destination_country,
                "visa_type": request.user_profile.visa_type.value
            },
            warnings=warnings
        )
        
        logger.info(f"✅ Complete package generated in {total_time:.2f}s")
        return response.model_dump()
        
    except Exception as e:
        logger.error(f"Complete package generation failed: {e}")
        total_time = time.time() - start_time
        
        return CompletePackageResponse(
            success=False,
            metadata={"total_time_seconds": round(total_time, 2)},
            warnings=warnings,
            error_message=str(e)
        ).model_dump()


# Run with: uvicorn api_server:app --host 0.0.0.0 --port 8000 --reload
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "api_server:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=True
    )

