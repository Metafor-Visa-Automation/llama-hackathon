"""
Unified Service Factory for Visa AI System.
Manages all services with dependency injection and singleton pattern.
"""

from typing import Optional
from utils import logger
from services.llm_service import OllamaClient
from config.settings import settings


class ServiceFactory:
    """
    Unified factory for creating and managing all service instances.
    Implements Singleton pattern for service instances.
    """
    
    # Service instances (singletons)
    _ollama_client: Optional[OllamaClient] = None
    _qdrant_service: Optional['QdrantService'] = None
    _scraper_service: Optional['ScraperService'] = None
    _visa_prep_generator: Optional['VisaPrepGenerator'] = None
    _cover_letter_generator: Optional['CoverLetterGenerator'] = None
    _document_indexer: Optional['DocumentIndexer'] = None
    
    @classmethod
    def get_ollama_client(cls) -> OllamaClient:
        """Get or create Ollama LLM client instance."""
        if cls._ollama_client is None:
            logger.info("Initializing Ollama LLM client...")
            cls._ollama_client = OllamaClient(
                api_url=settings.OLLAMA_API_URL,
                model=settings.OLLAMA_MODEL,
                timeout=settings.OLLAMA_TIMEOUT
            )
            logger.info(f"✓ Ollama client initialized (model: {settings.OLLAMA_MODEL})")
        return cls._ollama_client
    
    @classmethod
    def get_qdrant_service(cls):
        """Get or create Qdrant service instance."""
        if cls._qdrant_service is None:
            from services.qdrant_service import QdrantService
            logger.info("Initializing Qdrant service (multi-collection)...")
            cls._qdrant_service = QdrantService()
            logger.info("✓ Qdrant service initialized with 3 collections")
        return cls._qdrant_service
    
    @classmethod
    def get_scraper_service(cls):
        """Get or create Scraper service instance."""
        if cls._scraper_service is None:
            from services.scraper_service import ScraperService
            logger.info("Initializing Scraper service...")
            cls._scraper_service = ScraperService()
            logger.info("✓ Scraper service initialized")
        return cls._scraper_service
    
    @classmethod
    def get_document_indexer(cls):
        """Get or create Document Indexer instance."""
        if cls._document_indexer is None:
            from services.document_indexer import DocumentIndexer
            logger.info("Initializing Document Indexer...")
            qdrant_service = cls.get_qdrant_service()
            cls._document_indexer = DocumentIndexer(qdrant_service)
            logger.info("✓ Document Indexer initialized")
        return cls._document_indexer
    
    @classmethod
    def get_visa_prep_generator(cls):
        """
        Get or create VisaPrep Generator with all dependencies.
        For visa checklist generation.
        """
        if cls._visa_prep_generator is None:
            from services.visa_prep_service import VisaPrepGenerator
            from prompts import VisaStepsPromptBuilder  # Updated to new step-based builder
            
            logger.info("Initializing VisaPrep Generator (Step-Based)...")
            
            # Get dependencies
            ollama_client = cls.get_ollama_client()
            qdrant_service = cls.get_qdrant_service()
            scraper_service = cls.get_scraper_service()
            prompt_builder = VisaStepsPromptBuilder()  # New builder for actionable steps
            
            # Create generator
            cls._visa_prep_generator = VisaPrepGenerator(
                llm_client=ollama_client,
                qdrant_service=qdrant_service,
                scraper_service=scraper_service,
                prompt_builder=prompt_builder
            )
            
            logger.info("✓ VisaPrep Generator initialized with Step-Based Prompts")
        
        return cls._visa_prep_generator
    
    @classmethod
    def get_cover_letter_generator(cls):
        """
        Get or create Cover Letter Generator with all dependencies.
        For cover letter generation with visa requirements RAG.
        """
        if cls._cover_letter_generator is None:
            from services.cover_letter_service import CoverLetterGenerator
            from prompts import CoverLetterPromptBuilder
            
            logger.info("Initializing Cover Letter Generator with Visa RAG...")
            
            # Get dependencies
            qdrant_service = cls.get_qdrant_service()
            ollama_client = cls.get_ollama_client()
            prompt_builder = CoverLetterPromptBuilder()
            
            # Create generator
            cls._cover_letter_generator = CoverLetterGenerator(
                qdrant_service=qdrant_service,
                llm_client=ollama_client,
                prompt_builder=prompt_builder
            )
            
            logger.info("✓ Cover Letter Generator initialized")
        
        return cls._cover_letter_generator
    
    @classmethod
    def initialize_all_services(cls):
        """
        Initialize all services at startup.
        Useful for warming up the system.
        """
        logger.info("=" * 70)
        logger.info("🚀 Initializing Unified Visa AI System")
        logger.info("=" * 70)
        
        # Initialize core services
        cls.get_ollama_client()
        cls.get_qdrant_service()
        cls.get_scraper_service()
        cls.get_document_indexer()
        
        # Initialize generators
        cls.get_visa_prep_generator()
        cls.get_cover_letter_generator()
        
        logger.info("=" * 70)
        logger.info("✓ Unified Visa AI System Ready")
        logger.info("=" * 70)
        logger.info(f"Configuration:")
        logger.info(f"  • Ollama API: {settings.OLLAMA_API_URL}")
        logger.info(f"  • Model: {settings.OLLAMA_MODEL}")
        logger.info(f"  • Qdrant: {settings.QDRANT_HOST}:{settings.QDRANT_PORT}")
        logger.info(f"  • Collections: 3 (visa_requirements, cover_letters, visa_docs_rag)")
        logger.info(f"  • Cache TTL: {settings.SCRAPER_CACHE_TTL}s")
        logger.info(f"  • API Port: {settings.API_PORT}")
        logger.info("=" * 70)
    
    @classmethod
    async def close_all(cls):
        """
        Close all service connections and cleanup resources.
        Should be called when application shuts down.
        """
        logger.info("Closing all service connections...")
        
        # Close generators
        if cls._visa_prep_generator:
            await cls._visa_prep_generator.close()
        
        if cls._cover_letter_generator:
            await cls._cover_letter_generator.close()
        
        if cls._document_indexer:
            await cls._document_indexer.close()
        
        # Close core services
        if cls._qdrant_service:
            await cls._qdrant_service.close()
        
        if cls._ollama_client:
            await cls._ollama_client.close()
        
        # Reset singletons
        cls._ollama_client = None
        cls._qdrant_service = None
        cls._scraper_service = None
        cls._visa_prep_generator = None
        cls._cover_letter_generator = None
        cls._document_indexer = None
        
        logger.info("✓ All services closed and cleaned up")
    
    @classmethod
    def reset(cls):
        """
        Reset all singleton instances.
        Useful for testing or reconfiguration.
        """
        logger.info("Resetting ServiceFactory...")
        cls._ollama_client = None
        cls._qdrant_service = None
        cls._scraper_service = None
        cls._visa_prep_generator = None
        cls._cover_letter_generator = None
        cls._document_indexer = None
        logger.info("✓ ServiceFactory reset complete")


# Convenience functions
def get_visa_prep_generator():
    """Get VisaPrep Generator instance."""
    return ServiceFactory.get_visa_prep_generator()


def get_cover_letter_generator():
    """Get Cover Letter Generator instance."""
    return ServiceFactory.get_cover_letter_generator()


async def cleanup():
    """Cleanup all services."""
    await ServiceFactory.close_all()


__all__ = [
    'ServiceFactory',
    'get_visa_prep_generator',
    'get_cover_letter_generator',
    'cleanup',
]

