"""
Visa preparation service with RAG pipeline.
Orchestrates scraping, vector search, and LLM generation.
"""

import time
from typing import Optional, List, Dict, Any

from models.user_profile import VisaType
from models.visa_models import VisaRequirement, StepsResponse, ActionStep
from services.qdrant_service import QdrantService
from services.scraper_service import ScraperService
from services.llm_service import OllamaClient
from utils import logger
from utils.exceptions import LLMError
from config.settings import settings
from prompts.visa_templates import VISA_CATEGORIES


class VisaPrepGenerator:
    """
    Main service for generating personalized visa checklists.
    Implements RAG pipeline: Scrape -> Embed -> Search -> Generate
    """
    
    def __init__(
        self,
        llm_client: OllamaClient,
        qdrant_service: QdrantService,
        scraper_service: ScraperService,
        prompt_builder
    ):
        """
        Initialize visa prep generator with dependencies.
        
        Args:
            llm_client: Ollama LLM client
            qdrant_service: Qdrant vector database service
            scraper_service: Web scraping service
            prompt_builder: Prompt template builder
        """
        self.llm_client = llm_client
        self.qdrant_service = qdrant_service
        self.scraper_service = scraper_service
        self.prompt_builder = prompt_builder
        
        logger.info("VisaPrepGenerator initialized")
    
    async def generate_checklist(
        self,
        nationality: str,
        destination_country: str,
        target_urls: List[str],
        visa_type: VisaType,
        occupation: str,
        travel_purpose: Optional[str] = None,
        use_rag: bool = True,
        temperature: float = 0.7,
        force_refresh: bool = False
    ) -> StepsResponse:
        """
        Generate personalized visa checklist.
        
        Args:
            nationality: Applicant nationality
            destination_country: Target country
            target_urls: List of official visa website URLs
            visa_type: Type of visa
            occupation: Applicant occupation
            travel_purpose: Purpose of travel
            use_rag: Whether to use RAG for similar cases
            temperature: LLM temperature
            force_refresh: Force refresh scraped data
            
        Returns:
            Complete checklist response
        """
        start_time = time.time()
        
        try:
            logger.info(
                f"Generating checklist for {nationality} -> "
                f"{destination_country} ({visa_type}) from {len(target_urls)} sources"
            )
            
            # Step 1: Scrape latest visa requirements from multiple sources
            logger.info(f"Step 1: Scraping visa requirements from {len(target_urls)} sources...")
            
            if len(target_urls) > 1:
                scraped_data = await self.scraper_service.get_visa_info_from_multiple_sources(
                    country=destination_country,
                    target_urls=target_urls,
                    visa_type=visa_type,
                    nationality=nationality,
                    force_refresh=force_refresh
                )
            else:
                scraped_data = await self.scraper_service.get_visa_info(
                    country=destination_country,
                    target_url=target_urls[0],
                    visa_type=visa_type,
                    nationality=nationality,
                    force_refresh=force_refresh
                )

            requirements = scraped_data.requirements
            application_steps = scraped_data.application_steps or []

            # Collect warnings from scraping
            warnings = list(scraped_data.scraping_warnings)

            # Check if scraping was successful
            if not requirements:
                logger.warning(f"No requirements scraped for {destination_country}")
                warnings.append("No visa requirements could be scraped from official website - generation may be incomplete")

            logger.info(
                f"✓ Found {len(requirements)} requirements and "
                f"{len(application_steps)} steps (source: {scraped_data.data_source})"
            )
            
            # Step 2: Store requirements in Qdrant for future RAG
            await self._ensure_requirements_indexed(scraped_data)
            
            # Step 3: RAG - Search for similar successful applications
            similar_cases = []
            if use_rag:
                logger.info("Step 2: Searching for similar cases...")
                similar_cases = await self._search_similar_cases(
                    nationality, destination_country, visa_type, occupation, travel_purpose
                )
                logger.info(f"✓ Found {len(similar_cases)} similar cases")
            
            # Step 4: Generate personalized checklist with LLM
            logger.info("Step 3: Generating personalized checklist...")
            
            # Collect source URLs (from multi-source or single source)
            source_urls = scraped_data.source_urls if hasattr(scraped_data, 'source_urls') and scraped_data.source_urls else (
                [scraped_data.source_url] if scraped_data.source_url else []
            )
            
            checklist_response = await self._generate_with_llm(
                nationality=nationality,
                destination_country=destination_country,
                visa_type=visa_type,
                occupation=occupation,
                travel_purpose=travel_purpose,
                requirements=requirements,
                application_steps=application_steps,
                similar_cases=similar_cases,
                temperature=temperature,
                source_urls=source_urls
            )
            
            # Add metadata
            generation_time = time.time() - start_time
            checklist_response.metadata.update({
                'generation_time_seconds': round(generation_time, 2),
                'model_used': settings.OLLAMA_MODEL,
                'requirements_found': len(requirements),
                'application_steps': len(application_steps),
                'similar_cases_used': len(similar_cases),
                'data_source': scraped_data.data_source,  # "scraped_live", "cached", etc.
                'source_url': scraped_data.source_url,
                'scraped_at': scraped_data.scraped_at.isoformat(),
                'processing_time': scraped_data.processing_time,
            })

            # Merge scraping warnings with any existing warnings
            if not checklist_response.warnings:
                checklist_response.warnings = []
            checklist_response.warnings.extend(warnings)
            
            logger.info(
                f"✓ Checklist generated successfully in {generation_time:.2f}s"
            )
            
            return checklist_response
            
        except Exception as e:
            logger.error(f"Failed to generate checklist: {str(e)}", exc_info=True)
            
            return StepsResponse(
                success=False,
                action_steps=[],
                total_steps=0,
                mandatory_steps=0,
                optional_steps=0,
                steps_requiring_documents=0,
                estimated_total_time="N/A",
                grouped_by_priority={},
                grouped_by_category={},
                source_urls=[],
                summary="Generation failed",
                error_message=str(e),
                metadata={
                    'generation_time_seconds': time.time() - start_time,
                    'error_type': type(e).__name__
                }
            )
    
    async def _ensure_requirements_indexed(self, scraped_data) -> None:
        """Ensure scraped requirements are indexed in Qdrant."""
        try:
            await self.qdrant_service.connect()
            
            documents = []
            texts = []
            
            for req in scraped_data.requirements:
                # Build rich text for better semantic search
                text_parts = [
                    f"Country: {scraped_data.country}",
                    f"Visa Type: {scraped_data.visa_type}",
                    f"Requirement: {req.title}",
                    f"Description: {req.description}",
                    f"Category: {req.category}"
                ]
                if req.notes:
                    text_parts.append(f"Notes: {req.notes}")
                
                doc = {
                    'country': scraped_data.country,
                    'visa_type': scraped_data.visa_type,
                    'requirement_id': req.requirement_id,
                    'title': req.title,
                    'description': req.description,
                    'category': req.category,
                    'notes': req.notes or '',
                    'text': " | ".join(text_parts),
                }
                documents.append(doc)
                texts.append(doc['text'])
            
            if documents and texts:
                vectors = self.qdrant_service.encode(texts)
                await self.qdrant_service.add_documents(
                    collection_name=settings.COLLECTION_VISA_REQUIREMENTS,
                    documents=documents,
                    vectors=vectors
                )
                logger.info(f"Indexed {len(documents)} requirements in Qdrant")
            
        except Exception as e:
            logger.warning(f"Failed to index requirements: {str(e)}")
    
    async def _search_similar_cases(
        self,
        nationality: str,
        destination_country: str,
        visa_type: VisaType,
        occupation: str,
        travel_purpose: Optional[str]
    ) -> List[Dict[str, Any]]:
        """Search for similar visa cases using RAG."""
        try:
            await self.qdrant_service.connect()
            
            query_text = (
                f"{nationality} national applying for "
                f"{visa_type.value} visa to {destination_country}. "
                f"Occupation: {occupation}. "
                f"Purpose: {travel_purpose or 'tourism'}"
            )
            
            similar_cases = await self.qdrant_service.search_visa_requirements(
                query_text=query_text,
                country=destination_country,
                visa_type=visa_type.value,
                limit=settings.QDRANT_TOP_K  # Use configured value instead of hardcoded
            )
            
            return similar_cases
            
        except Exception as e:
            logger.warning(f"RAG search failed: {str(e)}")
            return []
    
    async def _generate_with_llm(
        self,
        nationality: str,
        destination_country: str,
        visa_type: VisaType,
        occupation: str,
        travel_purpose: Optional[str],
        requirements: List[VisaRequirement],
        application_steps: List[str],
        similar_cases: List[Dict[str, Any]],
        temperature: float,
        source_urls: List[str] = None
    ) -> StepsResponse:
        """Generate actionable steps using LLM."""
        try:
            # Build messages with source URLs
            messages = self.prompt_builder.build_messages(
                nationality=nationality,
                destination_country=destination_country,
                visa_type=visa_type,
                occupation=occupation,
                travel_purpose=travel_purpose,
                requirements=requirements,
                application_steps=application_steps,
                source_urls=source_urls or [],
                similar_cases=similar_cases
            )
            
            # step-based JSON schema (DRY - consistent with models)
            json_schema = {
                "type": "object",
                "properties": {
                    "success": {"type": "boolean"},
                    "action_steps": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "step_id": {"type": "string"},
                                "title": {"type": "string"},
                                "description": {"type": "string"},
                                "priority_score": {
                                    "type": "integer",
                                    "minimum": 1,
                                    "maximum": 5
                                },
                                "requires_document": {"type": "boolean"},
                                "source_urls": {
                                    "type": "array",
                                    "items": {"type": "string"}
                                }
                            },
                            "required": [
                                "step_id", "title", "description", 
                                "priority_score", "requires_document", "source_urls"
                            ]
                        }
                    },
                    "grouped_by_priority": {
                        "type": "object",
                        "additionalProperties": {
                            "type": "array",
                            "items": {"type": "string"}
                        }
                    },
                    "source_urls": {
                        "type": "array",
                        "items": {"type": "string"}
                    }
                },
                "required": [
                    "success", "action_steps", "grouped_by_priority", "source_urls"
                ]
            }
            
            response = await self.llm_client.generate_structured(
                messages=messages,
                response_format=json_schema,
                temperature=temperature
            )

            # Debug: Log response structure
            logger.warning(f"⚠️ Response root fields: {list(response.keys())}")
            logger.warning(f"⚠️ Response has 'success': {('success' in response)}")
            logger.warning(f"⚠️ Response has 'action_steps': {('action_steps' in response)}")

            if response.get("action_steps") and len(response["action_steps"]) > 0:
                first_step = response["action_steps"][0]
                logger.warning(f"⚠️ First step fields: {list(first_step.keys())}")
            else:
                logger.error(f"⚠️ No action_steps in response! Full response: {str(response)[:500]}")

            steps_response = StepsResponse(**response)
            return steps_response
            
        except Exception as e:
            logger.error(f"LLM generation failed: {str(e)}")
            raise LLMError(
                "Failed to generate checklist with LLM",
                {"error": str(e)}
            )
    
    async def close(self):
        """Close all connections."""
        logger.info("Closing VisaPrepGenerator...")
        logger.info("✓ VisaPrepGenerator closed")


__all__ = ['VisaPrepGenerator']

