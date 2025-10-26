"""
Centralized logging configuration.
Follows DRY principle - single logging setup for entire application.
"""

import logging
import sys
from typing import Optional
from pathlib import Path
from datetime import datetime


class Logger:
    """Centralized logger configuration."""
    
    _instance: Optional[logging.Logger] = None
    
    @classmethod
    def get_logger(
        cls,
        name: str = "unified_visa_ai",
        level: str = "INFO",
        log_file: Optional[str] = None
    ) -> logging.Logger:
        """
        Get or create logger instance.
        
        Args:
            name: Logger name
            level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
            log_file: Optional log file path
            
        Returns:
            Configured logger instance
        """
        if cls._instance is None:
            cls._instance = cls._setup_logger(name, level, log_file)
        return cls._instance
    
    @staticmethod
    def _setup_logger(
        name: str,
        level: str,
        log_file: Optional[str] = None
    ) -> logging.Logger:
        """Set up logger with console and optional file handlers."""
        logger = logging.getLogger(name)
        logger.setLevel(getattr(logging, level.upper()))
        
        # Prevent duplicate handlers
        if logger.handlers:
            return logger
        
        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(getattr(logging, level.upper()))
        
        # Formatter
        formatter = logging.Formatter(
            fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
        
        # File handler (optional)
        if log_file:
            log_path = Path(log_file)
            log_path.parent.mkdir(parents=True, exist_ok=True)
            
            file_handler = logging.FileHandler(log_file)
            file_handler.setLevel(getattr(logging, level.upper()))
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)
        
        return logger


# Default logger instance
logger = Logger.get_logger()

