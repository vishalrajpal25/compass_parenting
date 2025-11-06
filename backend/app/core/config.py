"""
Application configuration using Pydantic settings.
Validates environment variables on startup.
"""
from functools import lru_cache
from typing import Optional

from pydantic import Field, PostgresDsn, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings with environment variable validation."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )

    # Application
    app_name: str = Field(default="Compass", description="Application name")
    app_version: str = Field(default="0.1.0", description="Application version")
    debug: bool = Field(default=False, description="Debug mode")
    environment: str = Field(default="development", description="Environment (development, staging, production)")

    # API
    api_v1_prefix: str = Field(default="/api/v1", description="API v1 prefix")

    # CORS
    cors_origins: list[str] = Field(
        default=["http://localhost:5173", "http://localhost:3000"],
        description="Allowed CORS origins"
    )

    # Database
    database_url: PostgresDsn = Field(
        default="postgresql+asyncpg://compass:compass_dev_password@localhost:5433/compass",
        description="PostgreSQL database URL"
    )
    database_echo: bool = Field(default=False, description="Echo SQL queries")

    # Redis
    redis_url: str = Field(default="redis://localhost:6379/0", description="Redis URL")

    # Security
    secret_key: str = Field(
        default="CHANGE_ME_IN_PRODUCTION_THIS_IS_INSECURE",
        description="Secret key for JWT signing"
    )
    algorithm: str = Field(default="HS256", description="JWT algorithm")
    access_token_expire_minutes: int = Field(
        default=30,
        description="Access token expiration in minutes"
    )
    refresh_token_expire_days: int = Field(
        default=7,
        description="Refresh token expiration in days"
    )

    # Password hashing
    pwd_context_schemes: list[str] = Field(
        default=["bcrypt"],
        description="Password hashing schemes"
    )
    pwd_context_deprecated: str = Field(
        default="auto",
        description="Deprecated password schemes"
    )

    # Qdrant
    qdrant_url: str = Field(default="http://localhost:6333", description="Qdrant URL")
    qdrant_api_key: Optional[str] = Field(default=None, description="Qdrant API key")

    # External APIs
    openai_api_key: Optional[str] = Field(default=None, description="OpenAI API key")
    anthropic_api_key: Optional[str] = Field(default=None, description="Anthropic API key")
    sendgrid_api_key: Optional[str] = Field(default=None, description="SendGrid API key")
    sendgrid_from_email: Optional[str] = Field(
        default=None,
        description="SendGrid from email"
    )

    # Feature flags
    llm_qa_enabled: bool = Field(default=False, description="Enable LLM Q&A feature")
    bandits_enabled: bool = Field(
        default=False,
        description="Enable multi-armed bandits for A/B testing"
    )

    # Geospatial
    default_search_radius_km: float = Field(
        default=15.0,
        description="Default search radius in kilometers"
    )
    max_commute_time_minutes: int = Field(
        default=30,
        description="Maximum commute time in minutes"
    )

    @field_validator("database_url", mode="before")
    @classmethod
    def validate_database_url(cls, v: str) -> str:
        """Ensure database URL is properly formatted."""
        if isinstance(v, str) and not v.startswith(("postgresql://", "postgresql+asyncpg://")):
            raise ValueError("Database URL must use postgresql:// or postgresql+asyncpg://")
        return v

    @property
    def database_url_str(self) -> str:
        """Get database URL as string."""
        return str(self.database_url)


@lru_cache()
def get_settings() -> Settings:
    """
    Get cached settings instance.

    Uses lru_cache to ensure settings are only loaded once.
    """
    return Settings()


# Global settings instance
settings = get_settings()
