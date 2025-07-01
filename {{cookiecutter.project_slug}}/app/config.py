"""Configuration management using Pydantic settings."""

from functools import lru_cache

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from portia import LogLevel, StorageClass


class Settings(BaseSettings):
    """Application settings managed via environment variables."""

    # FastAPI Configuration
    app_name: str = Field(default="{{ cookiecutter.project_name }}", description="Application name")
    app_version: str = Field(default="{{ cookiecutter.version }}", description="Application version")
    debug: bool = Field(default=False, description="Debug mode")
    log_level: str = Field(default="INFO", description="Logging level")

    # Server Configuration
    host: str = Field(default="0.0.0.0", description="Host to bind the server")
    port: int = Field(default={{ cookiecutter.port }}, description="Port to bind the server")

    # Portia Configuration
    portia_log_level: LogLevel = Field(
        default=LogLevel.{{ cookiecutter.portia_log_level }},
        description="Portia SDK log level",
    )
    portia_storage_class: StorageClass = Field(
        default=StorageClass.{{ cookiecutter.portia_storage_class }},
        description="Portia storage class (MEMORY, DISK, or CLOUD)",
    )

    # API Keys (loaded from environment)
    openai_api_key: str | None = Field(default=None, description="OpenAI API key")
    anthropic_api_key: str | None = Field(default=None, description="Anthropic API key")
    mistral_api_key: str | None = Field(default=None, description="Mistral API key")
    google_api_key: str | None = Field(default=None, description="Google API key")
    portia_api_key: str | None = Field(default=None, description="Portia Cloud API key")

    # Additional Configuration
    max_request_size: int = Field(
        default=1_000_000,  # 1MB
        description="Maximum request size in bytes",
    )
    request_timeout: int = Field(
        default=300,  # 5 minutes
        description="Request timeout in seconds",
    )

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    def has_llm_api_key(self) -> bool:
        """Check if at least one LLM API key is configured."""
        return any(
            [
                self.openai_api_key,
                self.anthropic_api_key,
                self.mistral_api_key,
                self.google_api_key,
            ]
        )

    def get_portia_storage_class(self) -> StorageClass:
        """Get the appropriate storage class based on configuration."""
        if self.portia_api_key and self.portia_storage_class == StorageClass.CLOUD:
            return StorageClass.CLOUD
        elif self.portia_storage_class == StorageClass.DISK:
            return StorageClass.DISK
        return StorageClass.MEMORY

    @field_validator("port")
    @classmethod
    def validate_port(cls, v: int) -> int:
        """Validate port number is in valid range."""
        if not (1 <= v <= 65535):
            raise ValueError("Port must be between 1 and 65535")
        return v

    @field_validator("log_level")
    @classmethod
    def validate_log_level(cls, v: str) -> str:
        """Validate log level is valid."""
        valid_levels = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}
        if v.upper() not in valid_levels:
            raise ValueError(f"Log level must be one of: {', '.join(valid_levels)}")
        return v.upper()


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
