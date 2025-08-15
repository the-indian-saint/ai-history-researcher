"""Unit tests for configuration module."""

import pytest
from unittest.mock import patch
from pathlib import Path

from ai_research_framework.config import Settings


class TestSettings:
    """Test Settings class."""
    
    def test_default_settings(self):
        """Test default settings initialization."""
        settings = Settings()
        
        assert settings.app_name == "AI Research Framework"
        assert settings.environment == "development"
        assert settings.host == "0.0.0.0"
        assert settings.port == 8000
        assert settings.log_level == "INFO"
    
    def test_database_url_validation(self):
        """Test database URL validation."""
        # Valid SQLite URL
        settings = Settings(database_url="sqlite+aiosqlite:///test.db")
        assert settings.database_url == "sqlite+aiosqlite:///test.db"
        
        # Valid PostgreSQL URL
        settings = Settings(database_url="postgresql+asyncpg://user:pass@localhost/db")
        assert "postgresql+asyncpg" in settings.database_url
    
    def test_environment_specific_settings(self):
        """Test environment-specific settings."""
        # Development environment
        dev_settings = Settings(environment="development")
        assert dev_settings.environment == "development"
        
        # Production environment
        prod_settings = Settings(environment="production")
        assert prod_settings.environment == "production"
        
        # Test environment
        test_settings = Settings(environment="test")
        assert test_settings.environment == "test"
    
    def test_api_key_settings(self):
        """Test API key settings."""
        settings = Settings(
            openai_api_key="test-openai-key",
            anthropic_api_key="test-anthropic-key"
        )
        
        assert settings.openai_api_key == "test-openai-key"
        assert settings.anthropic_api_key == "test-anthropic-key"
    
    def test_redis_url_validation(self):
        """Test Redis URL validation."""
        settings = Settings(redis_url="redis://localhost:6379/0")
        assert settings.redis_url == "redis://localhost:6379/0"
    
    def test_log_level_validation(self):
        """Test log level validation."""
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        
        for level in valid_levels:
            settings = Settings(log_level=level)
            assert settings.log_level == level
    
    @patch.dict("os.environ", {
        "APP_NAME": "Test App",
        "ENVIRONMENT": "test",
        "HOST": "127.0.0.1",
        "PORT": "9000",
        "DATABASE_URL": "sqlite+aiosqlite:///test.db",
        "REDIS_URL": "redis://localhost:6379/1",
        "LOG_LEVEL": "DEBUG",
        "OPENAI_API_KEY": "env-openai-key",
        "ANTHROPIC_API_KEY": "env-anthropic-key"
    })
    def test_environment_variables(self):
        """Test loading settings from environment variables."""
        settings = Settings()
        
        assert settings.app_name == "Test App"
        assert settings.environment == "test"
        assert settings.host == "127.0.0.1"
        assert settings.port == 9000
        assert settings.database_url == "sqlite+aiosqlite:///test.db"
        assert settings.redis_url == "redis://localhost:6379/1"
        assert settings.log_level == "DEBUG"
        assert settings.openai_api_key == "env-openai-key"
        assert settings.anthropic_api_key == "env-anthropic-key"
    
    def test_model_config(self):
        """Test Pydantic model configuration."""
        settings = Settings()
        
        # Test that the model has the expected configuration
        assert hasattr(settings.model_config, 'env_file')
        assert hasattr(settings.model_config, 'env_file_encoding')
        assert hasattr(settings.model_config, 'case_sensitive')


class TestGetSettings:
    """Test get_settings function."""
    
    def test_get_settings_singleton(self):
        """Test that get_settings returns the same instance."""
        settings1 = get_settings()
        settings2 = get_settings()
        
        assert settings1 is settings2
    
    def test_get_settings_type(self):
        """Test that get_settings returns Settings instance."""
        settings = get_settings()
        assert isinstance(settings, Settings)
    
    @patch.dict("os.environ", {"ENVIRONMENT": "test"})
    def test_get_settings_with_env(self):
        """Test get_settings with environment variables."""
        # Clear any cached settings
        get_settings.cache_clear()
        
        settings = get_settings()
        assert settings.environment == "test"


class TestSettingsValidation:
    """Test settings validation."""
    
    def test_port_validation(self):
        """Test port number validation."""
        # Valid port
        settings = Settings(port=8080)
        assert settings.port == 8080
        
        # Test edge cases
        settings = Settings(port=1)
        assert settings.port == 1
        
        settings = Settings(port=65535)
        assert settings.port == 65535
    
    def test_host_validation(self):
        """Test host validation."""
        # Valid hosts
        valid_hosts = ["0.0.0.0", "127.0.0.1", "localhost", "example.com"]
        
        for host in valid_hosts:
            settings = Settings(host=host)
            assert settings.host == host
    
    def test_boolean_settings(self):
        """Test boolean settings."""
        settings = Settings()
        
        # Test default values
        assert isinstance(settings.debug, bool)
    
    def test_optional_settings(self):
        """Test optional settings."""
        settings = Settings()
        
        # These should be None by default
        assert settings.openai_api_key is None
        assert settings.anthropic_api_key is None
        assert settings.openai_api_base is None


@pytest.mark.unit
class TestSettingsIntegration:
    """Integration tests for settings."""
    
    def test_settings_with_file(self, temp_dir):
        """Test loading settings from file."""
        env_file = temp_dir / ".env"
        env_file.write_text("""
APP_NAME=File Test App
ENVIRONMENT=test
PORT=9999
LOG_LEVEL=DEBUG
""")
        
        settings = Settings(_env_file=str(env_file))
        
        assert settings.app_name == "File Test App"
        assert settings.environment == "test"
        assert settings.port == 9999
        assert settings.log_level == "DEBUG"
    
    def test_settings_precedence(self, temp_dir):
        """Test that direct parameters override environment variables."""
        env_file = temp_dir / ".env"
        env_file.write_text("APP_NAME=File App")
        
        with patch.dict("os.environ", {"APP_NAME": "Env App"}):
            # Direct parameter should override both file and env
            settings = Settings(
                app_name="Direct App",
                _env_file=str(env_file)
            )
            
            assert settings.app_name == "Direct App"

