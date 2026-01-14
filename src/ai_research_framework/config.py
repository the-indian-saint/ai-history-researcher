"""Configuration management for the AI Research Framework."""

import os
from functools import lru_cache
from typing import List, Optional
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings with environment variable support."""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )
    
    # Application
    app_name: str = Field(default="AI Research Framework", description="Application name")
    app_version: str = Field(default="0.1.0", description="Application version")
    debug: bool = Field(default=False, description="Debug mode")
    environment: str = Field(default="development", description="Environment (development, staging, production)")
    
    # Server
    host: str = Field(default="0.0.0.0", description="Server host")
    port: int = Field(default=8000, description="Server port")
    workers: int = Field(default=1, description="Number of worker processes")
    
    # Database
    database_url: str = Field(
        default="sqlite+aiosqlite:///./research.db",
        description="Database connection URL"
    )
    database_pool_size: int = Field(default=10, description="Database connection pool size")
    database_max_overflow: int = Field(default=20, description="Database max overflow connections")
    
    # Redis
    redis_url: str = Field(default="redis://localhost:6379", description="Redis connection URL")
    redis_db: int = Field(default=0, description="Redis database number")
    redis_password: str = Field(default="", description="Redis password")
    
    # ChromaDB
    chromadb_host: str = Field(default="localhost", description="ChromaDB host")
    chromadb_port: int = Field(default=8001, description="ChromaDB port")
    chromadb_collection_name: str = Field(default="research_documents", description="ChromaDB collection name")
    
    # AI Services
    openai_api_key: Optional[str] = Field(default="your_openai_api_key_here", description="OpenAI API key")
    openai_api_base: Optional[str] = Field(default="", description="OpenAI API base URL")
    anthropic_api_key: Optional[str] = Field(default="your_anthropic_api_key_here", description="Anthropic API key")
    
    # Local Model
    use_local_model: bool = Field(default=False, description="Use local model instead of cloud APIs")
    local_model_base_url: str = Field(default="http://ollama:11434/v1", description="Local model base URL (OpenAI compatible)")
    local_model_name: str = Field(default="phi3:mini", description="Local model name")
    
    # OCR Configuration
    tesseract_cmd: str = Field(default="/usr/bin/tesseract", description="Tesseract command path")
    ocr_confidence_threshold: float = Field(default=80.0, description="OCR confidence threshold (0-100)")
    ocr_languages: List[str] = Field(
        default=["eng", "hin", "san"],
        description="OCR languages to use"
    )
    
    # Document Processing
    max_file_size: int = Field(default=100 * 1024 * 1024, description="Maximum file size in bytes (100MB)")
    supported_formats: List[str] = Field(
        default=["pdf", "docx", "txt", "jpg", "png", "tiff"],
        description="Supported document formats"
    )
    processing_timeout: int = Field(default=300, description="Document processing timeout in seconds")
    
    # Web Scraping
    scraping_delay: float = Field(default=1.0, description="Delay between scraping requests in seconds")
    scraping_timeout: int = Field(default=30, description="Scraping request timeout in seconds")
    scraping_retries: int = Field(default=3, description="Number of scraping retries")
    user_agent: str = Field(
        default="AI Research Framework/0.1.0 (Educational Research)",
        description="User agent for web scraping"
    )
    
    # Rate Limiting
    rate_limit_requests: int = Field(default=100, description="Rate limit requests per minute")
    rate_limit_window: int = Field(default=60, description="Rate limit window in seconds")
    
    # Security
    jwt_secret_key: str = Field(default="your-secret-key-change-in-production", description="JWT secret key")
    jwt_algorithm: str = Field(default="HS256", description="JWT algorithm")
    jwt_expire_minutes: int = Field(default=60, description="JWT token expiration in minutes")
    
    # CORS
    cors_origins: List[str] = Field(
        default=["http://localhost:3000", "http://localhost:8080"],
        description="CORS allowed origins"
    )
    cors_allow_credentials: bool = Field(default=True, description="CORS allow credentials")
    cors_allow_methods: List[str] = Field(
        default=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        description="CORS allowed methods"
    )
    cors_allow_headers: List[str] = Field(default=["*"], description="CORS allowed headers")
    
    # Logging
    log_level: str = Field(default="INFO", description="Logging level")
    log_format: str = Field(default="json", description="Log format (json or text)")
    log_file: Optional[str] = Field(default=None, description="Log file path")
    
    # Monitoring
    enable_metrics: bool = Field(default=True, description="Enable Prometheus metrics")
    metrics_port: int = Field(default=9090, description="Metrics server port")
    
    # Storage
    storage_path: str = Field(default="./data", description="Local storage path")
    backup_path: str = Field(default="./backups", description="Backup storage path")
    temp_path: str = Field(default="./temp", description="Temporary files path")
    
    # Research Configuration
    max_sources_per_query: int = Field(default=50, description="Maximum sources per research query")
    default_time_range_years: int = Field(default=100, description="Default time range for queries in years")
    credibility_threshold: float = Field(default=0.6, description="Minimum credibility score (0-1)")
    
    # Language Processing
    default_language: str = Field(default="english", description="Default language for processing")
    supported_languages: List[str] = Field(
        default=["english", "hindi", "sanskrit", "tamil"],
        description="Supported languages for processing"
    )
    
    @property
    def is_development(self) -> bool:
        """Check if running in development mode."""
        return self.environment.lower() == "development"
    
    @property
    def is_production(self) -> bool:
        """Check if running in production mode."""
        return self.environment.lower() == "production"
    
    @property
    def database_url_sync(self) -> str:
        """Get synchronous database URL."""
        if self.database_url.startswith("postgresql+asyncpg://"):
            return self.database_url.replace("postgresql+asyncpg://", "postgresql://")
        return self.database_url
    
    def get_chromadb_url(self) -> str:
        """Get ChromaDB connection URL."""
        return f"http://{self.chromadb_host}:{self.chromadb_port}"
    
    def create_directories(self) -> None:
        """Create necessary directories."""
        directories = [self.storage_path, self.backup_path, self.temp_path]
        for directory in directories:
            os.makedirs(directory, exist_ok=True)


# Global settings instance
settings = Settings()

# Create necessary directories on import
settings.create_directories()


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance.
    
    Returns:
        Settings: Application settings instance
    """
    return Settings()

