"""
Configuration package for Unified Visa AI System.
Provides settings management and service factory.
"""

from .settings import settings
from .factory import (
    ServiceFactory,
    get_visa_prep_generator,
    get_cover_letter_generator,
    cleanup
)

__all__ = [
    'settings',
    'ServiceFactory',
    'get_visa_prep_generator',
    'get_cover_letter_generator',
    'cleanup',
]

