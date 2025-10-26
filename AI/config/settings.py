"""
Unified application settings with environment variable support.
Single configuration for both visa checklist and cover letter generation.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Base paths
BASE_DIR = Path(__file__).parent.parent
CACHE_DIR = BASE_DIR / os.getenv('SCRAPER_CACHE_DIR', '.cache')
CACHE_DIR.mkdir(exist_ok=True)


class Settings:
    """Unified application settings."""
    
    # Ollama LLM Configuration
    OLLAMA_API_URL: str = os.getenv('OLLAMA_API_URL', 'http://localhost:11434/api/chat')
    OLLAMA_MODEL: str = os.getenv('OLLAMA_MODEL', 'llama3.1:8b')
    OLLAMA_TIMEOUT: int = int(os.getenv('OLLAMA_TIMEOUT', '240'))  # 4 dakika
    OLLAMA_STREAM: bool = os.getenv('OLLAMA_STREAM', 'true').lower() == 'true'
    
    # Qdrant Configuration - Multiple Collections
    QDRANT_HOST: str = os.getenv('QDRANT_HOST', 'localhost')
    QDRANT_PORT: int = int(os.getenv('QDRANT_PORT', '6333'))
    QDRANT_API_KEY: str = os.getenv('QDRANT_API_KEY', '')
    
    # Qdrant Collections
    COLLECTION_VISA_REQUIREMENTS: str = os.getenv('QDRANT_COLLECTION_VISA_REQUIREMENTS', 'visa_requirements')
    COLLECTION_COVER_LETTERS: str = os.getenv('QDRANT_COLLECTION_COVER_LETTERS', 'cover_letter_examples')
    COLLECTION_VISA_DOCS_RAG: str = os.getenv('QDRANT_COLLECTION_VISA_DOCS_RAG', 'visa_documents_rag')
    
    # Vector size depends on embedding model:
    # all-MiniLM-L6-v2: 384, all-mpnet-base-v2: 768, all-MiniLM-L12-v2: 384
    QDRANT_VECTOR_SIZE: int = int(os.getenv('QDRANT_VECTOR_SIZE', '384'))  # 384 for all-MiniLM-L6-v2
    QDRANT_TOP_K: int = int(os.getenv('QDRANT_TOP_K', '20'))  # Increased from 5 to 20 for more results
    QDRANT_MIN_SCORE: float = float(os.getenv('QDRANT_MIN_SCORE', '0.3'))  # Lower threshold for more inclusive results (0.3-0.5 range)
    
    # Scraper Configuration
    SCRAPER_CACHE_DIR: Path = CACHE_DIR
    SCRAPER_CACHE_TTL: int = int(os.getenv('SCRAPER_CACHE_TTL', '86400'))  # 24 hours
    SCRAPER_TIMEOUT: int = int(os.getenv('SCRAPER_TIMEOUT', '30'))
    SCRAPER_USER_AGENT: str = os.getenv(
        'SCRAPER_USER_AGENT',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
    )
    
    # API Server Configuration
    API_HOST: str = os.getenv('API_HOST', '0.0.0.0')
    API_PORT: int = int(os.getenv('API_PORT', '8000'))
    API_CORS_ORIGINS: str = os.getenv('API_CORS_ORIGINS', '*')
    
    # Application Configuration
    LOG_LEVEL: str = os.getenv('LOG_LEVEL', 'INFO')
    MAX_RETRIES: int = int(os.getenv('MAX_RETRIES', '3'))
    RETRY_DELAY: int = int(os.getenv('RETRY_DELAY', '2'))
    
    # Embedding Model
    # all-MiniLM-L6-v2: Fast and decent quality (384 dims)
    # all-MiniLM-L12-v2: Better quality, similar speed (384 dims) 
    # all-mpnet-base-v2: Best quality but slower (768 dims)
    EMBEDDING_MODEL: str = os.getenv('EMBEDDING_MODEL', 'all-MiniLM-L12-v2')
    
    # Country-specific URLs - Dynamically expandable
    VISA_URLS = {
        # Schengen Countries
        'france': 'https://france-visas.gouv.fr',
        'germany': 'https://www.auswaertiges-amt.de',
        'spain': 'https://www.exteriores.gob.es',
        'italy': 'https://vistoperitalia.esteri.it',
        'netherlands': 'https://www.government.nl/topics/visa-for-the-netherlands',
        'belgium': 'https://dofi.ibz.be',
        'switzerland': 'https://www.sem.admin.ch',
        'austria': 'https://www.bmeia.gv.at',
        'portugal': 'https://vistos.mne.gov.pt',
        'greece': 'https://www.mfa.gr',
        'sweden': 'https://www.migrationsverket.se',
        'norway': 'https://www.udi.no',
        'denmark': 'https://www.nyidanmark.dk',
        'finland': 'https://migri.fi',
        'poland': 'https://www.gov.pl/web/diplomacy',
        'czech': 'https://www.mzv.cz',
        'hungary': 'https://konzuliszolgalat.kormany.hu',
        
        # Major Countries
        'uk': 'https://www.gov.uk/browse/visas-immigration',
        'usa': 'https://travel.state.gov/content/travel/en/us-visas/tourism-visit/visitor.html',
        'canada': 'https://www.canada.ca/en/immigration-refugees-citizenship/services/visit-canada.html',
        'australia': 'https://immi.homeaffairs.gov.au',
        'new_zealand': 'https://www.immigration.govt.nz',
        
        # Asian Countries
        'japan': 'https://www.mofa.go.jp',
        'south_korea': 'https://www.visa.go.kr',
        'singapore': 'https://www.ica.gov.sg',
        'china': 'https://www.visaforchina.org',
        'india': 'https://indianvisaonline.gov.in',
        
        # Middle East
        'uae': 'https://u.ae/en/information-and-services/visa-and-emirates-id',
        'saudi_arabia': 'https://visa.visitsaudi.com',
        'turkey': 'https://www.evisa.gov.tr',
    }
    
    # Supported countries - ALL countries with URLs are supported
    # All use UniversalScraper (single scraper for all countries)
    SUPPORTED_COUNTRIES = list(VISA_URLS.keys())
    
    @classmethod
    def get_visa_url(cls, country: str) -> str:
        """Get the official visa URL for a country."""
        return cls.VISA_URLS.get(country.lower(), '')
    
    @classmethod
    def is_country_supported(cls, country: str) -> bool:
        """Check if a country is supported."""
        return country.lower() in cls.SUPPORTED_COUNTRIES


# Global settings instance
settings = Settings()

