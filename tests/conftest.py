"""Pytest configuration and shared fixtures."""

import asyncio
import os
import tempfile
import pytest
from pathlib import Path
from typing import AsyncGenerator, Generator
from unittest.mock import AsyncMock, MagicMock

import httpx
from fastapi.testclient import TestClient

# Add src to path for imports
import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from ai_research_framework.config import Settings
from ai_research_framework.api.main import app
from ai_research_framework.storage.database import get_database, init_database


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def temp_dir() -> Generator[Path, None, None]:
    """Create a temporary directory for tests."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        yield Path(tmp_dir)


@pytest.fixture
def test_settings(temp_dir: Path) -> Settings:
    """Create test settings with temporary database."""
    return Settings(
        app_name="AI Research Framework Test",
        environment="test",
        database_url=f"sqlite+aiosqlite:///{temp_dir}/test.db",
        redis_url="redis://localhost:6379/1",  # Use different DB for tests
        log_level="DEBUG",
        openai_api_key="test-key",
        anthropic_api_key="test-key"
    )


@pytest.fixture
async def test_db(test_settings: Settings):
    """Create test database."""
    # Override settings for testing
    original_settings = None
    try:
        # Initialize test database
        await init_database()
        yield
    finally:
        # Cleanup would go here if needed
        pass


@pytest.fixture
def client(test_settings: Settings) -> TestClient:
    """Create test client for API testing."""
    return TestClient(app)


@pytest.fixture
async def async_client() -> AsyncGenerator[httpx.AsyncClient, None]:
    """Create async test client."""
    async with httpx.AsyncClient(app=app, base_url="http://test") as client:
        yield client


@pytest.fixture
def sample_text() -> str:
    """Sample historical text for testing."""
    return """
    The Maurya Empire was an ancient Indian empire that existed from 321 to 185 BCE. 
    Founded by Chandragupta Maurya, it was one of the largest empires in the world at its time.
    The empire was known for its sophisticated administrative system and the famous emperor Ashoka,
    who promoted Buddhism throughout his realm. The capital was located at Pataliputra,
    modern-day Patna in Bihar.
    """


@pytest.fixture
def sample_metadata() -> dict:
    """Sample metadata for testing."""
    return {
        "source_type": "academic",
        "author": "Dr. Test Historian",
        "publication": "Journal of Ancient Indian History",
        "year": 2023,
        "source_url": "https://example.com/maurya-empire"
    }


@pytest.fixture
def sample_research_data() -> list:
    """Sample research data for testing."""
    return [
        {
            "title": "Maurya Empire Administration",
            "content": "The Maurya Empire had a sophisticated administrative system with a centralized government...",
            "author": "Dr. Ancient History",
            "source_url": "https://example.com/maurya-admin",
            "credibility_score": 0.9
        },
        {
            "title": "Ashoka's Edicts and Buddhism",
            "content": "Emperor Ashoka's conversion to Buddhism marked a significant shift in imperial policy...",
            "author": "Prof. Buddhist Studies",
            "source_url": "https://example.com/ashoka-edicts",
            "credibility_score": 0.85
        }
    ]


@pytest.fixture
def mock_openai_client():
    """Mock OpenAI client for testing."""
    mock_client = AsyncMock()
    mock_response = AsyncMock()
    mock_response.choices = [AsyncMock()]
    mock_response.choices[0].message.content = '{"score": 0.8, "level": "high", "reasoning": "Test response"}'
    mock_client.chat.completions.create.return_value = mock_response
    return mock_client


@pytest.fixture
def mock_anthropic_client():
    """Mock Anthropic client for testing."""
    mock_client = AsyncMock()
    mock_response = AsyncMock()
    mock_response.content = [AsyncMock()]
    mock_response.content[0].text = '{"score": 0.8, "level": "high", "reasoning": "Test response"}'
    mock_client.messages.create.return_value = mock_response
    return mock_client


@pytest.fixture
def sample_pdf_file(temp_dir: Path) -> Path:
    """Create a sample PDF file for testing."""
    pdf_path = temp_dir / "sample.pdf"
    # Create a simple text file as PDF placeholder
    pdf_path.write_text("Sample PDF content for testing document processing.")
    return pdf_path


@pytest.fixture
def sample_docx_file(temp_dir: Path) -> Path:
    """Create a sample DOCX file for testing."""
    docx_path = temp_dir / "sample.docx"
    docx_path.write_text("Sample DOCX content for testing document processing.")
    return docx_path


@pytest.fixture
def sample_txt_file(temp_dir: Path) -> Path:
    """Create a sample text file for testing."""
    txt_path = temp_dir / "sample.txt"
    txt_path.write_text("Sample text content for testing document processing.")
    return txt_path


@pytest.fixture
def mock_redis():
    """Mock Redis client for testing."""
    mock_redis = AsyncMock()
    mock_redis.get.return_value = None
    mock_redis.set.return_value = True
    mock_redis.delete.return_value = 1
    mock_redis.exists.return_value = False
    return mock_redis


@pytest.fixture
def mock_database():
    """Mock database for testing."""
    mock_db = AsyncMock()
    return mock_db


# Markers for different test types
pytest_plugins = []


def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line("markers", "unit: Unit tests")
    config.addinivalue_line("markers", "integration: Integration tests")
    config.addinivalue_line("markers", "api: API endpoint tests")
    config.addinivalue_line("markers", "slow: Slow running tests")
    config.addinivalue_line("markers", "external: Tests requiring external services")


@pytest.fixture(autouse=True)
def setup_test_environment(monkeypatch):
    """Set up test environment variables."""
    monkeypatch.setenv("ENVIRONMENT", "test")
    monkeypatch.setenv("DATABASE_URL", "sqlite+aiosqlite:///:memory:")
    monkeypatch.setenv("LOG_LEVEL", "DEBUG")


class MockResponse:
    """Mock HTTP response for testing."""
    
    def __init__(self, json_data=None, status_code=200, text=""):
        self.json_data = json_data or {}
        self.status_code = status_code
        self.text = text
    
    def json(self):
        return self.json_data
    
    def raise_for_status(self):
        if self.status_code >= 400:
            raise httpx.HTTPStatusError(
                message=f"HTTP {self.status_code}",
                request=None,
                response=self
            )


@pytest.fixture
def mock_http_response():
    """Factory for creating mock HTTP responses."""
    def _create_response(json_data=None, status_code=200, text=""):
        return MockResponse(json_data, status_code, text)
    return _create_response

