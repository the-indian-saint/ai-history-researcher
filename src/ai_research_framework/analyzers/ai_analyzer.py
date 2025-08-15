"""Advanced AI analysis engine with LLM integration for historical research."""

import asyncio
import json
import time
from typing import Dict, Any, List, Optional, Union, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import re
from datetime import datetime

from loguru import logger
from ..config import settings
from ..utils.logging import LoggerMixin, LogContext


class AnalysisType(str, Enum):
    """Types of AI analysis available."""
    CREDIBILITY = "credibility"
    BIAS_DETECTION = "bias_detection"
    ENTITY_EXTRACTION = "entity_extraction"
    HISTORICAL_CONTEXT = "historical_context"
    FACT_CHECKING = "fact_checking"
    SCRIPT_GENERATION = "script_generation"
    SUMMARY = "summary"
    TRANSLATION = "translation"
    SENTIMENT = "sentiment"


class CredibilityLevel(str, Enum):
    """Credibility assessment levels."""
    VERY_HIGH = "very_high"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    VERY_LOW = "very_low"
    UNKNOWN = "unknown"


class BiasType(str, Enum):
    """Types of bias that can be detected."""
    COLONIAL = "colonial"
    RELIGIOUS = "religious"
    POLITICAL = "political"
    CULTURAL = "cultural"
    TEMPORAL = "temporal"
    GENDER = "gender"
    REGIONAL = "regional"
    NONE = "none"


@dataclass
class CredibilityResult:
    """Result of credibility analysis."""
    score: float  # 0.0 to 1.0
    level: CredibilityLevel
    factors: Dict[str, float]
    reasoning: str
    confidence: float


@dataclass
class BiasResult:
    """Result of bias detection analysis."""
    bias_types: List[BiasType]
    bias_scores: Dict[str, float]
    overall_bias_score: float
    reasoning: str
    confidence: float


@dataclass
class EntityResult:
    """Result of entity extraction."""
    people: List[Dict[str, Any]]
    places: List[Dict[str, Any]]
    dynasties: List[Dict[str, Any]]
    dates: List[Dict[str, Any]]
    events: List[Dict[str, Any]]
    concepts: List[Dict[str, Any]]
    confidence: float


@dataclass
class ScriptResult:
    """Result of YouTube script generation."""
    script: str
    structure: Dict[str, Any]
    key_points: List[str]
    sources_cited: List[str]
    estimated_duration: int  # in minutes
    target_audience: str


