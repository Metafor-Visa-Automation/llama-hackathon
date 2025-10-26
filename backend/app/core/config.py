from pydantic_settings import BaseSettings
from typing import Optional, List
import os
from pydantic import field_validator


class Settings(BaseSettings):
    # Firebase Configuration
    firebase_service_account_key_path: str = "visa-a05d3-firebase-adminsdk-fbsvc-f627f00882.json"
    firebase_storage_bucket: str = "visa-a05d3.firebasestorage.app"
    firebase_project_id: str = "visa-a05d3"
    
    # Firebase Service Account Details (from .env)
    firebase_private_key_id: Optional[str] = None
    firebase_private_key: Optional[str] = None
    firebase_client_email: Optional[str] = None
    firebase_client_id: Optional[str] = None
    firebase_auth_uri: Optional[str] = None
    firebase_token_uri: Optional[str] = None
    
    # App Configuration
    app_name: str = "VisaPrep AI"
    app_version: str = "1.0.0"
    debug: bool = True
    host: str = "0.0.0.0"
    port: int = 8000
    
    # OCR Configuration
    groq_api_key: Optional[str] = "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"
    
    # Security Settings
    secret_key: str = "your-secret-key-here"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # CORS Settings
    allowed_origins: List[str] = ["*"]
    allowed_methods: List[str] = ["*"]
    allowed_headers: List[str] = ["*"]
    
    @field_validator('allowed_origins', 'allowed_methods', 'allowed_headers', mode='before')
    @classmethod
    def parse_cors_settings(cls, v):
        if isinstance(v, str):
            # Split comma-separated values and strip whitespace
            return [item.strip() for item in v.split(',') if item.strip()]
        return v
    
    @field_validator('firebase_private_key', mode='before')
    @classmethod
    def parse_firebase_private_key(cls, v):
        if isinstance(v, str):
            # Handle multiline private key format
            if v.startswith('-----BEGIN PRIVATE KEY-----'):
                return v
            else:
                # If it's a single line key, format it properly
                return f"-----BEGIN PRIVATE KEY-----\n{v}\n-----END PRIVATE KEY-----"
        return v
    
    # Logging
    log_level: str = "INFO"
    log_format: str = "json"
    
    # Rate Limiting
    rate_limit_requests: int = 100
    rate_limit_window: int = 60
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
