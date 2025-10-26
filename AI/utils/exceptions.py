"""
Custom exceptions for Unified Visa AI System.
Centralized error handling following DRY principle.
"""


class UnifiedVisaAIError(Exception):
    """Base exception for all application errors."""
    
    def __init__(self, message: str, details: dict = None):
        self.message = message
        self.details = details or {}
        super().__init__(self.message)


class ConfigurationError(UnifiedVisaAIError):
    """Raised when configuration is invalid or missing."""
    pass


class DataSourceError(UnifiedVisaAIError):
    """Base exception for data source errors."""
    pass


class QdrantError(DataSourceError):
    """Raised when Qdrant operations fail."""
    pass


class LLMError(UnifiedVisaAIError):
    """Base exception for LLM-related errors."""
    pass


class LLMConnectionError(LLMError):
    """Raised when connection to LLM service fails."""
    pass


class LLMResponseError(LLMError):
    """Raised when LLM response is invalid or unexpected."""
    pass


class LLMTimeoutError(LLMError):
    """Raised when LLM request times out."""
    pass


class ValidationError(UnifiedVisaAIError):
    """Raised when data validation fails."""
    pass


class GenerationError(UnifiedVisaAIError):
    """Raised when document generation fails."""
    pass


class PromptError(UnifiedVisaAIError):
    """Raised when prompt rendering or validation fails."""
    pass


class ScraperError(UnifiedVisaAIError):
    """Raised when scraping fails."""
    pass


class CacheError(UnifiedVisaAIError):
    """Raised when cache operations fail."""
    pass


class VisaDataError(UnifiedVisaAIError):
    """Raised when visa data retrieval or processing fails."""
    pass


class RetryExhaustedError(UnifiedVisaAIError):
    """Raised when all retry attempts are exhausted."""
    pass