@dataclass
class AnalysisResult:
    """Generic analysis result container."""
    analysis_type: AnalysisType
    success: bool
    result: Union[CredibilityResult, BiasResult, EntityResult, ScriptResult, Dict[str, Any]]
    confidence: float
    processing_time: float
    error_message: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class AIAnalyzer(LoggerMixin):
    """Advanced AI analyzer for historical research."""
    
    def __init__(self):
        self.openai_client = None
        self.anthropic_client = None
        self._initialize_clients()
        
        # Historical knowledge base patterns
        self.dynasty_patterns = {
            'maurya': r'\b(maurya|chandragupta|ashoka|bindusara)\b',
            'gupta': r'\b(gupta|chandragupta ii|samudragupta|kumaragupta)\b',
            'chola': r'\b(chola|rajaraja|rajendra|kulottunga)\b',
            'mughal': r'\b(mughal|akbar|shah jahan|aurangzeb|babur)\b',
            'maratha': r'\b(maratha|shivaji|peshwa|bajirao)\b',
            'delhi_sultanate': r'\b(delhi sultanate|alauddin khilji|qutb|tughlaq)\b'
        }
        
        self.place_patterns = {
            'pataliputra': r'\b(pataliputra|patna)\b',
            'hastinapura': r'\b(hastinapura|indraprastha)\b',
            'ujjain': r'\b(ujjain|ujjayini|avanti)\b',
            'kanchipuram': r'\b(kanchipuram|kanchi)\b',
            'thanjavur': r'\b(thanjavur|tanjore)\b',
            'delhi': r'\b(delhi|dilli|indraprastha)\b'
        }
    
    def _initialize_clients(self):
        """Initialize AI service clients."""
        try:
            if hasattr(settings, 'openai_api_key') and settings.openai_api_key:
                try:
                    import openai
                    self.openai_client = openai.AsyncOpenAI(
                        api_key=settings.openai_api_key,
                        base_url=getattr(settings, 'openai_api_base', None)
                    )
                    self.log_info("OpenAI client initialized")
                except ImportError:
                    self.log_warning("OpenAI package not available")
            
            if hasattr(settings, 'anthropic_api_key') and settings.anthropic_api_key:
                try:
                    import anthropic
                    self.anthropic_client = anthropic.AsyncAnthropic(
                        api_key=settings.anthropic_api_key
                    )
                    self.log_info("Anthropic client initialized")
                except ImportError:
                    self.log_warning("Anthropic package not available")
        
        except Exception as e:
            self.log_error(f"Error initializing AI clients: {e}")
    
    async def _fallback_analysis(self, text: str, analysis_type: AnalysisType) -> Dict[str, Any]:
        """Fallback analysis when AI services are not available."""
        self.log_info(f"Using fallback analysis for {analysis_type}")
        
        if analysis_type == AnalysisType.CREDIBILITY:
            # Simple heuristic-based credibility assessment
            score = 0.7  # Default medium credibility
            
            # Increase score for academic indicators
            if any(term in text.lower() for term in ['university', 'professor', 'journal', 'research']):
                score += 0.2
            
            # Decrease score for bias indicators
            if any(term in text.lower() for term in ['obviously', 'clearly', 'everyone knows']):
                score -= 0.2
            
            score = max(0.0, min(1.0, score))
            
            return CredibilityResult(
                score=score,
                level=CredibilityLevel.MEDIUM,
                factors={'academic_indicators': 0.2, 'bias_indicators': -0.1},
                reasoning="Heuristic-based assessment using keyword analysis",
                confidence=0.6
            )
        
        elif analysis_type == AnalysisType.ENTITY_EXTRACTION:
            # Simple pattern-based entity extraction
            people = []
            places = []
            dynasties = []
            
            # Extract dynasties
            for dynasty, pattern in self.dynasty_patterns.items():
                matches = re.findall(pattern, text, re.IGNORECASE)
                if matches:
                    dynasties.append({
                        'name': dynasty.replace('_', ' ').title(),
                        'mentions': len(matches),
                        'confidence': 0.8
                    })
            
            # Extract places
            for place, pattern in self.place_patterns.items():
                matches = re.findall(pattern, text, re.IGNORECASE)
                if matches:
                    places.append({
                        'name': place.replace('_', ' ').title(),
                        'mentions': len(matches),
                        'confidence': 0.8
                    })
            
            return EntityResult(
                people=people,
                places=places,
                dynasties=dynasties,
                dates=[],
                events=[],
                concepts=[],
                confidence=0.7
            )
        
        elif analysis_type == AnalysisType.BIAS_DETECTION:
            # Simple bias detection
            bias_types = []
            bias_scores = {}
            
            # Check for colonial bias indicators
            colonial_terms = ['civilized', 'primitive', 'backward', 'savage']
            if any(term in text.lower() for term in colonial_terms):
                bias_types.append(BiasType.COLONIAL)
                bias_scores['colonial'] = 0.7
            
            overall_score = sum(bias_scores.values()) / len(bias_scores) if bias_scores else 0.0
            
            return BiasResult(
                bias_types=bias_types,
                bias_scores=bias_scores,
                overall_bias_score=overall_score,
                reasoning="Pattern-based bias detection using keyword analysis",
                confidence=0.6
            )
        
        elif analysis_type == AnalysisType.SCRIPT_GENERATION:
            return ScriptResult(
                script=f"[YouTube script about the topic would be generated here using AI services]",
                structure={'intro': '0-1min', 'main': '1-8min', 'conclusion': '8-10min'},
                key_points=["Key historical points would be extracted"],
                sources_cited=[],
                estimated_duration=10,
                target_audience="History enthusiasts"
            )
        
        else:
            return {
                'result': f"Fallback analysis for {analysis_type}",
                'confidence': 0.5,
                'method': 'fallback'
            }
    
    async def analyze_document_credibility(
        self, 
        text: str, 
        metadata: Dict[str, Any] = None
    ) -> AnalysisResult:
        """Analyze document credibility using AI."""
        
        start_time = time.time()
        
        with LogContext("credibility_analysis", text_length=len(text)):
            try:
                # Use fallback analysis for now (can be enhanced with actual AI calls)
                result = await self._fallback_analysis(text, AnalysisType.CREDIBILITY)
                
                processing_time = (time.time() - start_time) * 1000
                
                return AnalysisResult(
                    analysis_type=AnalysisType.CREDIBILITY,
                    success=True,
                    result=result,
                    confidence=result.confidence,
                    processing_time=processing_time,
                    metadata={'text_length': len(text), 'source_metadata': metadata}
                )
            
            except Exception as e:
                processing_time = (time.time() - start_time) * 1000
                self.log_error(f"Credibility analysis failed: {e}")
                
                return AnalysisResult(
                    analysis_type=AnalysisType.CREDIBILITY,
                    success=False,
                    result={},
                    confidence=0.0,
                    processing_time=processing_time,
                    error_message=str(e)
                )
    
    async def detect_bias(
        self, 
        text: str, 
        context: Dict[str, Any] = None
    ) -> AnalysisResult:
        """Detect various types of bias in historical text."""
        
        start_time = time.time()
        
        with LogContext("bias_detection", text_length=len(text)):
            try:
                result = await self._fallback_analysis(text, AnalysisType.BIAS_DETECTION)
                
                processing_time = (time.time() - start_time) * 1000
                
                return AnalysisResult(
                    analysis_type=AnalysisType.BIAS_DETECTION,
                    success=True,
                    result=result,
                    confidence=result.confidence,
                    processing_time=processing_time
                )
            
            except Exception as e:
                processing_time = (time.time() - start_time) * 1000
                self.log_error(f"Bias detection failed: {e}")
                
                return AnalysisResult(
                    analysis_type=AnalysisType.BIAS_DETECTION,
                    success=False,
                    result={},
                    confidence=0.0,
                    processing_time=processing_time,
                    error_message=str(e)
                )
    
    async def extract_entities(
        self, 
        text: str, 
        entity_types: List[str] = None
    ) -> AnalysisResult:
        """Extract historical entities from text."""
        
        start_time = time.time()
        entity_types = entity_types or ['people', 'places', 'dynasties', 'dates', 'events']
        
        with LogContext("entity_extraction", text_length=len(text), entity_types=entity_types):
            try:
                result = await self._fallback_analysis(text, AnalysisType.ENTITY_EXTRACTION)
                
                processing_time = (time.time() - start_time) * 1000
                
                return AnalysisResult(
                    analysis_type=AnalysisType.ENTITY_EXTRACTION,
                    success=True,
                    result=result,
                    confidence=result.confidence,
                    processing_time=processing_time
                )
            
            except Exception as e:
                processing_time = (time.time() - start_time) * 1000
                self.log_error(f"Entity extraction failed: {e}")
                
                return AnalysisResult(
                    analysis_type=AnalysisType.ENTITY_EXTRACTION,
                    success=False,
                    result={},
                    confidence=0.0,
                    processing_time=processing_time,
                    error_message=str(e)
                )
    
    async def create_youtube_script(
        self, 
        research_data: List[Dict[str, Any]], 
        topic: str,
        target_length: int = 10,  # minutes
        style: str = "educational"
    ) -> AnalysisResult:
        """Generate YouTube script from research data."""
        
        start_time = time.time()
        
        with LogContext("script_generation", topic=topic, target_length=target_length):
            try:
                # Enhanced script generation with research data
                script_content = f"""# YouTube Script: {topic}

## Hook (0:00 - 0:30)
Welcome back to our channel! Today, we're diving deep into {topic}, one of the most fascinating aspects of ancient Indian history that often gets overlooked. Stay tuned because what you're about to learn might completely change how you view this period!

## Introduction (0:30 - 1:30)
[Show map/timeline graphic]
Before we begin, make sure to hit that subscribe button and ring the notification bell for more incredible historical content!

{topic} represents a crucial period in Indian history, and today we'll explore:
"""
                
                # Add key points from research data
                key_points = []
                sources_cited = []
                
                for i, data in enumerate(research_data[:5], 1):
                    title = data.get('title', f'Research Point {i}')
                    content = data.get('content', '')[:300]
                    source_url = data.get('source_url', '')
                    
                    key_points.append(title)
                    if source_url:
                        sources_cited.append(source_url)
                    
                    script_content += f"""
## Main Point {i}: {title} ({i+1}:30 - {i+2}:30)
[Visual: Historical artwork/map]
{content}...

This shows us how {topic} influenced the broader historical narrative of ancient India.
"""
                
                script_content += f"""
## Historical Significance ({len(research_data)+2}:30 - {target_length-2}:00)
[Show timeline with key events]
The importance of {topic} cannot be overstated. It represents a turning point that shaped:
- Political structures of the time
- Cultural and religious practices
- Economic systems
- Social hierarchies

## Conclusion ({target_length-2}:00 - {target_length-1}:00)
As we've seen today, {topic} offers us incredible insights into ancient Indian civilization. The evidence we've examined shows just how sophisticated and complex these historical periods were.

## Call to Action ({target_length-1}:00 - {target_length}:00)
What aspect of {topic} fascinated you the most? Let me know in the comments below! 

If you enjoyed this deep dive into ancient Indian history, please give this video a thumbs up and subscribe for more content like this. 

Next week, we'll be exploring [related topic], so make sure you don't miss it!

Thanks for watching, and I'll see you in the next video!

---
## Sources and References:
{chr(10).join(f"- {source}" for source in sources_cited[:10])}

## Video Structure:
- Hook: 0:00-0:30
- Introduction: 0:30-1:30
- Main Content: 1:30-{target_length-2}:00
- Conclusion: {target_length-2}:00-{target_length-1}:00
- Call to Action: {target_length-1}:00-{target_length}:00

## Estimated Word Count: ~{len(script_content.split())} words
## Estimated Speaking Time: ~{target_length} minutes
"""
                
                result = ScriptResult(
                    script=script_content,
                    structure={
                        'hook': '0:00-0:30',
                        'introduction': '0:30-1:30',
                        'main_content': f'1:30-{target_length-2}:00',
                        'conclusion': f'{target_length-2}:00-{target_length-1}:00',
                        'call_to_action': f'{target_length-1}:00-{target_length}:00'
                    },
                    key_points=key_points,
                    sources_cited=sources_cited,
                    estimated_duration=target_length,
                    target_audience=f"{style.title()} audience interested in ancient Indian history"
                )
                
                processing_time = (time.time() - start_time) * 1000
                
                return AnalysisResult(
                    analysis_type=AnalysisType.SCRIPT_GENERATION,
                    success=True,
                    result=result,
                    confidence=0.8,
                    processing_time=processing_time,
                    metadata={'research_sources': len(research_data), 'target_length': target_length}
                )
            
            except Exception as e:
                processing_time = (time.time() - start_time) * 1000
                self.log_error(f"Script generation failed: {e}")
                
                return AnalysisResult(
                    analysis_type=AnalysisType.SCRIPT_GENERATION,
                    success=False,
                    result={},
                    confidence=0.0,
                    processing_time=processing_time,
                    error_message=str(e)
                )


# Global analyzer instance
analyzer = AIAnalyzer()


# Convenience functions
async def analyze_document_credibility(text: str, metadata: Dict[str, Any] = None) -> AnalysisResult:
    """Convenience function for credibility analysis."""
    return await analyzer.analyze_document_credibility(text, metadata)


async def detect_document_bias(text: str, context: Dict[str, Any] = None) -> AnalysisResult:
    """Convenience function for bias detection."""
    return await analyzer.detect_bias(text, context)


async def extract_historical_entities(text: str, entity_types: List[str] = None) -> AnalysisResult:
    """Convenience function for entity extraction."""
    return await analyzer.extract_entities(text, entity_types)


async def create_youtube_script(
    research_data: List[Dict[str, Any]], 
    topic: str,
    target_length: int = 10,
    style: str = "educational"
) -> AnalysisResult:
    """Convenience function for YouTube script generation."""
    return await analyzer.create_youtube_script(research_data, topic, target_length, style)

