"""
Scraper orchestration service with caching support.
"""

import json
from typing import Optional, List
from pathlib import Path
from datetime import datetime, timedelta
from diskcache import Cache
import asyncio

# Lazy import to avoid circular dependency
# from scrapers import get_scraper  # Moved to method level

from models.visa_models import ScrapedData
from models.user_profile import VisaType
from config.settings import settings
from utils import logger
from utils.exceptions import CacheError, VisaDataError


class ScraperService:
    """
    Service for orchestrating web scraping with intelligent caching.
    """
    
    def __init__(self):
        """Initialize scraper service with cache."""
        self.cache_dir = settings.SCRAPER_CACHE_DIR
        self.cache_ttl = settings.SCRAPER_CACHE_TTL
        
        # Initialize disk cache
        try:
            self._cache = Cache(str(self.cache_dir))
            logger.info(f"Initialized scraper cache at {self.cache_dir}")
        except Exception as e:
            logger.warning(f"Failed to initialize cache: {str(e)}")
            self._cache = None
    
    def _get_cache_key(self, country: str, visa_type: VisaType, nationality: Optional[str] = None) -> str:
        """
        Generate cache key for scraped data.
        
        Args:
            country: Country code
            visa_type: Visa type
            nationality: Optional nationality
            
        Returns:
            Cache key string
        """
        key_parts = [country.lower(), visa_type.value]
        if nationality:
            key_parts.append(nationality.lower())
        return "_".join(key_parts)
    
    def _is_cache_valid(self, cached_data: ScrapedData) -> bool:
        """
        Check if cached data is still valid.
        
        Args:
            cached_data: Cached scraped data
            
        Returns:
            True if cache is valid, False otherwise
        """
        if not cached_data or not hasattr(cached_data, 'scraped_at'):
            return False
        
        age = datetime.now() - cached_data.scraped_at
        return age.total_seconds() < self.cache_ttl
    
    async def get_visa_info(
        self,
        country: str,
        target_url: str,
        visa_type: VisaType,
        nationality: Optional[str] = None,
        force_refresh: bool = False
    ) -> ScrapedData:
        """
        Get visa information with caching.

        Args:
            country: Country code (e.g., 'france')
            target_url: Official visa website URL to scrape
            visa_type: Type of visa
            nationality: Applicant's nationality
            force_refresh: Force refresh from source (bypass cache)

        Returns:
            Scraped visa information

        Raises:
            VisaDataError: If URL is not provided
        """
        cache_key = self._get_cache_key(country, visa_type, nationality)

        # Try to get from cache if not forcing refresh
        if not force_refresh and self._cache is not None:
            try:
                cached_data_dict = self._cache.get(cache_key)
                if cached_data_dict:
                    cached_data = ScrapedData(**cached_data_dict)

                    if self._is_cache_valid(cached_data):
                        logger.info(
                            f"Using cached data for {country} {visa_type} "
                            f"(age: {(datetime.now() - cached_data.scraped_at).seconds}s)"
                        )
                        # Mark data source as cached
                        cached_data.data_source = "cached"
                        return cached_data
                    else:
                        logger.info(f"Cache expired for {country} {visa_type}, refreshing...")
            except Exception as e:
                logger.warning(f"Cache read error: {str(e)}")

        # Scrape fresh data
        logger.info(f"Scraping fresh data for {country} {visa_type}...")

        try:
            # Lazy import to avoid circular dependency
            from scrapers import get_scraper
            scraper = get_scraper(country, target_url)
            scraped_data = await scraper.scrape_all(visa_type, nationality)

            # Save to cache ONLY if scraping was successful
            if scraped_data.data_source == "scraped_live" and self._cache is not None:
                try:
                    self._cache.set(
                        cache_key,
                        scraped_data.model_dump(mode='json'),
                        expire=self.cache_ttl
                    )
                    logger.info(f"Cached successfully scraped data for {country} {visa_type}")
                except Exception as e:
                    logger.warning(f"Cache write error: {str(e)}")
            elif scraped_data.data_source != "scraped_live":
                logger.warning(f"Not caching data with source: {scraped_data.data_source}")

            return scraped_data

        except Exception as e:
            logger.error(f"Failed to scrape {country} visa info: {str(e)}")

            # Try to return stale cache as fallback
            if self._cache is not None:
                try:
                    cached_data_dict = self._cache.get(cache_key)
                    if cached_data_dict:
                        logger.warning("Using stale cache as fallback")
                        cached_data = ScrapedData(**cached_data_dict)
                        # Mark as stale cached data
                        cached_data.data_source = "cached_stale"
                        return cached_data
                except:
                    pass

            raise
    
    async def get_visa_info_from_multiple_sources(
        self,
        country: str,
        target_urls: List[str],
        visa_type: VisaType,
        nationality: Optional[str] = None,
        force_refresh: bool = False
    ) -> ScrapedData:
        """
        Scrape visa information from multiple sources and intelligently merge.
        
        Args:
            country: Country code
            target_urls: List of URLs to scrape
            visa_type: Type of visa
            nationality: Applicant's nationality
            force_refresh: Force refresh from source
            
        Returns:
            Merged scraped data from all sources
            
        Raises:
            VisaDataError: If all sources fail
        """
        logger.info(f"Scraping {country} visa info from {len(target_urls)} sources...")
        
        # Scrape from all sources (parallel)
        scrape_tasks = [
            self.get_visa_info(country, url, visa_type, nationality, force_refresh)
            for url in target_urls
        ]
        
        # Gather results (continue on errors)
        results = []
        scraping_errors = []
        
        for i, task in enumerate(asyncio.as_completed(scrape_tasks)):
            try:
                result = await task
                results.append(result)
                logger.info(f"✓ Successfully scraped source {i+1}/{len(target_urls)}")
            except Exception as e:
                error_msg = f"Failed to scrape {target_urls[i] if i < len(target_urls) else 'unknown'}: {str(e)}"
                logger.warning(error_msg)
                scraping_errors.append(error_msg)
        
        # Check if we got any results
        if not results:
            error_msg = f"All {len(target_urls)} sources failed to scrape"
            logger.error(error_msg)
            raise VisaDataError(error_msg, {"errors": scraping_errors})
        
        logger.info(f"Successfully scraped {len(results)}/{len(target_urls)} sources")
        
        # Merge results
        merged_data = self._merge_scraped_data(results, scraping_errors)
        
        # Try to cache merged result (using first URL as representative)
        if merged_data.data_source == "scraped_live" and self._cache is not None:
            cache_key = self._get_cache_key(country, visa_type, nationality)
            try:
                self._cache.set(
                    cache_key,
                    merged_data.model_dump(mode='json'),
                    expire=self.cache_ttl
                )
                logger.info(f"Cached merged data for {country} {visa_type}")
            except Exception as e:
                logger.warning(f"Cache write error for merged data: {str(e)}")
        
        return merged_data
    
    def _merge_scraped_data(
        self,
        results: List[ScrapedData],
        errors: List[str] = None
    ) -> ScrapedData:
        """
        Intelligently merge multiple scraped results.
        
        Strategy:
        1. Combine all requirements from all sources
        2. Deduplicate based on title similarity (case-insensitive)
        3. Add source URL to notes for traceability
        4. Merge application steps (remove duplicates, keep order)
        5. Use most detailed processing info
        6. Aggregate warnings
        
        Args:
            results: List of ScrapedData from different sources
            errors: List of error messages from failed sources
            
        Returns:
            Merged ScrapedData
        """
        if not results:
            raise ValueError("Cannot merge empty results list")
        
        logger.info(f"Merging {len(results)} scraped results...")
        
        # Use first result as base
        merged = results[0]
        
        # Merge requirements with deduplication
        all_requirements = []
        seen_titles = {}  # title_lower -> requirement (keep first/best)
        
        for result in results:
            for req in result.requirements:
                title_key = req.title.lower().strip()
                
                if title_key not in seen_titles:
                    # Add source URL to notes for traceability
                    if req.notes:
                        req.notes += f" | Source: {result.source_url}"
                    else:
                        req.notes = f"Source: {result.source_url}"
                    
                    all_requirements.append(req)
                    seen_titles[title_key] = req
                    logger.debug(f"Added requirement: {req.title} from {result.source_url}")
                else:
                    # Already have this requirement, optionally enhance it
                    existing = seen_titles[title_key]
                    
                    # If new one has more details, append notes
                    if len(req.description) > len(existing.description):
                        existing.description = req.description
                    
                    # Append additional source to notes
                    if result.source_url not in existing.notes:
                        existing.notes += f", {result.source_url}"
        
        merged.requirements = all_requirements
        logger.info(f"✓ Merged requirements: {len(all_requirements)} unique items")
        
        # Merge application steps (deduplicate, keep order)
        all_steps = []
        seen_steps = set()
        
        for result in results:
            for step in result.application_steps:
                step_normalized = step.lower().strip()
                if step_normalized not in seen_steps:
                    all_steps.append(step)
                    seen_steps.add(step_normalized)
        
        merged.application_steps = all_steps
        logger.info(f"✓ Merged application steps: {len(all_steps)} unique steps")
        
        # Use most detailed processing info (prefer longer descriptions)
        best_processing_time = merged.processing_time or ""
        best_fees = merged.fees or {}
        
        for result in results[1:]:
            if result.processing_time and len(result.processing_time) > len(best_processing_time):
                best_processing_time = result.processing_time
            if result.fees and len(result.fees) > len(best_fees):
                best_fees = result.fees
        
        merged.processing_time = best_processing_time
        merged.fees = best_fees
        
        # Aggregate warnings
        all_warnings = []
        for result in results:
            all_warnings.extend(result.scraping_warnings or [])
        
        if errors:
            all_warnings.extend(errors)
        
        merged.scraping_warnings = list(set(all_warnings))  # Deduplicate warnings
        
        # Update source URL to indicate multiple sources
        source_urls = [r.source_url for r in results]
        merged.source_url = f"Multiple sources ({len(source_urls)}): " + ", ".join(source_urls[:3])
        if len(source_urls) > 3:
            merged.source_url += f" and {len(source_urls) - 3} more"
        
        # Update metadata
        merged.scraped_at = datetime.now()
        merged.data_source = "scraped_live_merged" if any(
            r.data_source == "scraped_live" for r in results
        ) else "scraped_live_fallback"
        
        logger.info(f"✓ Merge complete: {len(all_requirements)} requirements, {len(all_steps)} steps")
        
        return merged
    
    def get_cache_status(self, country: str, visa_type: VisaType) -> dict:
        """Get cache status for a country/visa type."""
        cache_key = self._get_cache_key(country, visa_type)
        
        if self._cache is None:
            return {
                "cached": False,
                "reason": "Cache not available"
            }
        
        try:
            cached_data_dict = self._cache.get(cache_key)
            if not cached_data_dict:
                return {
                    "cached": False,
                    "reason": "No cached data"
                }
            
            cached_data = ScrapedData(**cached_data_dict)
            age = datetime.now() - cached_data.scraped_at
            is_valid = self._is_cache_valid(cached_data)
            
            return {
                "cached": True,
                "valid": is_valid,
                "scraped_at": cached_data.scraped_at.isoformat(),
                "age_seconds": int(age.total_seconds()),
                "ttl_seconds": self.cache_ttl,
                "expires_in_seconds": max(0, self.cache_ttl - int(age.total_seconds()))
            }
            
        except Exception as e:
            return {
                "cached": False,
                "reason": f"Cache error: {str(e)}"
            }
    
    def clear_cache(self, country: Optional[str] = None, visa_type: Optional[VisaType] = None):
        """Clear cache."""
        if self._cache is None:
            logger.warning("Cache not available")
            return
        
        try:
            if country and visa_type:
                cache_key = self._get_cache_key(country, visa_type)
                self._cache.delete(cache_key)
                logger.info(f"Cleared cache for {country} {visa_type}")
            else:
                self._cache.clear()
                logger.info("Cleared all cache")
        except Exception as e:
            logger.error(f"Failed to clear cache: {str(e)}")
            raise CacheError("Failed to clear cache", {"error": str(e)})


__all__ = ['ScraperService']

