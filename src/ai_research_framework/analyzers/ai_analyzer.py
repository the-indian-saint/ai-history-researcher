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
    
    async def _call_llm(self, messages: List[Dict[str, str]], **kwargs) -> str:
            """Unified LLM call supporting both Cloud and Local models."""
            try:
                if settings.use_local_model and self.openai_client:
                    # Use local model via OpenAI compatible endpoint
                    self.log_info(f"Using local model: {settings.local_model_name}")
                    response = await self.openai_client.chat.completions.create(
                        model=settings.local_model_name,
                        messages=messages,
                        **kwargs
                    )
                    return response.choices[0].message.content
                
                elif self.anthropic_client:
                    response = await self.anthropic_client.messages.create(
                        model="claude-3-sonnet-20240229",
                        messages=messages,
                        max_tokens=kwargs.get("max_tokens", 1000)
                    )
                    return response.content[0].text
                    
                elif self.openai_client:
                    response = await self.openai_client.chat.completions.create(
                        model="gpt-4-turbo-preview",
                        messages=messages,
                        **kwargs
                    )
                    return response.choices[0].message.content
                    
                else:
                    raise Exception("No AI clients available")
                    
            except Exception as e:
                self.log_error(f"LLM call failed: {e}")
                raise

    def _initialize_clients(self):
        """Initialize AI service clients."""
        try:
            # Initialize OpenAI client (works for both OpenAI and Local Ollama)
            import openai
            
            if settings.use_local_model:
                self.openai_client = openai.AsyncOpenAI(
                    api_key="ollama",  # Not required for Ollama but field is needed
                    base_url=settings.local_model_base_url
                )
                self.log_info(f"Local model client initialized at {settings.local_model_base_url}")
            
            elif hasattr(settings, 'openai_api_key') and settings.openai_api_key:
                self.openai_client = openai.AsyncOpenAI(
                    api_key=settings.openai_api_key,
                    base_url=getattr(settings, 'openai_api_base', None)
                )
                self.log_info("OpenAI client initialized")
            
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
                # Use LLM for analysis if clients are available
                if self.openai_client or self.anthropic_client:
                    prompt = f"""Analyze the credibility of the following historical text. 
                    Consider the source type, probable author intent, and linguistic markers.
                    
                    Metadata: {json.dumps(metadata or {})}
                    
                    Text:
                    {text[:4000]}
                    
                    Return a JSON object with:
                    - score: float (0.0 to 1.0)
                    - level: string (very_high, high, medium, low, very_low)
                    - factors: dict of factor scores
                    - reasoning: string explanation
                    - confidence: float (0.0 to 1.0)
                    """
                    
                    response = await self._call_llm([
                        {"role": "system", "content": "You are an expert historian specializing in source criticism and historiography. Return only valid JSON."},
                        {"role": "user", "content": prompt}
                    ], temperature=0.3, response_format={"type": "json_object"} if settings.use_local_model else None)
                    
                    # Clean response and parse JSON (handle potential markdown fences)
                    clean_json = response.replace("```json", "").replace("```", "").strip()
                    data = json.loads(clean_json)
                    
                    result = CredibilityResult(
                        score=data.get('score', 0.5),
                        level=CredibilityLevel(data.get('level', 'medium').lower()),
                        factors=data.get('factors', {}),
                        reasoning=data.get('reasoning', 'No reasoning provided'),
                        confidence=data.get('confidence', 0.8)
                    )
                else:
                    # Fallback if no LLM configured/available
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
                if self.openai_client or self.anthropic_client:
                    prompt = f"""Analyze the provided text for historical biases (colonial, religious, political, cultural, gender, etc.).
                    
                    Context: {json.dumps(context or {})}
                    
                    Text:
                    {text[:4000]}
                    
                    Return a JSON object with:
                    - bias_types: list of strings (colonial, religious, political, cultural, temporal, gender, regional, none)
                    - bias_scores: dict mapping bias type to score (0.0-1.0)
                    - overall_bias_score: float
                    - reasoning: string explanation
                    - confidence: float
                    """
                    
                    response = await self._call_llm([
                        {"role": "system", "content": "You are an expert historian. Detect bias with nuance. Return only valid JSON."},
                        {"role": "user", "content": prompt}
                    ], temperature=0.3, response_format={"type": "json_object"} if settings.use_local_model else None)
                    
                    clean_json = response.replace("```json", "").replace("```", "").strip()
                    data = json.loads(clean_json)
                    
                    result = BiasResult(
                        bias_types=[BiasType(b.lower()) for b in data.get('bias_types', ['none']) if b.lower() in [e.value for e in BiasType]],
                        bias_scores=data.get('bias_scores', {}),
                        overall_bias_score=data.get('overall_bias_score', 0.0),
                        reasoning=data.get('reasoning', 'No reasoning provided'),
                        confidence=data.get('confidence', 0.8)
                    )
                else:
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
                if self.openai_client or self.anthropic_client:
                    prompt = f"""Extract historical entities from the text.
                    Focus on: {', '.join(entity_types)}
                    
                    Text:
                    {text[:4000]}
                    
                    Return a JSON object with:
                    - people: list of objects (name, role, significance)
                    - places: list of objects (name, modern_location, type)
                    - dynasties: list of objects (name, period, region)
                    - dates: list of objects (date, event)
                    - events: list of objects (name, date, description)
                    - concepts: list of objects (name, definition)
                    - confidence: float
                    """
                    
                    response = await self._call_llm([
                        {"role": "system", "content": "You are an expert historian. Extract structured data. Return only valid JSON."},
                        {"role": "user", "content": prompt}
                    ], temperature=0.1, response_format={"type": "json_object"} if settings.use_local_model else None)
                    
                    clean_json = response.replace("```json", "").replace("```", "").strip()
                    data = json.loads(clean_json)
                    
                    result = EntityResult(
                        people=data.get('people', []),
                        places=data.get('places', []),
                        dynasties=data.get('dynasties', []),
                        dates=data.get('dates', []),
                        events=data.get('events', []),
                        concepts=data.get('concepts', []),
                        confidence=data.get('confidence', 0.8)
                    )
                else:
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
                

                if self.openai_client or self.anthropic_client:
                    # Prepare research context
                    research_summary = "\n\n".join([
                        f"Source: {d.get('title')}\nContent: {d.get('content', '')[:500]}"
                        for d in research_data[:5]
                    ])
                    
                    prompt = f"""Create a YouTube script for a {target_length}-minute video about "{topic}".
                    Style: {style}
                    
                    Research Data:
                    {research_summary}
                    
                    Return a JSON object with:
                    - script: string (full markdown script with sections, timestamps, and visual cues)
                    - structure: dict mapping section to timestamp range
                    - key_points: list of strings
                    - sources_cited: list of strings
                    - estimated_duration: int
                    - target_audience: string
                    """
                    
                    response = await self._call_llm([
                        {"role": "system", "content": "You are a professional scriptwriter for educational history channels. Return only valid JSON."},
                        {"role": "user", "content": prompt}
                    ], temperature=0.7, response_format={"type": "json_object"} if settings.use_local_model else None)
                    
                    clean_json = response.replace("```json", "").replace("```", "").strip()
                    data = json.loads(clean_json)
                    
                    # Ensure mock structure if LLM fails to provide good structure
                    structure = data.get('structure', {
                        'intro': '0:00-1:00',
                        'main': f'1:00-{target_length-1}:00',
                        'outro': f'{target_length-1}:00-{target_length}:00'
                    })
                    
                    result = ScriptResult(
                        script=data.get('script', 'Failed to generate script content.'),
                        structure=structure,
                        key_points=data.get('key_points', []),
                        sources_cited=data.get('sources_cited', []),
                        estimated_duration=data.get('estimated_duration', target_length),
                        target_audience=data.get('target_audience', 'General Audience')
                    )
                else:
                    result = await self._fallback_analysis("", AnalysisType.SCRIPT_GENERATION)
                
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

