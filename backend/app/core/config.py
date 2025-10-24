from pydantic import BaseSettings
from typing import Optional, List

class Settings(BaseSettings):
    # JWT Configuration
    secret_key: str = "your-secret-key-here-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # API Configuration
    api_v1_str: str = "/api/v1"
    project_name: str = "VisaPrep AI"
    
    # File Upload Configuration
    max_file_size: int = 10 * 1024 * 1024  # 10MB
    allowed_file_types: List[str] = ["image/jpeg", "image/png", "application/pdf"]
    
    # Firebase (using JSON file directly, no env vars needed)
    firebase_project_id: str = "visa-a05d3"
    
    class Config:
        env_file = ".env"

settings = Settings()
