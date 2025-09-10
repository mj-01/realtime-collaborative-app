"""
Application configuration using Pydantic settings.
"""
import os
from typing import List
from pydantic_settings import BaseSettings
from pydantic import field_validator, ConfigDict
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Settings(BaseSettings):
    """Application settings."""
    
    # Server Configuration
    host: str = os.getenv('HOST', '0.0.0.0')
    port: int = int(os.getenv('PORT', '8080'))
    debug: bool = os.getenv('DEBUG', 'false').lower() == 'true'
    
    # Google Cloud Configuration
    google_service_account_key: str = os.getenv('GOOGLE_SERVICE_ACCOUNT_KEY', '')
    gcs_bucket_name: str = os.getenv('GCS_BUCKET_NAME', 'labs-realtime-app-files')
    google_cloud_project: str = os.getenv('GOOGLE_CLOUD_PROJECT', '')
    
    # CORS Configuration
    cors_origins: List[str] = os.getenv('CORS_ORIGINS', 'http://localhost:3000,https://frontend-987275518911.us-central1.run.app').split(',')
    
    # File Upload Configuration
    max_file_size_mb: int = int(os.getenv('MAX_FILE_SIZE_MB', '10'))
    allowed_file_types: List[str] = os.getenv('ALLOWED_FILE_TYPES', 'image/*,application/pdf,text/*,application/json').split(',')
    
    # Feature Flags
    enable_file_upload: bool = os.getenv('ENABLE_FILE_UPLOAD', 'true').lower() == 'true'
    enable_real_time_chat: bool = os.getenv('ENABLE_REAL_TIME_CHAT', 'true').lower() == 'true'
    enable_whiteboard: bool = os.getenv('ENABLE_WHITEBOARD', 'true').lower() == 'true'
    enable_file_cleanup: bool = os.getenv('ENABLE_FILE_CLEANUP', 'true').lower() == 'true'
    
    # Security
    jwt_secret: str = os.getenv('JWT_SECRET', 'your-super-secret-jwt-key-here')
    rate_limit_per_minute: int = int(os.getenv('RATE_LIMIT_PER_MINUTE', '60'))
    
    # Logging
    log_level: str = os.getenv('LOG_LEVEL', 'INFO')
    
    @field_validator('cors_origins', mode='before')
    @classmethod
    def parse_cors_origins(cls, v):
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(',')]
        return v
    
    @field_validator('allowed_file_types', mode='before')
    @classmethod
    def parse_allowed_file_types(cls, v):
        if isinstance(v, str):
            return [file_type.strip() for file_type in v.split(',')]
        return v
    
    model_config = ConfigDict(
        env_file=".env",
        case_sensitive=False,
        extra='ignore'
    )

# Create global settings instance
settings = Settings()
