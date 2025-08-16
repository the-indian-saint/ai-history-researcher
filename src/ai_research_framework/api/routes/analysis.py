"""Analysis API routes for document and content analysis."""

from typing import List, Dict, Any, Optional
from datetime import datetime

from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel, Field
from sqlalchemy import text

from ...storage.database import get_database
from ...analyzers.ai_analyzer import (
    analyze_document_credibility,
    detect_document_bias,
    extract_historical_entities,
    create_youtube_script
)
from ...utils.logging import get_logger

logger = get_logger(__name__)
router = APIRouter()


class AnalysisRequest(BaseModel):
    """Analysis request model."""
    document_id: str = Field(..., description="Document ID to analyze")
    analysis_types: List[str] = Field(
        default=["credibility", "bias", "entities"],
        description="Types of analysis to perform"
    )
    options: Dict[str, Any] = Field(default={}, description="Analysis options")


class CredibilityAnalysis(BaseModel):
    """Credibility analysis result."""
    score: float
    level: str
    factors: Dict[str, float]
    reasoning: str
    confidence: float


class BiasAnalysis(BaseModel):
    """Bias analysis result."""
    bias_types: List[str]
    bias_scores: Dict[str, float]
    overall_bias_score: float
    reasoning: str
    confidence: float


class EntityAnalysis(BaseModel):
    """Entity extraction result."""
    people: List[Dict[str, Any]]
    places: List[Dict[str, Any]]
    dynasties: List[Dict[str, Any]]
    dates: List[Dict[str, Any]]
    events: List[Dict[str, Any]]
    concepts: List[Dict[str, Any]]
    confidence: float


class ScriptGenerationRequest(BaseModel):
    """YouTube script generation request."""
    document_ids: List[str] = Field(..., description="Document IDs to use for script")
    target_duration: int = Field(default=10, description="Target duration in minutes")
    style: str = Field(default="educational", description="Script style")
    audience: str = Field(default="general", description="Target audience")
    include_citations: bool = Field(default=True, description="Include source citations")


class AnalysisResponse(BaseModel):
    """Analysis response model."""
    document_id: str
    analyses: Dict[str, Any]
    processing_time_ms: float
    timestamp: datetime


