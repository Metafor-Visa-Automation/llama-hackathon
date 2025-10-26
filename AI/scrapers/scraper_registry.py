"""
Simplified registry for universal scraper.
Single scraper for all countries following DRY principles.
"""

from .base_scraper import BaseScraper
from .universal_scraper import UniversalScraper
from config.settings import settings
from utils import logger
from utils.exceptions import VisaDataError


class ScraperRegistry:
    """
    Simplified scraper registry using UniversalScraper for ALL countries.
    No country-specific implementations - single universal scraper handles everything.
    """
    
    @classmethod
    def get_scraper(cls, country_code: str, target_url: str) -> BaseScraper:
        """
        Get UniversalScraper instance for any country with dynamic URL.
        
        Args:
            country_code: Country code (e.g., 'france', 'germany', 'spain', 'usa')
            target_url: Official visa website URL to scrape
            
        Returns:
            UniversalScraper instance configured for the country
            
        Raises:
            VisaDataError: If URL is not provided
        """
        country_key = country_code.lower()
        
        # Validate URL is provided
        if not target_url:
            raise VisaDataError(
                f"Target URL is required for {country_code}",
                {
                    "country": country_code,
                    "error": "target_url parameter is missing"
                }
            )
        
        # Always use UniversalScraper with dynamic URL
        logger.info(f"✓ Using UniversalScraper for {country_key.upper()} with URL: {target_url}")
        return UniversalScraper(country_code=country_key, target_url=target_url)
    
    @classmethod
    def get_supported_countries(cls) -> list:
        """
        Get list of ALL supported countries (30+).
        All countries use the same UniversalScraper.
        """
        return settings.SUPPORTED_COUNTRIES


def get_scraper(country_code: str, target_url: str) -> BaseScraper:
    """
    Convenience function to get a scraper with dynamic URL.
    
    Args:
        country_code: Country code
        target_url: Official visa website URL
        
    Returns:
        Scraper instance
    """
    return ScraperRegistry.get_scraper(country_code, target_url)


__all__ = ['ScraperRegistry', 'get_scraper']

