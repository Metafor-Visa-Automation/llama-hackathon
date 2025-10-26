"""
Enhanced Cover Letter Generator with Visa Requirements RAG.
This is the KEY innovation: Cover letters now use actual visa requirements as context!
"""

from typing import Dict, Any, List, Optional
import time

from models.user_profile import UnifiedUserProfile
from models.cover_letter_models import (
    CoverLetterResponse,
    CoverLetterGenerationResponse,
    GenerationMetadata,
    ExampleCoverLetter
)
from services.qdrant_service import QdrantService
from services.llm_service import OllamaClient, LLMService
from utils.exceptions import GenerationError, ValidationError
from utils import logger
from utils.helpers import count_words
from config.settings import settings


class CoverLetterGenerator:
    """
    Enhanced cover letter generation service with visa requirements RAG.
    
    KEY INNOVATION:
    - Uses visa_documents_rag collection to get actual visa requirements
    - Incorporates requirements into prompts
    - Cover letters specifically address what consulates want to see
    """
    
    def __init__(
        self,
        qdrant_service: QdrantService,
        llm_client: OllamaClient,
        prompt_builder
    ):
        """
        Initialize cover letter generator.
        
        Args:
            qdrant_service: Qdrant service for RAG
            llm_client: Ollama LLM client
            prompt_builder: Prompt template builder
        """
        self.qdrant_service = qdrant_service
        self.llm_client = llm_client
        self.llm_service = LLMService(llm_client)
        self.prompt_builder = prompt_builder
        
        logger.info("CoverLetterGenerator initialized with visa requirements RAG")
    
    async def generate_cover_letter(
        self,
        user_profile: UnifiedUserProfile,
        use_visa_requirements: bool = True,
        use_examples: bool = True,
        max_word_count: Optional[int] = None,
        temperature: float = 0.7
    ) -> CoverLetterGenerationResponse:
        """
        Complete cover letter generation workflow with visa requirements context.
        
        Args:
            user_profile: Complete user profile
            use_visa_requirements: Use visa requirements RAG (RECOMMENDED)
            use_examples: Use example cover letters RAG
            max_word_count: Maximum word count (default: 500)
            temperature: LLM temperature for generation
            
        Returns:
            CoverLetterGenerationResponse with result and metadata
        """
        start_time = time.time()
        warnings = []
        retry_count = 0
        
        logger.info(f"Starting cover letter generation for user: {user_profile.user_id}")
        
        try:
            # Step 1: Retrieve visa requirements from visa_docs_rag (KEY INNOVATION!)
            visa_requirements = []
            if use_visa_requirements:
                try:
                    logger.info("Retrieving visa requirements for cover letter context")
                    visa_requirements = await self._retrieve_visa_requirements(
                        user_profile.destination_country,
                        user_profile.visa_type.value
                    )
                    
                    if visa_requirements:
                        logger.info(f"Retrieved {len(visa_requirements)} visa requirements")
                    else:
                        logger.warning("No visa requirements found, generating without requirements context")
                        warnings.append("No visa requirements found in database")
                        
                except Exception as e:
                    logger.warning(f"Failed to retrieve visa requirements: {str(e)}")
                    warnings.append(f"Could not retrieve visa requirements: {str(e)}")
                    visa_requirements = []
            
            # Step 2: Retrieve similar example cover letters from cover_letters collection
            example_letters: List[ExampleCoverLetter] = []
            if use_examples:
                try:
                    logger.info("Retrieving similar cover letter examples")
                    example_letters = await self._retrieve_examples(
                        user_profile.destination_country,
                        user_profile.visa_type.value,
                        user_profile.travel_purpose
                    )
                    
                    if example_letters:
                        logger.info(f"Retrieved {len(example_letters)} example letters")
                    else:
                        logger.warning("No similar examples found")
                        warnings.append("No similar example letters found in database")
                        
                except Exception as e:
                    logger.warning(f"Failed to retrieve examples: {str(e)}")
                    warnings.append(f"Could not retrieve example letters: {str(e)}")
                    example_letters = []
            
            # Step 3: Build enhanced prompt with BOTH visa requirements AND examples
            logger.info("Building enhanced prompts with visa requirements context")
            
            if max_word_count is None:
                max_word_count = 500
            
            messages = self.prompt_builder.build_messages_with_visa_context(
                user_profile=user_profile,
                visa_requirements=visa_requirements,
                example_letters=example_letters,
                max_word_count=max_word_count
            )
            
            # Step 4: Generate cover letter using LLM
            logger.info("Generating cover letter with LLM")
            
            json_schema = {
                "type": "object",
                "properties": {
                    "title": {"type": "string"},
                    "salutation": {"type": "string"},
                    "introduction": {"type": "string"},
                    "body_paragraphs": {
                        "type": "array",
                        "items": {"type": "string"}
                    },
                    "conclusion": {"type": "string"},
                    "closing": {"type": "string"},
                    "key_points": {
                        "type": "array",
                        "items": {"type": "string"}
                    },
                    "tone": {"type": "string"},
                    "word_count": {"type": "integer"}
                },
                "required": ["title", "introduction", "body_paragraphs", "conclusion"]
            }
            
            # Generate with retries
            generated_json = None
            last_error = None
            
            while retry_count < settings.MAX_RETRIES:
                try:
                    generated_json = await self.llm_client.generate_structured(
                        messages=messages,
                        response_format=json_schema,
                        temperature=temperature
                    )
                    break  # Success
                    
                except Exception as e:
                    last_error = e
                    retry_count += 1
                    logger.warning(f"Generation attempt {retry_count} failed: {str(e)}")
                    
                    if retry_count < settings.MAX_RETRIES:
                        import asyncio
                        await asyncio.sleep(settings.RETRY_DELAY)
            
            if generated_json is None:
                raise GenerationError(
                    "Failed to generate cover letter after all retries",
                    {"retries": retry_count, "last_error": str(last_error)}
                )
            
            # Step 5: Parse and validate response
            logger.info("Parsing generated cover letter")
            
            try:
                # Pre-process body_paragraphs if too many
                if 'body_paragraphs' in generated_json:
                    paragraphs = generated_json['body_paragraphs']
                    if len(paragraphs) > 8:
                        logger.warning(f"LLM generated {len(paragraphs)} paragraphs, limiting to 8")
                        combined = ' '.join(paragraphs[7:])
                        generated_json['body_paragraphs'] = paragraphs[:7] + [combined]
                
                cover_letter = CoverLetterResponse(**generated_json)
                
                # Calculate actual word count if not provided
                if cover_letter.word_count is None:
                    full_text = cover_letter.to_full_text()
                    cover_letter.word_count = count_words(full_text)
                
                logger.info(f"Successfully generated cover letter ({cover_letter.word_count} words)")
                
            except Exception as e:
                logger.error(f"Validation failed: {str(e)}")
                logger.error(f"Generated JSON: {generated_json}")
                raise ValidationError(
                    "Failed to validate generated cover letter",
                    {"error": str(e), "response": generated_json, "validation_details": str(e)}
                )
            
            # Calculate generation time
            generation_time = time.time() - start_time
            
            # Build metadata
            metadata = GenerationMetadata(
                model_used=settings.OLLAMA_MODEL,
                examples_used=len(example_letters),
                visa_requirements_used=len(visa_requirements),  # NEW!
                generation_time_seconds=generation_time,
                retry_count=retry_count,
                data_sources={
                    "user_profile": {
                        "user_id": user_profile.user_id,
                        "nationality": user_profile.nationality,
                        "destination_country": user_profile.destination_country,
                        "visa_type": user_profile.visa_type.value
                    },
                    "visa_requirements": len(visa_requirements),
                    "example_letters": len(example_letters),
                    "model_info": {
                        "model_name": settings.OLLAMA_MODEL,
                        "temperature": temperature
                    }
                }
            )
            
            # Build successful response
            return CoverLetterGenerationResponse(
                success=True,
                cover_letter=cover_letter,
                metadata=metadata,
                warnings=warnings
            )
            
        except (GenerationError, ValidationError):
            raise
            
        except Exception as e:
            logger.error(f"Unexpected error during generation: {str(e)}")
            
            generation_time = time.time() - start_time
            metadata = GenerationMetadata(
                model_used=settings.OLLAMA_MODEL,
                examples_used=0,
                generation_time_seconds=generation_time,
                retry_count=retry_count
            )
            
            return CoverLetterGenerationResponse(
                success=False,
                cover_letter=None,
                metadata=metadata,
                error_message=str(e),
                warnings=warnings
            )
    
    async def _retrieve_visa_requirements(
        self,
        country: str,
        visa_type: str
    ) -> List[Dict[str, Any]]:
        """
        Retrieve visa requirements from visa_docs_rag collection.
        This is the KEY INNOVATION - using actual requirements in cover letters!
        
        Args:
            country: Target country
            visa_type: Visa type
            
        Returns:
            List of visa requirements for context
        """
        try:
            await self.qdrant_service.connect()
            
            # Build query
            query_text = f"{visa_type} visa requirements for {country}"
            
            # Search visa_docs_rag collection
            requirements = await self.qdrant_service.search_visa_docs_for_cover_letter(
                query_text=query_text,
                country=country,
                visa_type=visa_type,
                limit=settings.QDRANT_TOP_K
            )
            
            logger.info(f"Retrieved {len(requirements)} visa requirements from RAG")
            return requirements
            
        except Exception as e:
            logger.warning(f"Failed to retrieve visa requirements: {str(e)}")
            return []
    
    async def _retrieve_examples(
        self,
        country: str,
        visa_type: str,
        travel_purpose: str
    ) -> List[ExampleCoverLetter]:
        """
        Retrieve example cover letters from cover_letters collection.
        
        Args:
            country: Target country
            visa_type: Visa type
            travel_purpose: Travel purpose for better matching
            
        Returns:
            List of example cover letters
        """
        try:
            await self.qdrant_service.connect()
            
            # Build query with travel purpose for better matching
            query_text = f"{travel_purpose} for {visa_type} visa to {country}"
            
            # Search cover_letters collection
            results = await self.qdrant_service.search_cover_letter_examples(
                query_text=query_text,
                country=country,
                visa_type=visa_type,
                limit=settings.QDRANT_TOP_K
            )
            
            # Convert to ExampleCoverLetter objects
            examples = []
            for result in results:
                payload = result['payload']
                example = ExampleCoverLetter(
                    id=result['id'],
                    content=payload.get('content', ''),
                    country=payload.get('country', country),
                    visa_type=payload.get('visa_type', visa_type),
                    approved=payload.get('approved', False),
                    similarity_score=result['score']
                )
                examples.append(example)
            
            logger.info(f"Retrieved {len(examples)} example letters from RAG")
            return examples
            
        except Exception as e:
            logger.warning(f"Failed to retrieve examples: {str(e)}")
            return []
    
    async def close(self) -> None:
        """Close all service connections."""
        logger.info("Closing CoverLetterGenerator...")
        try:
            await self.llm_client.close()
        except Exception as e:
            logger.warning(f"Error closing LLM client: {str(e)}")
        logger.info("✓ CoverLetterGenerator closed")


__all__ = ['CoverLetterGenerator']