@router.post("/analyze", response_model=AnalysisResponse)
async def analyze_document(
    request: AnalysisRequest,
    background_tasks: BackgroundTasks
):
    """Perform various analyses on a document."""
    start_time = datetime.utcnow()
    
    try:
        # Get document
        async with get_database() as db:
            result = await db.execute(
                text("SELECT * FROM research_documents WHERE id = :id"),
                {"id": request.document_id}
            )
            document = result.fetchone()
            
            if not document:
                raise HTTPException(
                    status_code=404,
                    detail="Document not found"
                )
        
        analyses = {}
        
        # Perform requested analyses
        if "credibility" in request.analysis_types:
            try:
                credibility_result = await analyze_document_credibility(
                    content=document.content or document.content_summary,
                    metadata={
                        "title": document.title,
                        "source": document.source_url,
                        "author": document.author
                    }
                )
                analyses["credibility"] = CredibilityAnalysis(
                    score=credibility_result.score,
                    level=credibility_result.level.value,
                    factors=credibility_result.factors,
                    reasoning=credibility_result.reasoning,
                    confidence=credibility_result.confidence
                ).dict()
                
                # Update document credibility score
                background_tasks.add_task(
                    update_document_credibility,
                    request.document_id,
                    credibility_result.score
                )
                
            except Exception as e:
                logger.error(f"Credibility analysis failed: {e}")
                analyses["credibility"] = {"error": str(e)}
        
        if "bias" in request.analysis_types:
            try:
                bias_result = await detect_document_bias(
                    content=document.content or document.content_summary,
                    metadata={
                        "title": document.title,
                        "source": document.source_url,
                        "author": document.author
                    }
                )
                analyses["bias"] = BiasAnalysis(
                    bias_types=[bt.value for bt in bias_result.bias_types],
                    bias_scores=bias_result.bias_scores,
                    overall_bias_score=bias_result.overall_bias_score,
                    reasoning=bias_result.reasoning,
                    confidence=bias_result.confidence
                ).dict()
                
                # Store bias assessment
                background_tasks.add_task(
                    store_bias_assessment,
                    request.document_id,
                    analyses["bias"]
                )
                
            except Exception as e:
                logger.error(f"Bias analysis failed: {e}")
                analyses["bias"] = {"error": str(e)}
        
        if "entities" in request.analysis_types:
            try:
                entities_result = await extract_historical_entities(
                    content=document.content or document.content_summary,
                    options=request.options.get("entity_options", {})
                )
                analyses["entities"] = EntityAnalysis(
                    people=entities_result.people,
                    places=entities_result.places,
                    dynasties=entities_result.dynasties,
                    dates=entities_result.dates,
                    events=entities_result.events,
                    concepts=entities_result.concepts,
                    confidence=entities_result.confidence
                ).dict()
                
                # Store extracted entities
                background_tasks.add_task(
                    store_extracted_entities,
                    request.document_id,
                    analyses["entities"]
                )
                
            except Exception as e:
                logger.error(f"Entity extraction failed: {e}")
                analyses["entities"] = {"error": str(e)}
        
        # Calculate processing time
        processing_time_ms = (datetime.utcnow() - start_time).total_seconds() * 1000
        
        logger.info(f"Document analysis completed: {request.document_id} in {processing_time_ms:.2f}ms")
        
        return AnalysisResponse(
            document_id=request.document_id,
            analyses=analyses,
            processing_time_ms=processing_time_ms,
            timestamp=datetime.utcnow()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Analysis error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/generate-script")
async def generate_youtube_script(request: ScriptGenerationRequest):
    """Generate a YouTube script from documents."""
    try:
        # Get documents
        documents = []
        async with get_database() as db:
            for doc_id in request.document_ids:
                result = await db.execute(
                    text("SELECT * FROM research_documents WHERE id = :id"),
                    {"id": doc_id}
                )
                doc = result.fetchone()
                if doc:
                    documents.append(doc)
        
        if not documents:
            raise HTTPException(
                status_code=404,
                detail="No valid documents found"
            )
        
        # Combine document content
        combined_content = "\n\n".join([
            f"Title: {doc.title}\nContent: {doc.content or doc.content_summary}"
            for doc in documents
        ])
        
        # Generate script
        script_result = await create_youtube_script(
            content=combined_content,
            target_duration=request.target_duration,
            style=request.style,
            audience=request.audience
        )
        
        # Format response
        response = {
            "script": script_result.script,
            "structure": script_result.structure,
            "key_points": script_result.key_points,
            "estimated_duration": script_result.estimated_duration,
            "target_audience": script_result.target_audience
        }
        
        if request.include_citations:
            response["citations"] = [
                {
                    "document_id": str(doc.id),
                    "title": doc.title,
                    "author": doc.author,
                    "source_url": doc.source_url
                }
                for doc in documents
            ]
        
        logger.info(f"YouTube script generated for {len(documents)} documents")
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Script generation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/history/{document_id}")
async def get_analysis_history(document_id: str):
    """Get analysis history for a document."""
    try:
        async with get_database() as db:
            result = await db.execute(
                text("""
                    SELECT * FROM document_analyses
                    WHERE document_id = :document_id
                    ORDER BY created_at DESC
                    LIMIT 10
                """),
                {"document_id": document_id}
            )
            analyses = result.fetchall()
            
            if not analyses:
                return {"document_id": document_id, "analyses": []}
            
            # Format analysis history
            history = [
                {
                    "id": str(analysis.id),
                    "analysis_type": analysis.analysis_type,
                    "result": analysis.result,
                    "confidence": analysis.confidence,
                    "created_at": analysis.created_at.isoformat()
                }
                for analysis in analyses
            ]
            
            return {
                "document_id": document_id,
                "analyses": history,
                "total": len(history)
            }
            
    except Exception as e:
        logger.error(f"Error getting analysis history: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Helper functions for background tasks
async def update_document_credibility(document_id: str, score: float):
    """Update document credibility score."""
    try:
        async with get_database() as db:
            await db.execute(
                text("""
                    UPDATE research_documents
                    SET credibility_score = :score,
                        updated_at = :updated_at
                    WHERE id = :id
                """),
                {
                    "id": document_id,
                    "score": score,
                    "updated_at": datetime.utcnow()
                }
            )
            await db.commit()
    except Exception as e:
        logger.error(f"Failed to update credibility score: {e}")


async def store_bias_assessment(document_id: str, assessment: Dict[str, Any]):
    """Store bias assessment results."""
    try:
        async with get_database() as db:
            await db.execute(
                text("""
                    UPDATE research_documents
                    SET bias_assessment = :assessment,
                        updated_at = :updated_at
                    WHERE id = :id
                """),
                {
                    "id": document_id,
                    "assessment": assessment,
                    "updated_at": datetime.utcnow()
                }
            )
            await db.commit()
    except Exception as e:
        logger.error(f"Failed to store bias assessment: {e}")


async def store_extracted_entities(document_id: str, entities: Dict[str, Any]):
    """Store extracted entities."""
    try:
        async with get_database() as db:
            await db.execute(
                text("""
                    UPDATE research_documents
                    SET entities = :entities,
                        updated_at = :updated_at
                    WHERE id = :id
                """),
                {
                    "id": document_id,
                    "entities": entities,
                    "updated_at": datetime.utcnow()
                }
            )
            await db.commit()
    except Exception as e:
        logger.error(f"Failed to store entities: {e}")
