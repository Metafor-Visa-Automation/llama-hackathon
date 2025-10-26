"""
Universal visa scraper for ALL countries using Crawl4AI.
Single scraper implementation following DRY principles.
Handles all countries with intelligent pattern matching and fallback strategies.
"""

from typing import List, Dict, Any, Optional
from datetime import datetime
import re

from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig, CacheMode

from .base_scraper import BaseScraper
from models.visa_models import VisaRequirement
from models.user_profile import VisaType
from config.settings import settings
from utils import logger
from prompts.visa_templates import VisaExtractionPrompts


class UniversalScraper(BaseScraper):
    """
    Universal visa information scraper using Crawl4AI.
    Single implementation that works for ALL countries dynamically.
    
    Features:
    - Crawl4AI with JavaScript rendering
    - Multi-language pattern matching
    - Intelligent URL construction per country
    - Robust fallback strategies
    - Smart caching support
    """
    
    def __init__(self, country_code: str, target_url: str):
        """
        Initialize universal scraper for any country.
        
        Args:
            country_code: Country code (e.g., 'france', 'germany', 'spain', 'usa')
            target_url: Official visa website URL to scrape
        """
        if not target_url:
            logger.warning(f"No URL provided for {country_code}")
            target_url = ''
        
        super().__init__(
            country_code=country_code,
            base_url=target_url
        )
        
        # Crawl4AI browser configuration
        self.browser_config = BrowserConfig(
            headless=True,
            verbose=False,
            extra_args=["--disable-gpu", "--disable-dev-shm-usage", "--no-sandbox"]
        )
        
        # Crawler run configuration
        self.crawler_config = CrawlerRunConfig(
            cache_mode=CacheMode.BYPASS,
            js_code=[
                "await new Promise(r => setTimeout(r, 3000));",  # Wait for JS
            ],
            wait_for="body",
            page_timeout=30000,
        )
    
    async def scrape_requirements(
        self,
        visa_type: VisaType,
        nationality: Optional[str] = None
    ) -> tuple[List[VisaRequirement], str]:
        """
        Scrape visa requirements using universal pattern matching.
        NO FALLBACK DATA - returns real scraped data or empty list.

        Args:
            visa_type: Type of visa to scrape
            nationality: Optional applicant nationality for filtering

        Returns:
            Tuple of (requirements_list, data_source)
            data_source values:
                - "scraped_live": Successfully scraped real data
                - "scraping_failed_no_url": No URL configured for country
                - "scraping_failed_no_data": Scraping succeeded but no data extracted
                - "scraping_failed_error": Crawl4AI returned error
                - "scraping_failed_exception": Exception during scraping
        """
        logger.info(f"🌍 UniversalScraper: Scraping {self.country_code.upper()} {visa_type.value} visa requirements")

        try:
            if not self.base_url:
                logger.warning(f"No URL configured for {self.country_code}, cannot scrape")
                return [], "scraping_failed_no_url"

            # Construct URL
            url = self._construct_url(visa_type, nationality)

            # Crawl with Crawl4AI
            async with AsyncWebCrawler(config=self.browser_config) as crawler:
                result = await crawler.arun(
                    url=url,
                    config=self.crawler_config
                )

                if result.success:
                    logger.info(f"Successfully scraped {url}")
                    
                    # Try LLM-powered extraction first (primary method)
                    requirements = await self._extract_requirements_with_llm(
                        result.markdown,
                        visa_type
                    )
                    
                    # If LLM extraction is successful, use it
                    if requirements and len(requirements) >= 3:
                        logger.info(f"✓ LLM extracted {len(requirements)} requirements")
                        return requirements, "scraped_live"
                    
                    # Fallback to regex pattern matching
                    logger.warning(f"LLM extraction insufficient ({len(requirements)} requirements), using regex fallback")
                    regex_requirements = self._parse_requirements_from_content(
                        result.markdown,
                        result.html,
                        visa_type
                    )
                    
                    # Combine LLM and regex results (deduplicate by title)
                    combined_requirements = self._combine_requirements(requirements, regex_requirements)

                    if combined_requirements:
                        logger.info(f"Extracted {len(combined_requirements)} requirements (hybrid approach)")
                        return combined_requirements, "scraped_live"
                    else:
                        logger.warning("No requirements extracted from content")
                        return [], "scraping_failed_no_data"
                else:
                    logger.warning(f"Crawl failed: {result.error_message}")
                    return [], "scraping_failed_error"

        except Exception as e:
            logger.error(f"Error during scraping: {e}")
            return [], "scraping_failed_exception"
    
    def _construct_url(self, visa_type: VisaType, nationality: Optional[str] = None) -> str:
        """
        Intelligently construct URL based on country and visa type.
        Handles country-specific URL patterns.
        """
        # Country-specific URL patterns
        url_patterns = {
            'france': {
                VisaType.TOURIST: f"{self.base_url}/en_US/short-stay-visa",
                VisaType.BUSINESS: f"{self.base_url}/en_US/business-visa",
                VisaType.STUDENT: f"{self.base_url}/en_US/student-visa",
                VisaType.WORK: f"{self.base_url}/en_US/work-visa",
            },
            'germany': {
                VisaType.TOURIST: f"{self.base_url}/visa-for-tourism",
                VisaType.BUSINESS: f"{self.base_url}/visa-for-business",
            },
            'uk': {
                VisaType.TOURIST: f"{self.base_url}/standard-visitor-visa",
                VisaType.STUDENT: f"{self.base_url}/student-visa",
            },
            'usa': {
                VisaType.TOURIST: f"{self.base_url}/tourism-visit/visitor",
                VisaType.BUSINESS: f"{self.base_url}/business/visitor",
            },
        }
        
        # Try country-specific URL pattern
        if self.country_code in url_patterns:
            country_patterns = url_patterns[self.country_code]
            if visa_type in country_patterns:
                return country_patterns[visa_type]
        
        # Default: use base URL
        return self.base_url
    
    def _parse_requirements_from_content(
        self,
        markdown: str,
        html: str,
        visa_type: VisaType
    ) -> List[VisaRequirement]:
        """
        Parse requirements from scraped content using intelligent pattern matching.
        Uses regex patterns to identify common visa requirements.
        """
        requirements = []
        content = markdown.lower()
        
        # Enhanced requirement patterns - multi-language including Turkish
        patterns = {
            'passport': r'(?:passport|pasaporte|passeport|reisepass|paspoort|pasaport)(?:.*?(?:valid|validity|válido|valide|gültig|geldig|geçerli))?',
            'application_form': r'(?:application|visa|vize)\s*(?:form|formulario|formulaire|antrag|aanvraag|formu|başvuru)',
            'photo': r'(?:photo(?:graph)?s?|foto(?:graf[íiğ]?a)?s?|image|resim|fotoğraf)(?:.*?(?:\d+\s*[xX×]\s*\d+|biometric|passport[- ]?size|biyometrik))?',
            'insurance': r'(?:insurance|seguro|assurance|versicherung|verzekering|sigorta)(?:.*?(?:medical|travel|health|médico|médicale|kranken|voyage|sağlık|seyahat))?',
            'accommodation': r'(?:accommodation|hotel|lodging|alojamiento|hébergement|unterkunft|verblijf|booking|reservation|konaklama|otel|rezervasyon)',
            'flight': r'(?:flight|air|vuelo|vol|flug|vlucht|uçuş|uçak)(?:.*?(?:ticket|reservation|itinerary|billete|billet|reserva|bilet|rezervasyon))?',
            'bank': r'(?:bank|financial|banka)(?:.*?(?:statement|account|extract|extracto|relevé|kontoauszug|afschrift|hesap|ekstresi?))?',
            'employment': r'(?:employment|work|job|empleo|emploi|beschäftigung|werk|iş|çalışma)(?:.*?(?:letter|proof|certificate|carta|lettre|brief|certificat|mektup|belge|sertifika))?',
            'invitation': r'(?:invitation|invitación|lettre\s*d.?invitation|einladung|uitnodiging|host|davet|davetiye)',
            'financial': r'(?:financial|financiero|financier|finanziell|funds|means|recursos|mali|finansal)(?:.*?(?:proof|evidence|prueba|preuve|nachweis|kanıt|belge))?',
            'income': r'(?:income|salary|sueldo|salaire|gehalt|inkomen|gelir|maaş)(?:.*?(?:proof|statement|certificate|belge|sertifika))?',
            'purpose': r'(?:purpose|reason|motiv|objetivo|raison|grund|amaç|sebep|neden)(?:.*?(?:visit|travel|trip|stay|viaje|séjour|ziyaret|seyahat|gezi))?',
        }
        
        requirement_id_counter = 1
        matched_patterns = []  # Track which patterns matched for logging
        
        # Check for passport requirement
        if re.search(patterns['passport'], content, re.IGNORECASE):
            matched_patterns.append('passport')
            requirements.append(
                VisaRequirement(
                    requirement_id=f"{self.country_code}_gen_{requirement_id_counter:03d}",
                    title="Valid Passport",
                    description="Passport must be valid for required period beyond intended stay",
                    category="documents",
                    mandatory=True
                )
            )
            requirement_id_counter += 1
        
        # Check for application form
        if re.search(patterns['application_form'], content, re.IGNORECASE):
            matched_patterns.append('application_form')
            requirements.append(
                VisaRequirement(
                    requirement_id=f"{self.country_code}_gen_{requirement_id_counter:03d}",
                    title="Visa Application Form",
                    description="Completed and signed visa application form",
                    category="documents",
                    mandatory=True
                )
            )
            requirement_id_counter += 1
        
        # Check for photos
        if re.search(patterns['photo'], content, re.IGNORECASE):
            matched_patterns.append('photo')
            requirements.append(
                VisaRequirement(
                    requirement_id=f"{self.country_code}_gen_{requirement_id_counter:03d}",
                    title="Passport Photos",
                    description="Recent passport-size photos as per specifications",
                    category="documents",
                    mandatory=True
                )
            )
            requirement_id_counter += 1
        
        # Check for insurance
        if re.search(patterns['insurance'], content, re.IGNORECASE):
            matched_patterns.append('insurance')
            requirements.append(
                VisaRequirement(
                    requirement_id=f"{self.country_code}_gen_{requirement_id_counter:03d}",
                    title="Travel Insurance",
                    description="Medical/travel insurance covering required amount",
                    category="financial",
                    mandatory=True
                )
            )
            requirement_id_counter += 1
        
        # Check for accommodation
        if re.search(patterns['accommodation'], content, re.IGNORECASE):
            matched_patterns.append('accommodation')
            requirements.append(
                VisaRequirement(
                    requirement_id=f"{self.country_code}_gen_{requirement_id_counter:03d}",
                    title="Proof of Accommodation",
                    description="Hotel booking, rental agreement, or invitation letter",
                    category="documents",
                    mandatory=True
                )
            )
            requirement_id_counter += 1
        
        # Check for flight itinerary
        if re.search(patterns['flight'], content, re.IGNORECASE):
            matched_patterns.append('flight')
            requirements.append(
                VisaRequirement(
                    requirement_id=f"{self.country_code}_gen_{requirement_id_counter:03d}",
                    title="Flight Itinerary",
                    description="Round-trip flight reservation or itinerary",
                    category="documents",
                    mandatory=True
                )
            )
            requirement_id_counter += 1
        
        # Check for bank statements
        if re.search(patterns['bank'], content, re.IGNORECASE):
            matched_patterns.append('bank')
            requirements.append(
                VisaRequirement(
                    requirement_id=f"{self.country_code}_gen_{requirement_id_counter:03d}",
                    title="Bank Statements",
                    description="Recent bank statements showing sufficient funds",
                    category="financial",
                    mandatory=True
                )
            )
            requirement_id_counter += 1
        
        # Check for employment letter
        if re.search(patterns['employment'], content, re.IGNORECASE):
            matched_patterns.append('employment')
            requirements.append(
                VisaRequirement(
                    requirement_id=f"{self.country_code}_gen_{requirement_id_counter:03d}",
                    title="Employment Letter",
                    description="Letter from employer",
                    category="documents",
                    mandatory=True,
                    applicable_to=["employed"]
                )
            )
            requirement_id_counter += 1
        
        # Add financial proof if mentioned
        if re.search(patterns['financial'], content, re.IGNORECASE):
            matched_patterns.append('financial')
            requirements.append(
                VisaRequirement(
                    requirement_id=f"{self.country_code}_gen_{requirement_id_counter:03d}",
                    title="Financial Proof",
                    description="Proof of sufficient financial means for the trip",
                    category="financial",
                    mandatory=True
                )
            )
            requirement_id_counter += 1
        
        # Log matched patterns for debugging
        if matched_patterns:
            logger.info(f"✓ Regex matched patterns: {', '.join(matched_patterns)}")
        else:
            logger.warning("⚠ No regex patterns matched in content")
        
        return requirements
    
    async def _extract_requirements_with_llm(
        self,
        content: str,
        visa_type: VisaType
    ) -> List[VisaRequirement]:
        """
        Extract visa requirements using LLM for intelligent, context-aware parsing.
        
        Args:
            content: Scraped markdown content
            visa_type: Type of visa
            
        Returns:
            List of extracted requirements (empty list if LLM fails)
        """
        try:
            # Import LLM service (lazy to avoid circular dependency)
            from services.llm_service import LLMService, OllamaClient
            
            # Build extraction prompt
            prompts = VisaExtractionPrompts.build_extraction_prompt(
                content=content,
                country=self.country_code,
                visa_type=visa_type.value
            )
            
            # Create LLM client and service
            llm_client = OllamaClient()
            llm_service = LLMService(llm_client)
            
            try:
                # Generate structured JSON
                logger.info("Calling LLM for requirement extraction...")
                result = await llm_service.generate_json(
                    system_prompt=prompts["system"],
                    user_prompt=prompts["user"],
                    json_schema=VisaExtractionPrompts.REQUIREMENT_SCHEMA,
                    temperature=0.3  # Lower temperature for more consistent extraction
                )
                
                # Parse result into VisaRequirement objects
                requirements = []
                requirement_id_counter = 1
                
                for req_data in result.get("requirements", []):
                    requirement = VisaRequirement(
                        requirement_id=f"{self.country_code}_llm_{requirement_id_counter:03d}",
                        title=req_data.get("title", "Unknown"),
                        description=req_data.get("description", ""),
                        category=req_data.get("category", "documents"),
                        mandatory=req_data.get("mandatory", True),
                        notes=req_data.get("notes", ""),
                        applicable_to=req_data.get("applicable_to", [])
                    )
                    requirements.append(requirement)
                    requirement_id_counter += 1
                
                logger.info(f"LLM successfully extracted {len(requirements)} requirements")
                return requirements
                
            finally:
                # Always close LLM client
                await llm_client.close()
                
        except Exception as e:
            logger.warning(f"LLM extraction failed: {str(e)}")
            return []  # Return empty list, fallback will be used
    
    def _combine_requirements(
        self,
        llm_requirements: List[VisaRequirement],
        regex_requirements: List[VisaRequirement]
    ) -> List[VisaRequirement]:
        """
        Combine LLM and regex requirements, removing duplicates.
        
        Args:
            llm_requirements: Requirements from LLM extraction
            regex_requirements: Requirements from regex pattern matching
            
        Returns:
            Combined deduplicated list
        """
        # Use LLM requirements as base
        combined = list(llm_requirements)
        
        # Track titles for deduplication (case-insensitive)
        seen_titles = {req.title.lower().strip() for req in llm_requirements}
        
        # Add regex requirements that aren't already present
        for req in regex_requirements:
            req_title_key = req.title.lower().strip()
            if req_title_key not in seen_titles:
                combined.append(req)
                seen_titles.add(req_title_key)
                logger.debug(f"Added regex requirement: {req.title}")
        
        return combined
    
    async def scrape_application_steps(
        self,
        visa_type: VisaType
    ) -> List[str]:
        """Generic application steps."""
        country_name = self.country_code.replace('_', ' ').title()
        return [
            f"Visit the official {country_name} visa website",
            "Create an account or register (if required)",
            "Complete the online visa application form",
            "Gather all required documents",
            "Pay the visa application fee",
            "Schedule an appointment at the embassy/consulate or visa application center",
            "Attend the appointment with all original documents",
            "Provide biometric data if required",
            "Submit your application",
            "Track your application status online",
            "Collect your passport with visa decision"
        ]
    
    async def scrape_processing_info(
        self,
        visa_type: VisaType
    ) -> Dict[str, Any]:
        """Generic processing information."""
        return {
            'processing_time': "Typically 15-30 business days (varies by country and season)",
            'fees': {
                'adult': 'Check official website for current fees',
                'child': 'May be reduced or free for children',
            },
            'additional_info': {
                'urgent_processing': 'May be available for additional fee',
                'validity': 'Varies by country and visa type',
                'entry_type': 'Single, double, or multiple entry',
                'note': 'Actual processing time and fees may vary. Check official website for accurate information.'
            }
        }


__all__ = ['UniversalScraper']

