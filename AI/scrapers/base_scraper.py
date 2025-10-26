"""
Abstract base class for country-specific visa scrapers.
Implements Strategy Pattern for extensibility.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from models.visa_models import VisaRequirement, ScrapedData
from models.user_profile import VisaType
from utils import logger


class BaseScraper(ABC):
    """Abstract base class for visa information scrapers."""
    
    def __init__(self, country_code: str, base_url: str):
        """Initialize scraper."""
        self.country_code = country_code.lower()
        self.base_url = base_url
        logger.info(f"Initialized {self.__class__.__name__} for {country_code}")
    
    @abstractmethod
    async def scrape_requirements(
        self,
        visa_type: VisaType,
        nationality: Optional[str] = None
    ) -> tuple[List[VisaRequirement], str]:
        """
        Scrape visa requirements from official website.

        Returns:
            Tuple of (requirements_list, data_source)
        """
        pass
    
    @abstractmethod
    async def scrape_application_steps(
        self,
        visa_type: VisaType
    ) -> List[str]:
        """Scrape application steps/process."""
        pass
    
    @abstractmethod
    async def scrape_processing_info(
        self,
        visa_type: VisaType
    ) -> Dict[str, Any]:
        """Scrape processing time and fees information."""
        pass
    
    async def scrape_all(
        self,
        visa_type: VisaType,
        nationality: Optional[str] = None
    ) -> ScrapedData:
        """Scrape all visa information with warnings tracking."""
        from datetime import datetime

        logger.info(f"Starting complete scrape for {self.country_code} {visa_type.value}")

        warnings = []

        # Scrape requirements (returns tuple: requirements, source)
        requirements, data_source = await self.scrape_requirements(visa_type, nationality)

        if not requirements:
            warnings.append("Unable to scrape visa requirements from official website")

        # Scrape application steps
        application_steps = await self.scrape_application_steps(visa_type)
        if not application_steps:
            warnings.append("Unable to scrape application steps")

        # Scrape processing info
        processing_info = await self.scrape_processing_info(visa_type)
        if not processing_info or not processing_info.get('processing_time'):
            warnings.append("Unable to scrape processing time information")

        # Build complete response
        scraped_data = ScrapedData(
            country=self.country_code,
            visa_type=visa_type.value,
            requirements=requirements,
            application_steps=application_steps,
            processing_time=processing_info.get('processing_time'),
            fees=processing_info.get('fees'),
            source_url=self.base_url,
            scraped_at=datetime.now(),
            data_source=data_source,
            scraping_warnings=warnings,
            additional_info=processing_info.get('additional_info', {})
        )

        logger.info(
            f"Scraping complete: {len(requirements)} requirements, "
            f"{len(application_steps)} steps, source={data_source}"
        )
        if warnings:
            logger.warning(f"Scraping warnings: {warnings}")

        return scraped_data


__all__ = ['BaseScraper']

