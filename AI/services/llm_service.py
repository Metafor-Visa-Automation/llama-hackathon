"""
Ollama LLM service for text generation.
Implements retry logic and structured JSON generation.
"""

from typing import List, Dict, Any, Optional
import aiohttp
import asyncio
import json

from utils import logger
from utils.exceptions import (
    LLMError,
    LLMConnectionError,
    LLMResponseError,
    LLMTimeoutError,
    RetryExhaustedError
)
from utils.helpers import clean_json_response, extract_json_from_text


class OllamaClient:
    """Ollama LLM client implementation."""
    
    def __init__(
        self,
        api_url: Optional[str] = None,
        model: Optional[str] = None,
        timeout: Optional[int] = None
    ):
        """
        Initialize Ollama client.
        
        Args:
            api_url: Ollama API endpoint
            model: Model name
            timeout: Request timeout in seconds
        """
        from config.settings import settings
        self.api_url = api_url or settings.OLLAMA_API_URL
        self.model = model or settings.OLLAMA_MODEL
        self.timeout = timeout or settings.OLLAMA_TIMEOUT
        self._session: Optional[aiohttp.ClientSession] = None
    
    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create aiohttp session."""
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession()
        return self._session
    
    async def close(self) -> None:
        """Close aiohttp session."""
        if self._session and not self._session.closed:
            await self._session.close()
            logger.info("Ollama client session closed")
    
    async def _make_request(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        stream: bool = False
    ) -> Dict[str, Any]:
        """Make HTTP request to Ollama API with retry logic."""
        session = await self._get_session()
        
        payload = {
            "model": self.model,
            "messages": messages,
            "stream": stream,
            "format": "json",  # ← FORCE JSON MODE
            "options": {
                "temperature": temperature
            }
        }
        
        from config.settings import settings
        
        retry_count = 0
        last_error = None
        
        while retry_count < settings.MAX_RETRIES:
            try:
                logger.debug(f"Making request to Ollama API (attempt {retry_count + 1})")
                
                async with session.post(
                    self.api_url,
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=self.timeout)
                ) as response:
                    
                    if response.status != 200:
                        error_text = await response.text()
                        raise LLMResponseError(
                            f"Ollama API returned status {response.status}",
                            {"status": response.status, "error": error_text}
                        )
                    
                    result = await response.json()
                    logger.info("Ollama API request successful")
                    return result
                    
            except asyncio.TimeoutError as e:
                last_error = LLMTimeoutError(
                    "Ollama API request timed out",
                    {"timeout": self.timeout, "attempt": retry_count + 1}
                )
                logger.warning(f"Request timeout (attempt {retry_count + 1})")
                
            except aiohttp.ClientError as e:
                last_error = LLMConnectionError(
                    "Failed to connect to Ollama API",
                    {"error": str(e), "attempt": retry_count + 1}
                )
                logger.warning(f"Connection error (attempt {retry_count + 1}): {str(e)}")
                
            except Exception as e:
                last_error = LLMError(
                    "Unexpected error during Ollama API request",
                    {"error": str(e), "attempt": retry_count + 1}
                )
                logger.error(f"Unexpected error: {str(e)}")
            
            retry_count += 1
            if retry_count < settings.MAX_RETRIES:
                await asyncio.sleep(settings.RETRY_DELAY)
        
        # All retries exhausted
        logger.error(f"All {settings.MAX_RETRIES} retry attempts exhausted")
        raise RetryExhaustedError(
            "Max retries exceeded for Ollama API",
            {"retries": settings.MAX_RETRIES, "last_error": str(last_error)}
        )
    
    async def generate(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: Optional[int] = None
    ) -> Dict[str, Any]:
        """Generate text using Ollama LLM."""
        try:
            result = await self._make_request(messages, temperature)
            
            if 'message' in result and 'content' in result['message']:
                return {
                    'content': result['message']['content'],
                    'model': result.get('model', self.model),
                    'created_at': result.get('created_at'),
                    'done': result.get('done', True)
                }
            else:
                raise LLMResponseError(
                    "Invalid response structure from Ollama",
                    {"response": result}
                )
                
        except (LLMConnectionError, LLMTimeoutError, LLMResponseError, RetryExhaustedError):
            raise
        except Exception as e:
            logger.error(f"Text generation failed: {str(e)}")
            raise LLMError(
                "Failed to generate text",
                {"error": str(e)}
            )
    
    async def generate_structured(
        self,
        messages: List[Dict[str, str]],
        response_format: Dict[str, Any],
        temperature: float = 0.7
    ) -> Dict[str, Any]:
        """Generate structured JSON output using Ollama LLM."""
        try:
            formatted_messages = messages.copy()

            # Build schema instruction with actual schema
            import json as json_module
            schema_str = json_module.dumps(response_format, indent=2)

            json_instruction = (
                "\n\n⚠️ CRITICAL: You MUST respond with ONLY valid JSON matching this EXACT schema:\n\n"
                f"{schema_str}\n\n"
                "RULES:\n"
                "1. Do NOT include markdown, code blocks, or explanatory text\n"
                "2. Your ENTIRE response must be a single valid JSON object\n"
                "3. Include ALL required fields from the schema\n"
                "4. Follow the exact field names and types shown above"
            )
            
            has_system_message = any(msg.get('role') == 'system' for msg in formatted_messages)
            
            if has_system_message:
                for msg in formatted_messages:
                    if msg.get('role') == 'system':
                        msg['content'] += json_instruction
                        break
            else:
                formatted_messages.insert(0, {
                    'role': 'system',
                    'content': f"You are a helpful assistant that responds in JSON format.{json_instruction}"
                })
            
            result = await self._make_request(formatted_messages, temperature)
            
            if 'message' in result and 'content' in result['message']:
                content = result['message']['content']
                cleaned_content = clean_json_response(content)

                # Debug: Log raw content
                logger.debug(f"Raw LLM content length: {len(content)}")
                logger.debug(f"Raw LLM content preview: {content[:500]}")
                logger.debug(f"Cleaned content preview: {cleaned_content[:500]}")

                try:
                    parsed_json = json.loads(cleaned_content)
                    logger.info("Successfully parsed structured JSON response")
                    return parsed_json
                except json.JSONDecodeError as e:
                    logger.warning(f"Initial JSON parse failed: {str(e)}")
                    logger.error(f"Failed content (first 1000 chars): {content[:1000]}")
                    
                    extracted = extract_json_from_text(content)
                    if extracted:
                        logger.info("Successfully extracted JSON using fallback methods")
                        return extracted
                    else:
                        logger.error("All JSON extraction methods failed")
                        raise LLMResponseError(
                            "Failed to parse JSON from LLM response after all attempts",
                            {
                                "parse_error": str(e),
                                "raw_preview": content[:300],
                                "cleaned_preview": cleaned_content[:300]
                            }
                        )
            else:
                raise LLMResponseError(
                    "Invalid response structure from Ollama",
                    {"response": result}
                )
                
        except (LLMConnectionError, LLMTimeoutError, LLMResponseError, RetryExhaustedError):
            raise
        except Exception as e:
            logger.error(f"Structured generation failed: {str(e)}")
            raise LLMError(
                "Failed to generate structured output",
                {"error": str(e)}
            )


class LLMService:
    """High-level LLM service with convenience methods."""
    
    def __init__(self, llm_client: OllamaClient):
        """Initialize LLM service."""
        self.client = llm_client
    
    async def generate_text(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.7
    ) -> str:
        """Generate text with system and user prompts."""
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        result = await self.client.generate(messages, temperature)
        return result['content']
    
    async def generate_json(
        self,
        system_prompt: str,
        user_prompt: str,
        json_schema: Dict[str, Any],
        temperature: float = 0.7
    ) -> Dict[str, Any]:
        """Generate structured JSON output."""
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        return await self.client.generate_structured(
            messages,
            json_schema,
            temperature
        )
    
    async def close(self) -> None:
        """Close LLM client session."""
        await self.client.close()

