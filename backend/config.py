
"""
Configuration settings for TruthGuard AI Backend
"""

import os
from typing import List, Optional
from pydantic import BaseSettings, validator

class Settings(BaseSettings):
    """Application settings"""

    # Basic app configuration
    APP_NAME: str = "TruthGuard AI"
    APP_VERSION: str = "2.0.0"
    DEBUG: bool = False
    TESTING: bool = False

    # Server configuration
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    WORKERS: int = 1

    # Security settings
    SECRET_KEY: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    ALGORITHM: str = "HS256"

    # CORS settings
    ALLOWED_ORIGINS: List[str] = ["*"]
    ALLOWED_HOSTS: List[str] = ["*"]

    # Database configuration
    DATABASE_URL: str = "postgresql://user:password@localhost/truthguard"
    DATABASE_ECHO: bool = False

    # Google Cloud configuration
    GOOGLE_CLOUD_PROJECT: str
    GOOGLE_APPLICATION_CREDENTIALS: Optional[str] = None
    VERTEX_AI_LOCATION: str = "us-central1"

    # Storage configuration
    CONTENT_BUCKET_NAME: Optional[str] = None
    MODEL_BUCKET_NAME: Optional[str] = None
    MAX_FILE_SIZE: int = 50 * 1024 * 1024  # 50MB

    # AI Model settings
    GEMINI_MODEL_VERSION: str = "gemini-2.0-flash"
    DEFAULT_CONFIDENCE_THRESHOLD: float = 0.7
    MAX_BATCH_SIZE: int = 10

    # WhatsApp Business API
    WHATSAPP_PHONE_NUMBER_ID: str = ""
    WHATSAPP_ACCESS_TOKEN: str = ""
    WHATSAPP_WEBHOOK_VERIFY_TOKEN: str = ""
    WHATSAPP_APP_ID: str = ""
    WHATSAPP_APP_SECRET: str = ""

    # External API keys
    FACT_CHECK_API_KEY: Optional[str] = None
    SOCIAL_MEDIA_API_KEYS: dict = {}

    # Redis configuration (for caching)
    REDIS_URL: Optional[str] = None
    CACHE_TTL: int = 3600  # 1 hour

    # Email configuration
    SMTP_SERVER: Optional[str] = None
    SMTP_PORT: int = 587
    SMTP_USERNAME: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    FROM_EMAIL: Optional[str] = None

    # Monitoring and logging
    LOG_LEVEL: str = "INFO"
    SENTRY_DSN: Optional[str] = None
    ENABLE_METRICS: bool = True
    METRICS_PORT: int = 9090

    # Rate limiting
    RATE_LIMIT_PER_MINUTE: int = 60
    RATE_LIMIT_PER_HOUR: int = 1000
    PREMIUM_RATE_LIMIT_MULTIPLIER: int = 10

    # Webhook settings
    WEBHOOK_SECRET: Optional[str] = None
    WEBHOOK_TIMEOUT: int = 30

    # Feature flags
    ENABLE_COMMUNITY_REPORTS: bool = True
    ENABLE_EDUCATION_MODULES: bool = True
    ENABLE_BLOCKCHAIN_VERIFICATION: bool = True
    ENABLE_WHATSAPP_INTEGRATION: bool = True
    ENABLE_SOCIAL_MEDIA_MONITORING: bool = False

    # Performance settings
    MAX_CONCURRENT_ANALYSES: int = 100
    ANALYSIS_TIMEOUT: int = 300  # 5 minutes
    CLEANUP_INTERVAL: int = 3600  # 1 hour

    @validator("ALLOWED_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v):
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)

    @validator("ALLOWED_HOSTS", pre=True)
    def assemble_allowed_hosts(cls, v):
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)

    @validator("CONTENT_BUCKET_NAME", pre=True, always=True)
    def set_content_bucket_name(cls, v, values):
        if not v:
            return f"{values.get('GOOGLE_CLOUD_PROJECT', 'truthguard')}-content-storage"
        return v

    @validator("MODEL_BUCKET_NAME", pre=True, always=True)
    def set_model_bucket_name(cls, v, values):
        if not v:
            return f"{values.get('GOOGLE_CLOUD_PROJECT', 'truthguard')}-model-artifacts"
        return v

    class Config:
        env_file = ".env"
        case_sensitive = True

# Create settings instance
settings = Settings()

# Environment-specific settings
if settings.DEBUG:
    settings.LOG_LEVEL = "DEBUG"
    settings.DATABASE_ECHO = True

# Production overrides
if not settings.DEBUG:
    settings.ALLOWED_ORIGINS = [
        "https://truthguard.ai",
        "https://www.truthguard.ai",
        "https://api.truthguard.ai"
    ]
    settings.ALLOWED_HOSTS = [
        "truthguard.ai",
        "www.truthguard.ai", 
        "api.truthguard.ai"
    ]
