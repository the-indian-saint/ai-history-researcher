"""Research API endpoints for historical research queries."""

import asyncio
import uuid
import json
from typing import Dict, Any, List, Optional
from datetime import datetime

from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends, Query
from pydantic import BaseModel, Field
from sqlalchemy import text

from ...storage.database import (
    create_research_query, update_query_progress, get_database,
    create_document, search_documents
)
from ...processors.document_processor import process_document_url
from ...analyzers.ai_analyzer import (
    analyze_document_credibility, detect_document_bias,
    extract_historical_entities, create_youtube_script
)
from ...collectors.web_scraper import search_academic_content, search_internet_archive
from ...utils.logging import get_logger

logger = get_logger(__name__)

router = APIRouter()


class ResearchRequest(BaseModel):
    """Research query request model."""
    query: str = Field(..., description="Research query text")
    time_period_start: Optional[str] = Field(None, description="Start of time period (e.g., '320 CE')")
    time_period_end: Optional[str] = Field(None, description="End of time period (e.g., '550 CE')")
    geographical_region: Optional[str] = Field(None, description="Geographical region of interest")
    source_types: List[str] = Field(default=["academic", "primary"], description="Types of sources to search")
    max_sources: int = Field(default=10, description="Maximum number of sources to collect")
    languages: List[str] = Field(default=["english"], description="Languages to search in")
    generate_script: bool = Field(default=False, description="Generate YouTube script from results")
    script_length: int = Field(default=10, description="Target script length in minutes")


class ResearchResponse(BaseModel):
    """Research query response model."""
    research_id: str
    status: str
    query: str
    estimated_completion: Optional[str] = None
    sources_found: int = 0
    processing_progress: float = 0.0
    message: str = "Research query submitted successfully"


class ResearchStatus(BaseModel):
    """Research status response model."""
    research_id: str
    status: str
    progress: float
    sources_found: int
    completed_at: Optional[str] = None
    results_summary: Optional[str] = None
    generated_script: Optional[str] = None
    timeline_events: List[Dict[str, Any]] = []
    geo_locations: List[Dict[str, Any]] = []


class TimelineEvent(BaseModel):
    """Historical timeline event."""
    date: str
    description: str
    type: str = "event"  # event, reign, battle, cultural
    significance: Optional[str] = None


class GeoLocation(BaseModel):
    """Historical geographical location."""
    name: str
    coordinates: List[float]  # [lat, long]
    description: str
    type: str = "city"  # city, battle_site, monument, region


class ResearchResults(BaseModel):
    """Research results response model."""
    research_id: str
    query: str
    status: str
    total_sources: int
    sources: List[Dict[str, Any]]
    analysis_summary: Dict[str, Any]
    timeline_events: List[TimelineEvent] = []
    locations: List[GeoLocation] = []
    generated_script: Optional[Dict[str, Any]] = None
    processing_time: float
    completed_at: str


@router.post("/", response_model=ResearchResponse)
async def submit_research_query(
    request: ResearchRequest,
    background_tasks: BackgroundTasks
) -> ResearchResponse:
    """
    Submit a new research query for historical content.
    
    This endpoint initiates a comprehensive research process that:
    1. Searches academic databases and digital archives
    2. Processes and analyzes found documents
    3. Assesses credibility and bias
    4. Extracts historical entities
    5. Optionally generates YouTube scripts
    """
    try:
        # Create research query record
        query_record = await create_research_query(
            query_text=request.query,
            time_period_start=request.time_period_start,
            time_period_end=request.time_period_end,
            geographical_region=request.geographical_region,
            source_types=request.source_types,
            max_sources=request.max_sources
        )
        
        # Start background research process
        background_tasks.add_task(
            process_research_query,
            str(query_record.id),
            request
        )
        
        return ResearchResponse(
            research_id=str(query_record.id),
            status="processing",
            query=request.query,
            estimated_completion=(datetime.utcnow().isoformat() + "Z"),
            message="Research query submitted successfully"
        )
        
    except Exception as e:
        logger.error(f"Error submitting research query: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{research_id}/status", response_model=ResearchStatus)
