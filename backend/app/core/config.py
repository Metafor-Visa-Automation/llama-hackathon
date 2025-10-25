from pydantic_settings import BaseSettings
from typing import Optional
import os


class Settings(BaseSettings):
    # Firebase Configuration
    firebase_service_account_key_path: str = "visa-a05d3-firebase-adminsdk-fbsvc-f627f00882.json"
    firebase_storage_bucket: str = "visa-a05d3.appspot.com"
    firebase_project_id: str = "visa-a05d3"
    
    # App Configuration
    app_name: str = "VisaPrep AI"
    app_version: str = "1.0.0"
    debug: bool = True
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
