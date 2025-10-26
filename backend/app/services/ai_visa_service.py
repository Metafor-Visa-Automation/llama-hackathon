"""
AI Visa Service
Handles communication with external AI visa checklist generation API
"""
import httpx
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


class AIVisaService:
    """Service for interacting with external AI visa API"""
    
    def __init__(self, base_url: str = "https://d0b00d6a25a6.ngrok-free.app"):
        self.base_url = base_url
        self.checklist_endpoint = f"{base_url}/api/v1/visa/generate-checklist"
    
    async def generate_checklist(
        self,
        nationality: str,
        destination_country: str,
        visa_type: str,
        occupation: str,
        travel_purpose: str,
        force_refresh: bool = True,
        temperature: float = 0.3
    ) -> Dict[str, Any]:
        """
        Generate visa checklist by calling external AI API
        
        Args:
            nationality: User's nationality (e.g., "Türkiye")
            destination_country: Destination country (e.g., "Almanya")
            visa_type: Type of visa (e.g., "tourist")
            occupation: User's occupation (e.g., "Software Engineer")
            travel_purpose: Purpose of travel (e.g., "Tourism")
            force_refresh: Whether to force refresh the checklist
            temperature: AI temperature parameter for generation
            
        Returns:
            Dictionary containing the AI-generated checklist response
        """
        try:
            payload = {
                "nationality": nationality,
                "destination_country": destination_country,
                "visa_type": visa_type,
                "occupation": occupation,
                "travel_purpose": travel_purpose,
                "force_refresh": force_refresh,
                "temperature": temperature
            }
            
            logger.info(f"Calling AI visa checklist API with payload: {payload}")
            
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    self.checklist_endpoint,
                    json=payload,
                    headers={"Content-Type": "application/json"}
                )
                
                # Raise an error for bad status codes
                response.raise_for_status()
                
                result = response.json()
                logger.info(f"Successfully received AI visa checklist response")
                return result
                
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error occurred: {e.response.status_code} - {e.response.text}")
            raise Exception(f"External API error: {e.response.status_code}")
        except httpx.RequestError as e:
            logger.error(f"Request error occurred: {str(e)}")
            raise Exception(f"Failed to connect to external API: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error in AI visa service: {str(e)}")
            raise Exception(f"AI visa service error: {str(e)}")


# Singleton instance
ai_visa_service = AIVisaService()
