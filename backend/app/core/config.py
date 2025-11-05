"""
Application configuration settings.
"""
from typing import List, Optional
from pydantic import AnyHttpUrl, EmailStr, PostgresDsn, RedisDsn, validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Demo Mode - bypasses database, Stripe, and email requirements
    DEMO_MODE: bool = False

    # Application
    APP_NAME: str = "Citizen Journalism Platform"
    VERSION: str = "1.0.0"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    LOG_LEVEL: str = "INFO"

    # API
    API_V1_PREFIX: str = "/api/v1"

    # Security
    SECRET_KEY: str = "demo-secret-key-change-in-production"
    JWT_SECRET_KEY: str = "demo-jwt-secret-key-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    PASSWORD_MIN_LENGTH: int = 12
    MAX_LOGIN_ATTEMPTS: int = 5
    ACCOUNT_LOCKOUT_DURATION_MINUTES: int = 30

    # Database (optional in demo mode)
    DATABASE_URL: Optional[PostgresDsn] = None
    DB_ECHO_LOG: bool = False
    DB_POOL_SIZE: int = 20
    DB_MAX_OVERFLOW: int = 10

    # Redis (optional in demo mode)
    REDIS_URL: Optional[RedisDsn] = None
    REDIS_CACHE_EXPIRE_SECONDS: int = 3600

    # Elasticsearch (optional in demo mode)
    ELASTICSEARCH_URL: Optional[str] = None

    # CORS
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = []

    @validator("BACKEND_CORS_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v: str | List[str]) -> List[str] | str:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)

    # Frontend URL
    FRONTEND_URL: AnyHttpUrl = "http://localhost:3000"

    # Email (optional in demo mode)
    EMAIL_HOST: Optional[str] = None
    EMAIL_PORT: int = 587
    EMAIL_USERNAME: Optional[str] = None
    EMAIL_PASSWORD: Optional[str] = None
    EMAIL_FROM: Optional[EmailStr] = None
    EMAIL_USE_TLS: bool = True

    # Stripe (optional in demo mode)
    STRIPE_SECRET_KEY: Optional[str] = None
    STRIPE_PUBLISHABLE_KEY: Optional[str] = None
    STRIPE_WEBHOOK_SECRET: Optional[str] = None
    PLATFORM_FEE_PERCENTAGE: int = 15
    MINIMUM_PAYOUT_USD: int = 10
    PAYOUT_SCHEDULE: str = "weekly"

    # AWS S3 (optional in demo mode)
    AWS_ACCESS_KEY_ID: Optional[str] = None
    AWS_SECRET_ACCESS_KEY: Optional[str] = None
    AWS_S3_BUCKET: Optional[str] = None
    AWS_REGION: str = "us-east-1"

    # AI Services
    OPENAI_API_KEY: Optional[str] = None
    ANTHROPIC_API_KEY: Optional[str] = None

    # Sentry
    SENTRY_DSN: Optional[str] = None

    # Rate Limiting
    RATE_LIMIT_AUTHENTICATED: int = 100
    RATE_LIMIT_ANONYMOUS: int = 20

    # Content Settings
    MAX_FILE_SIZE_MB: int = 10
    ALLOWED_IMAGE_TYPES: List[str] = ["jpg", "jpeg", "png", "gif", "webp"]
    ARTICLES_PER_PAGE: int = 20
    DRAFT_AUTOSAVE_INTERVAL_SECONDS: int = 30

    # Pagination
    MAX_PAGE_SIZE: int = 100
    DEFAULT_PAGE_SIZE: int = 20

    class Config:
        env_file = ".env"
        case_sensitive = True


# Global settings instance
settings = Settings()
