import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from ai_research_framework.analyzers.ai_analyzer import analyzer, AnalysisType
from ai_research_framework.collectors.web_scraper import web_scraper
from ai_research_framework.config import settings

@pytest.mark.asyncio
async def test_local_credibility_analysis():
    """Test credibility analysis with local model setting."""
    # Force settings
    settings.use_local_model = True
    settings.local_model_name = "phi3:mini"
    
    mock_response = {
        "score": 0.9,
        "level": "very_high",
        "factors": {"authority": 0.9},
        "reasoning": "Test reasoning",
        "confidence": 0.95
    }
    
    # Mock the _call_llm method directly to avoid mocking openai client internals complexity
    with patch.object(analyzer, '_call_llm', new_callable=AsyncMock) as mock_call:
        mock_call.return_value = '```json\n{"score": 0.9, "level": "very_high", "factors": {"authority": 0.9}, "reasoning": "Test reasoning", "confidence": 0.95}\n```'
        
        result = await analyzer.analyze_document_credibility("Test text")
        
        assert result.success
        assert result.result.score == 0.9
        assert result.result.level == "very_high"
        mock_call.assert_called_once()
        assert "response_format" in mock_call.call_args[1]

@pytest.mark.asyncio
async def test_real_web_scraping_mock():
    """Test web scraper with mocked network calls."""
    mock_html = "<html><head><title>Test Page</title></head><body><p>Test content paragraph.</p></body></html>"
    
    with patch("aiohttp.ClientSession.get") as mock_get:
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.text.return_value = mock_html
        mock_response.__aenter__.return_value = mock_response
        mock_get.return_value.__aenter__.return_value = mock_response
        
        result = await web_scraper.scrape_url("http://test.com")
        
        assert result.success
        assert result.title == "Test Page"
        assert "Test content paragraph" in result.content