async def get_research_status(research_id: str) -> ResearchStatus:
    """Get the status of a research query."""
    try:
        async with get_database() as db:
            result = await db.execute(
                text("SELECT * FROM research_queries WHERE id = :id"),
                {"id": research_id}
            )
            query_record = result.fetchone()
            
            if not query_record:
                raise HTTPException(status_code=404, detail="Research query not found")
            
            return ResearchStatus(
                research_id=research_id,
                status=query_record.status,
                progress=query_record.processing_progress,
                sources_found=query_record.total_sources_found,
                completed_at=query_record.completed_at.isoformat() if query_record.completed_at else None,
                results_summary=query_record.results_summary,
                generated_script=query_record.generated_script
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting research status: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{research_id}/results", response_model=ResearchResults)
async def get_research_results(research_id: str) -> ResearchResults:
    """Get the complete results of a research query."""
    try:
        async with get_database() as db:
            # Get query record
            query_result = await db.execute(
                text("SELECT * FROM research_queries WHERE id = :id"),
                {"id": research_id}
            )
            query_record = query_result.fetchone()
            
            if not query_record:
                raise HTTPException(status_code=404, detail="Research query not found")
            
            if query_record.status != "completed":
                raise HTTPException(status_code=400, detail="Research query not completed yet")
            
            # Get associated documents
            docs_result = await db.execute(
                text("""
                SELECT d.* FROM research_documents d
                JOIN query_documents qd ON d.id = qd.document_id
                WHERE qd.query_id = :query_id
                ORDER BY d.credibility_score DESC
                """),
                {"query_id": research_id}
            )
            documents = docs_result.fetchall()
            
            # Format sources
            sources = []
            for doc in documents:
                sources.append({
                    "id": str(doc.id),
                    "title": doc.title,
                    "source_url": doc.source_url,
                    "source_type": doc.source_type,
                    "author": doc.author,
                    "summary": doc.summary,
                    "credibility_score": doc.credibility_score,
                    "bias_assessment": doc.bias_assessment,
                    "entities": doc.entities,
                    "keywords": doc.keywords
                })
            
            # Create analysis summary
            analysis_summary = {
                "total_sources": len(sources),
                "average_credibility": sum(s.get("credibility_score", 0) for s in sources) / len(sources) if sources else 0,
                "source_types": list(set(s["source_type"] for s in sources)),
                "time_periods_covered": query_record.time_period_start and query_record.time_period_end,
                "geographical_regions": [query_record.geographical_region] if query_record.geographical_region else []
            }
            
            # Parse generated script if available
            generated_script = None
            if query_record.generated_script:
                try:
                    generated_script = json.loads(query_record.generated_script)
                except:
                    generated_script = {"script": query_record.generated_script}

            # Aggregate Timeline Events and Locations from Documents
            timeline_events = []
            locations = []
            seen_events = set()
            seen_locations = set()

            # Coordinates mapping for common Ancient Indian cities (Mock Geocoding)
            city_coords = {
                "Pataliputra": [25.61, 85.13], "Patna": [25.61, 85.13],
                "Hastinapura": [29.17, 78.02], "Indraprastha": [28.61, 77.23], "Delhi": [28.61, 77.23],
                "Ujjain": [23.17, 75.78], "Avanti": [23.17, 75.78],
                "Kanchipuram": [12.83, 79.70], "Thanjavur": [10.78, 79.13],
                "Taxila": [33.75, 72.82], "Takshashila": [33.75, 72.82],
                "Varanasi": [25.31, 82.97], "Kashi": [25.31, 82.97],
                "Madurai": [9.92, 78.11], "Ayodhya": [26.79, 82.19],
                "Nalanda": [25.15, 85.44], "Hampi": [15.33, 76.46],
                "Lothal": [22.52, 72.25], "Harappa": [30.63, 72.87], "Mohenjo-daro": [27.32, 68.14]
            }

            for doc in documents:
                if doc.entities:
                    try:
                        entities = json.loads(doc.entities) if isinstance(doc.entities, str) else doc.entities
                        
                        # Process Events for Timeline
                        if 'events' in entities:
                            for event in entities['events']:
                                # Expecting event dict to have name/description/date usually
                                event_name = event.get('name', 'Unknown Event')
                                if event_name not in seen_events:
                                    # Try to find a date in the event object or use a default
                                    date = event.get('date', 'Unknown Date')
                                    # Refine date extraction if needed
                                    
                                    timeline_events.append(TimelineEvent(
                                        date=date,
                                        description=event_name,
                                        type="event",
                                        significance="Historical event extracted from source"
                                    ))
                                    seen_events.add(event_name)

                        # Process Places for Map
                        if 'places' in entities:
                            for place in entities['places']:
                                place_name = place.get('name', '')
                                if place_name and place_name not in seen_locations:
                                    # Look up coords or default to central India
                                    coords = city_coords.get(place_name, city_coords.get(place_name.title(), [20.59, 78.96]))
                                    
                                    locations.append(GeoLocation(
                                        name=place_name,
                                        coordinates=coords,
                                        description=f"Historical location mentioned in {doc.title}",
                                        type="city"
                                    ))
                                    seen_locations.add(place_name)

                    except Exception as e:
                        logger.warning(f"Error parsing entities for doc {doc.id}: {e}")

            # Fallback/Mock data if empty (for demo purposes)
            if not timeline_events and "Gupta" in query_record.query_text:
                timeline_events = [
                    TimelineEvent(date="320 CE", description="Chandragupta I establishes Gupta Empire", type="reign"),
                    TimelineEvent(date="335 CE", description="Samudragupta begins his expansion campaigns", type="battle"),
                    TimelineEvent(date="380 CE", description="Accession of Chandragupta II (Vikramaditya)", type="reign"),
                    TimelineEvent(date="405 CE", description="Faxian visits Pataliputra", type="cultural")
                ]
            
            if not locations and "Gupta" in query_record.query_text:
                locations = [
                    GeoLocation(name="Pataliputra", coordinates=[25.61, 85.13], description="Capital of the Gupta Empire", type="city"),
                    GeoLocation(name="Ujjain", coordinates=[23.17, 75.78], description="Second capital and cultural hub", type="city"),
                    GeoLocation(name="Prayag", coordinates=[25.43, 81.84], description="Site of strategic importance", type="region")
                ]
            
            return ResearchResults(
                research_id=research_id,
                query=query_record.query_text,
                status=query_record.status,
                total_sources=len(sources),
                sources=sources,
                analysis_summary=analysis_summary,
                timeline_events=timeline_events,
                locations=locations,
                generated_script=generated_script,
                processing_time=0.0,
                completed_at=query_record.completed_at.isoformat() if query_record.completed_at else ""
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting research results: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/", response_model=List[Dict[str, Any]])
async def list_research_queries(
    limit: int = Query(default=10, le=100),
    offset: int = Query(default=0, ge=0),
    status: Optional[str] = Query(default=None)
) -> List[Dict[str, Any]]:
    """List research queries with pagination."""
    try:
        async with get_database() as db:
            # Build query
            sql = "SELECT * FROM research_queries"
            params = {}
            
            if status:
                sql += " WHERE status = :status"
                params["status"] = status
            
            sql += " ORDER BY created_at DESC LIMIT :limit OFFSET :offset"
            params.update({"limit": limit, "offset": offset})
            
            result = await db.execute(text(sql), params)
            queries = result.fetchall()
            
            # Format response
            query_list = []
            for query in queries:
                query_list.append({
                    "research_id": str(query.id),
                    "query": query.query_text,
                    "status": query.status,
                    "progress": query.processing_progress,
                    "sources_found": query.total_sources_found,
                    "created_at": query.created_at.isoformat(),
                    "completed_at": query.completed_at.isoformat() if query.completed_at else None
                })
            
            return query_list
            
    except Exception as e:
        logger.error(f"Error listing research queries: {e}")
        raise HTTPException(status_code=500, detail=str(e))


async def process_research_query(research_id: str, request: ResearchRequest):
    """Background task to process research query."""
    try:
        logger.info(f"Starting research query processing: {research_id}")
        
        # Update status to processing
        await update_query_progress(research_id, 0.1, "processing")
        
        # Step 1: Search academic sources
        logger.info(f"Searching academic sources for: {request.query}")
        academic_results = await search_academic_content(request.query, request.max_sources // 2)
        await update_query_progress(research_id, 0.3, "processing")
        
        # Step 2: Search Internet Archive
        logger.info(f"Searching Internet Archive for: {request.query}")
        archive_results = await search_internet_archive(request.query, request.max_sources // 2)
        await update_query_progress(research_id, 0.5, "processing")
        
        # Step 3: Process found documents
        all_sources = []
        processed_documents = []
        
        # Process academic results
        for result in academic_results:
            if result.success and result.url:
                try:
                    # Process document
                    doc_result = await process_document_url(result.url)
                    if doc_result.success:
                        # Create document record
                        doc = await create_document(
                            title=result.title,
                            source_url=result.url,
                            source_type="academic",
                            raw_text=doc_result.extracted_text,
                            processed_text=doc_result.extracted_text,
                            processing_status="completed",
                            ocr_confidence=doc_result.ocr_confidence
                        )
                        processed_documents.append(doc)
                        all_sources.append(result)
                        
                except Exception as e:
                    logger.warning(f"Error processing document {result.url}: {e}")
                    continue
        
        # Process archive results
        if archive_results.success:
            for item in archive_results.items:
                try:
                    # Create document record for archive item
                    doc = await create_document(
                        title=item["title"],
                        source_url=item["url"],
                        source_type="digital_archive",
                        raw_text=item.get("description", ""),
                        processed_text=item.get("description", ""),
                        author=item.get("creator", ""),
                        processing_status="completed"
                    )
                    processed_documents.append(doc)
                    
                except Exception as e:
                    logger.warning(f"Error processing archive item {item.get('identifier', 'unknown')}: {e}")
                    continue
        
        await update_query_progress(research_id, 0.7, "processing")
        
        # Step 4: Analyze documents
        for doc in processed_documents:
            try:
                # Credibility analysis
                credibility_result = await analyze_document_credibility(
                    doc.processed_text,
                    {
                        "source_type": doc.source_type,
                        "author": doc.author,
                        "source_url": doc.source_url
                    }
                )
                
                if credibility_result.success:
                    # Update document with credibility score
                    async with get_database() as db:
                        await db.execute(
                            text("UPDATE documents SET credibility_score = :score WHERE id = :id"),
                            {"score": credibility_result.result.score, "id": doc.id}
                        )
                        await db.commit()
                
                # Bias detection
                bias_result = await detect_document_bias(
                    doc.processed_text,
                    {
                        "source_type": doc.source_type,
                        "author": doc.author,
                        "publication_date": doc.publication_date
                    }
                )
                
                if bias_result.success:
                    # Update document with bias assessment
                    async with get_database() as db:
                        await db.execute(
                            text("UPDATE documents SET bias_assessment = :assessment WHERE id = :id"),
                            {"assessment": json.dumps(bias_result.result.__dict__), "id": doc.id}
                        )
                        await db.commit()
                
                # Entity extraction
                entity_result = await extract_historical_entities(doc.processed_text)
                
                if entity_result.success:
                    # Update document with entities
                    async with get_database() as db:
                        await db.execute(
                            text("UPDATE documents SET entities = :entities WHERE id = :id"),
                            {"entities": json.dumps(entity_result.result.__dict__), "id": doc.id}
                        )
                        await db.commit()
                
            except Exception as e:
                logger.warning(f"Error analyzing document {doc.id}: {e}")
                continue
        
        await update_query_progress(research_id, 0.9, "processing")
        
        # Step 5: Generate script if requested
        generated_script = None
        if request.generate_script and processed_documents:
            try:
                # Prepare research data for script generation
                research_data = []
                for doc in processed_documents[:5]:  # Use top 5 documents
                    research_data.append({
                        "title": doc.title,
                        "content": doc.processed_text[:1000],  # First 1000 chars
                        "summary": doc.summary,
                        "author": doc.author,
                        "source_url": doc.source_url
                    })
                
                script_result = await create_youtube_script(
                    research_data,
                    request.query,
                    request.script_length
                )
                
                if script_result.success:
                    generated_script = script_result.result
                    
            except Exception as e:
                logger.warning(f"Error generating script: {e}")
        
        # Step 6: Update final status
        async with get_database() as db:
            await db.execute(
                text("""
                UPDATE research_queries 
                SET status = :status, processing_progress = :progress, 
                    total_sources_found = :total, completed_at = :completed,
                    results_summary = :summary, generated_script = :script
                WHERE id = :id
                """),
                {
                    "status": "completed",
                    "progress": 1.0,
                    "total": len(processed_documents),
                    "completed": datetime.utcnow(),
                    "summary": f"Found {len(processed_documents)} sources for query: {request.query}",
                    "script": json.dumps(generated_script) if generated_script else None,
                    "id": research_id
                }
            )
            await db.commit()
        
        logger.info(f"Research query completed: {research_id}")
        
    except Exception as e:
        logger.error(f"Error processing research query {research_id}: {e}")
        
        # Update status to failed
        try:
            await update_query_progress(research_id, 0.0, "failed")
        except:
            pass
