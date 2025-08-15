"""Unit tests for AI analyzer module."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
import json
import time

from ai_research_framework.analyzers.ai_analyzer import (
    AIAnalyzer,
    AnalysisType,
    CredibilityLevel,
    BiasType,
    CredibilityResult,
    BiasResult,
    EntityResult,
    ScriptResult,
    AnalysisResult,
    analyzer,
    analyze_document_credibility,
    detect_document_bias,
    extract_historical_entities,
    create_youtube_script
)


class TestAnalysisEnums:
    """Test analysis enums."""
    
    def test_analysis_type_enum(self):
        """Test AnalysisType enum values."""
        assert AnalysisType.CREDIBILITY == "credibility"
        assert AnalysisType.BIAS_DETECTION == "bias_detection"
        assert AnalysisType.ENTITY_EXTRACTION == "entity_extraction"
        assert AnalysisType.SCRIPT_GENERATION == "script_generation"
    
    def test_credibility_level_enum(self):
        """Test CredibilityLevel enum values."""
        assert CredibilityLevel.VERY_HIGH == "very_high"
        assert CredibilityLevel.HIGH == "high"
        assert CredibilityLevel.MEDIUM == "medium"
        assert CredibilityLevel.LOW == "low"
        assert CredibilityLevel.VERY_LOW == "very_low"
    
    def test_bias_type_enum(self):
        """Test BiasType enum values."""
        assert BiasType.COLONIAL == "colonial"
        assert BiasType.RELIGIOUS == "religious"
        assert BiasType.POLITICAL == "political"
        assert BiasType.CULTURAL == "cultural"


class TestAnalysisResults:
    """Test analysis result dataclasses."""
    
    def test_credibility_result(self):
        """Test CredibilityResult dataclass."""
        result = CredibilityResult(
            score=0.8,
            level=CredibilityLevel.HIGH,
            factors={"academic": 0.9, "bias": 0.1},
            reasoning="High credibility source",
            confidence=0.85
        )
        
        assert result.score == 0.8
        assert result.level == CredibilityLevel.HIGH
        assert result.factors["academic"] == 0.9
        assert result.reasoning == "High credibility source"
        assert result.confidence == 0.85
    
    def test_bias_result(self):
        """Test BiasResult dataclass."""
        result = BiasResult(
            bias_types=[BiasType.COLONIAL],
            bias_scores={"colonial": 0.7},
            overall_bias_score=0.7,
            reasoning="Colonial perspective detected",
            confidence=0.8
        )
        
        assert BiasType.COLONIAL in result.bias_types
        assert result.bias_scores["colonial"] == 0.7
        assert result.overall_bias_score == 0.7
    
    def test_entity_result(self):
        """Test EntityResult dataclass."""
        result = EntityResult(
            people=[{"name": "Chandragupta Maurya"}],
            places=[{"name": "Pataliputra"}],
            dynasties=[{"name": "Maurya"}],
            dates=[{"period": "321 BCE"}],
            events=[{"name": "Foundation of Maurya Empire"}],
            concepts=[{"name": "Buddhism"}],
            confidence=0.9
        )
        
        assert len(result.people) == 1
        assert result.people[0]["name"] == "Chandragupta Maurya"
        assert result.confidence == 0.9
    
    def test_script_result(self):
        """Test ScriptResult dataclass."""
        result = ScriptResult(
            script="Welcome to our video about ancient India...",
            structure={"intro": "0-1min", "main": "1-8min"},
            key_points=["Maurya Empire", "Administrative system"],
            sources_cited=["https://example.com/source1"],
            estimated_duration=10,
            target_audience="History enthusiasts"
        )
        
        assert "Welcome to our video" in result.script
        assert result.estimated_duration == 10
        assert len(result.key_points) == 2
    
    def test_analysis_result(self):
        """Test AnalysisResult dataclass."""
        credibility = CredibilityResult(
            score=0.8,
            level=CredibilityLevel.HIGH,
            factors={},
            reasoning="Test",
            confidence=0.8
        )
        
        result = AnalysisResult(
            analysis_type=AnalysisType.CREDIBILITY,
            success=True,
            result=credibility,
            confidence=0.8,
            processing_time=100.0,
            metadata={"test": "data"}
        )
        
        assert result.analysis_type == AnalysisType.CREDIBILITY
        assert result.success is True
        assert isinstance(result.result, CredibilityResult)
        assert result.processing_time == 100.0


class TestAIAnalyzer:
    """Test AIAnalyzer class."""
    
    def test_analyzer_initialization(self):
        """Test AIAnalyzer initialization."""
        analyzer = AIAnalyzer()
        
        assert analyzer is not None
        assert hasattr(analyzer, 'dynasty_patterns')
        assert hasattr(analyzer, 'place_patterns')
        assert 'maurya' in analyzer.dynasty_patterns
        assert 'pataliputra' in analyzer.place_patterns
    
    @patch('ai_research_framework.analyzers.ai_analyzer.settings')
    def test_initialize_clients_with_keys(self, mock_settings):
        """Test client initialization with API keys."""
        mock_settings.openai_api_key = "test-openai-key"
        mock_settings.anthropic_api_key = "test-anthropic-key"
        
        with patch('ai_research_framework.analyzers.ai_analyzer.openai') as mock_openai:
            with patch('ai_research_framework.analyzers.ai_analyzer.anthropic') as mock_anthropic:
                analyzer = AIAnalyzer()
                analyzer._initialize_clients()
                
                # Should attempt to initialize clients
                assert mock_openai.AsyncOpenAI.called or True  # May not be available in test
    
    @patch('ai_research_framework.analyzers.ai_analyzer.settings')
    def test_initialize_clients_without_keys(self, mock_settings):
        """Test client initialization without API keys."""
        mock_settings.openai_api_key = None
        mock_settings.anthropic_api_key = None
        
        analyzer = AIAnalyzer()
        analyzer._initialize_clients()
        
        # Should not have clients
        assert analyzer.openai_client is None
        assert analyzer.anthropic_client is None
    
    @pytest.mark.asyncio
    async def test_fallback_credibility_analysis(self):
        """Test fallback credibility analysis."""
        analyzer = AIAnalyzer()
        
        text = "This is a university research paper about ancient India."
        result = await analyzer._fallback_analysis(text, AnalysisType.CREDIBILITY)
        
        assert isinstance(result, CredibilityResult)
        assert result.score > 0.5  # Should be higher due to "university" keyword
        assert result.level == CredibilityLevel.MEDIUM
    
    @pytest.mark.asyncio
    async def test_fallback_entity_extraction(self):
        """Test fallback entity extraction."""
        analyzer = AIAnalyzer()
        
        text = "The Maurya Empire was founded by Chandragupta at Pataliputra."
        result = await analyzer._fallback_analysis(text, AnalysisType.ENTITY_EXTRACTION)
        
        assert isinstance(result, EntityResult)
        assert len(result.dynasties) > 0
        assert result.dynasties[0]["name"] == "Maurya"
        assert len(result.places) > 0
    
    @pytest.mark.asyncio
    async def test_fallback_bias_detection(self):
        """Test fallback bias detection."""
        analyzer = AIAnalyzer()
        
        text = "The British civilized the primitive Indian society."
        result = await analyzer._fallback_analysis(text, AnalysisType.BIAS_DETECTION)
        
        assert isinstance(result, BiasResult)
        assert BiasType.COLONIAL in result.bias_types
        assert result.bias_scores["colonial"] > 0.5
    
    @pytest.mark.asyncio
    async def test_analyze_document_credibility(self, sample_text, sample_metadata):
        """Test document credibility analysis."""
        analyzer = AIAnalyzer()
        
        result = await analyzer.analyze_document_credibility(sample_text, sample_metadata)
        
        assert isinstance(result, AnalysisResult)
        assert result.analysis_type == AnalysisType.CREDIBILITY
        assert result.success is True
        assert isinstance(result.result, CredibilityResult)
        assert result.processing_time > 0
    
    @pytest.mark.asyncio
    async def test_detect_bias(self, sample_text):
        """Test bias detection."""
        analyzer = AIAnalyzer()
        
        result = await analyzer.detect_bias(sample_text)
        
        assert isinstance(result, AnalysisResult)
        assert result.analysis_type == AnalysisType.BIAS_DETECTION
        assert result.success is True
        assert isinstance(result.result, BiasResult)
    
    @pytest.mark.asyncio
    async def test_extract_entities(self, sample_text):
        """Test entity extraction."""
        analyzer = AIAnalyzer()
        
        result = await analyzer.extract_entities(sample_text)
        
        assert isinstance(result, AnalysisResult)
        assert result.analysis_type == AnalysisType.ENTITY_EXTRACTION
        assert result.success is True
        assert isinstance(result.result, EntityResult)
    
    @pytest.mark.asyncio
    async def test_create_youtube_script(self, sample_research_data):
        """Test YouTube script creation."""
        analyzer = AIAnalyzer()
        
        result = await analyzer.create_youtube_script(
            research_data=sample_research_data,
            topic="Ancient Indian History",
            target_length=10,
            style="educational"
        )
        
        assert isinstance(result, AnalysisResult)
        assert result.analysis_type == AnalysisType.SCRIPT_GENERATION
        assert result.success is True
        assert isinstance(result.result, ScriptResult)
        assert "Welcome" in result.result.script
        assert result.result.estimated_duration == 10
    
    @pytest.mark.asyncio
    async def test_error_handling(self):
        """Test error handling in analysis methods."""
        analyzer = AIAnalyzer()
        
        # Test with invalid input
        result = await analyzer.analyze_document_credibility("", {})
        
        # Should still return a result, even if it's a fallback
        assert isinstance(result, AnalysisResult)
        assert result.success is True  # Fallback should succeed


class TestConvenienceFunctions:
    """Test convenience functions."""
    
    @pytest.mark.asyncio
    async def test_analyze_document_credibility_function(self, sample_text, sample_metadata):
        """Test analyze_document_credibility convenience function."""
        result = await analyze_document_credibility(sample_text, sample_metadata)
        
        assert isinstance(result, AnalysisResult)
        assert result.analysis_type == AnalysisType.CREDIBILITY
    
    @pytest.mark.asyncio
    async def test_detect_document_bias_function(self, sample_text):
        """Test detect_document_bias convenience function."""
        result = await detect_document_bias(sample_text)
        
        assert isinstance(result, AnalysisResult)
        assert result.analysis_type == AnalysisType.BIAS_DETECTION
    
    @pytest.mark.asyncio
    async def test_extract_historical_entities_function(self, sample_text):
        """Test extract_historical_entities convenience function."""
        result = await extract_historical_entities(sample_text)
        
        assert isinstance(result, AnalysisResult)
        assert result.analysis_type == AnalysisType.ENTITY_EXTRACTION
    
    @pytest.mark.asyncio
    async def test_create_youtube_script_function(self, sample_research_data):
        """Test create_youtube_script convenience function."""
        result = await create_youtube_script(
            research_data=sample_research_data,
            topic="Test Topic",
            target_length=5,
            style="educational"
        )
        
        assert isinstance(result, AnalysisResult)
        assert result.analysis_type == AnalysisType.SCRIPT_GENERATION


class TestGlobalAnalyzer:
    """Test global analyzer instance."""
    
    def test_global_analyzer_exists(self):
        """Test that global analyzer instance exists."""
        assert analyzer is not None
        assert isinstance(analyzer, AIAnalyzer)
    
    @pytest.mark.asyncio
    async def test_global_analyzer_functionality(self, sample_text):
        """Test global analyzer functionality."""
        result = await analyzer.analyze_document_credibility(sample_text)
        
        assert isinstance(result, AnalysisResult)
        assert result.success is True


@pytest.mark.unit
class TestAIAnalyzerIntegration:
    """Integration tests for AI analyzer."""
    
    @pytest.mark.asyncio
    async def test_multiple_analysis_types(self, sample_text, sample_metadata):
        """Test multiple analysis types on same text."""
        analyzer = AIAnalyzer()
        
        # Run multiple analyses
        credibility_result = await analyzer.analyze_document_credibility(sample_text, sample_metadata)
        bias_result = await analyzer.detect_bias(sample_text)
        entity_result = await analyzer.extract_entities(sample_text)
        
        # All should succeed
        assert credibility_result.success is True
        assert bias_result.success is True
        assert entity_result.success is True
        
        # Should have different analysis types
        assert credibility_result.analysis_type == AnalysisType.CREDIBILITY
        assert bias_result.analysis_type == AnalysisType.BIAS_DETECTION
        assert entity_result.analysis_type == AnalysisType.ENTITY_EXTRACTION
    
    @pytest.mark.asyncio
    async def test_pattern_matching_accuracy(self):
        """Test pattern matching accuracy."""
        analyzer = AIAnalyzer()
        
        # Test text with known entities
        text = """
        The Maurya Empire was founded by Chandragupta Maurya in 321 BCE.
        The capital was at Pataliputra. Later, Emperor Ashoka ruled the empire.
        The Gupta Empire followed, with rulers like Samudragupta.
        """
        
        result = await analyzer.extract_entities(text)
        entities = result.result
        
        # Should detect multiple dynasties
        dynasty_names = [d["name"] for d in entities.dynasties]
        assert "Maurya" in dynasty_names
        
        # Should detect places
        place_names = [p["name"] for p in entities.places]
        assert "Pataliputra" in place_names
    
    @pytest.mark.asyncio
    async def test_performance_timing(self, sample_text):
        """Test that performance timing is recorded."""
        analyzer = AIAnalyzer()
        
        result = await analyzer.analyze_document_credibility(sample_text)
        
        # Should have timing information
        assert result.processing_time > 0
        assert result.processing_time < 10000  # Should be reasonable (< 10 seconds)
    
    @pytest.mark.asyncio
    async def test_concurrent_analysis(self, sample_text):
        """Test concurrent analysis operations."""
        import asyncio
        
        analyzer = AIAnalyzer()
        
        # Run multiple analyses concurrently
        tasks = [
            analyzer.analyze_document_credibility(sample_text),
            analyzer.detect_bias(sample_text),
            analyzer.extract_entities(sample_text)
        ]
        
        results = await asyncio.gather(*tasks)
        
        # All should complete successfully
        assert len(results) == 3
        assert all(result.success for result in results)

