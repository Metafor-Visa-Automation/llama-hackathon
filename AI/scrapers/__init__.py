"""
Scrapers package for web scraping visa information.
Single UniversalScraper supports 30+ countries dynamically.
DRY principle: one scraper implementation for all countries.
"""

from .base_scraper import BaseScraper
from .universal_scraper import UniversalScraper
from .scraper_registry import ScraperRegistry, get_scraper

__all__ = [
    'BaseScraper',
    'UniversalScraper',
    'ScraperRegistry',
    'get_scraper',
]

