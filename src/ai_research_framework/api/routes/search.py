"""Search API routes for document and research queries."""

from typing import List, Optional, Dict, Any
from datetime import datetime

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy import text

from ...storage.database import get_database, search_documents
from ...storage.vector_storage import get_vector_storage
from ...search.hybrid_search import HybridSearch
from ...search.semantic_search import SemanticSearch
from ...utils.logging import get_logger

logger = get_logger(__name__)
router = APIRouter()


class SearchRequest(BaseModel):
    """Search request model."""
    query: str = Field(..., description="Search query text")
    search_type: str = Field(default="hybrid", description="Search type: 'semantic', 'fulltext', 'hybrid'")
    filters: Dict[str, Any] = Field(default={}, description="Additional filters")
    limit: int = Field(default=10, ge=1, le=100, description="Maximum results to return")
    include_snippets: bool = Field(default=True, description="Include text snippets in results")
    include_facets: bool = Field(default=False, description="Include search facets")
    fusion_method: str = Field(default="weighted", description="Fusion method: 'weighted' or 'rrf'")


class SearchResult(BaseModel):
    """Individual search result."""
    document_id: str
    title: str
    source_url: Optional[str]
    author: Optional[str]
    relevance_score: float
    snippet: Optional[str]
    highlights: List[str]
    metadata: Dict[str, Any]


class SearchResponse(BaseModel):
    """Search response model."""
    query: str
    total_results: int
    results: List[SearchResult]
    search_time_ms: float
    search_type: str


@router.post("/", response_model=SearchResponse)
async def search(request: SearchRequest):
    """Perform hybrid, semantic, or full-text search across documents."""
    start_time = datetime.utcnow()
    
    try:
        results = []
        
        # Use hybrid search for most cases
        if request.search_type == "hybrid":
            async with get_database() as session:
                hybrid_search = HybridSearch(
                    session=session,
                    fusion_method=request.fusion_method
                )
                
                search_results = await hybrid_search.search(
                    query=request.query,
                    limit=request.limit,
                    filters=request.filters,
                    search_types=["semantic", "fulltext"],
                    include_facets=request.include_facets
                )
                
                # Format results for API response
                for result in search_results.get("results", []):
                    results.append(SearchResult(
                        document_id=result.get("document_id"),
                        title=result.get("title", result.get("metadata", {}).get("title", "")),
                        source_url=result.get("metadata", {}).get("source_url"),
                        author=result.get("metadata", {}).get("author"),
                        relevance_score=result.get("final_score", result.get("score", 0)),
                        snippet=result.get("text", result.get("headline", ""))[:500] if request.include_snippets else None,
                        highlights=[],
                        metadata=result.get("metadata", {})
                    ))
        
        elif request.search_type == "semantic":
            # Semantic search using vector embeddings
            try:
                vector_store = await get_vector_storage()
                
                # Perform vector similarity search
                vector_results = await vector_store.similarity_search(
                    query=request.query,
                    k=request.limit,
                    filter=request.filters
                )
                
                # Get document details for each result
                async with get_database() as db:
                    for vr in vector_results:
                        doc_result = await db.execute(
                            text("SELECT * FROM research_documents WHERE id = :id"),
                            {"id": vr["document_id"]}
                        )
                        doc = doc_result.fetchone()
                        
                        if doc:
                            results.append(SearchResult(
                                document_id=str(doc.id),
                                title=doc.title,
                                source_url=doc.source_url,
                                author=doc.author,
                                relevance_score=vr["score"],
                                snippet=vr.get("text", "")[:500] if request.include_snippets else None,
                                highlights=[],
                                metadata={
                                    "source_type": doc.source_type,
                                    "language": doc.language,
                                    "credibility_score": doc.credibility_score
                                }
                            ))
                            
            except Exception as e:
                logger.warning(f"Vector search failed, falling back to keyword search: {e}")
                request.search_type = "keyword"
        
        if request.search_type == "keyword" or not results:
            # Keyword-based search
            search_results = await search_documents(
                query=request.query,
                filters=request.filters,
                limit=request.limit
            )
            
            for doc in search_results:
                # Extract snippets and highlights
                snippet = None
                highlights = []
                
                if request.include_snippets and doc.content:
                    # Find relevant snippet
                    content_lower = doc.content.lower()
                    query_lower = request.query.lower()
                    query_words = query_lower.split()
                    
                    # Find best matching section
                    best_pos = -1
                    for word in query_words:
                        pos = content_lower.find(word)
                        if pos != -1:
                            best_pos = pos
                            break
                    
                    if best_pos != -1:
                        start = max(0, best_pos - 100)
                        end = min(len(doc.content), best_pos + 400)
                        snippet = doc.content[start:end]
                        
                        # Extract highlights
                        for word in query_words:
                            if word in content_lower:
                                highlights.append(word)
                
                results.append(SearchResult(
                    document_id=str(doc.id),
                    title=doc.title,
                    source_url=doc.source_url,
                    author=doc.author,
                    relevance_score=doc.relevance_score if hasattr(doc, 'relevance_score') else 0.5,
                    snippet=snippet,
                    highlights=highlights,
                    metadata={
                        "source_type": doc.source_type,
                        "language": doc.language,
                        "credibility_score": doc.credibility_score,
                        "created_at": doc.created_at.isoformat()
                    }
                ))
        
        # Calculate search time
        search_time_ms = (datetime.utcnow() - start_time).total_seconds() * 1000
        
        logger.info(f"Search completed: '{request.query}' - {len(results)} results in {search_time_ms:.2f}ms")
        
        return SearchResponse(
            query=request.query,
            total_results=len(results),
            results=results,
            search_time_ms=search_time_ms,
            search_type=request.search_type
        )
        
    except Exception as e:
        logger.error(f"Search error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/quick")
async def quick_search(
    q: str = Query(..., description="Search query"),
    limit: int = Query(10, ge=1, le=50, description="Maximum results")
):
    """Quick keyword search endpoint."""
    try:
        # Perform quick keyword search
        results = await search_documents(
            query=q,
            limit=limit
        )
        
        # Format simplified results
        formatted_results = [
            {
                "id": str(doc.id),
                "title": doc.title,
                "url": doc.source_url,
                "summary": doc.content_summary[:200] if doc.content_summary else None,
                "score": doc.credibility_score
            }
            for doc in results
        ]
        
        return {
            "query": q,
            "results": formatted_results,
            "count": len(formatted_results)
        }
        
    except Exception as e:
        logger.error(f"Quick search error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/suggest")
async def search_suggestions(
    q: str = Query(..., description="Partial query for suggestions"),
    limit: int = Query(5, ge=1, le=20, description="Maximum suggestions")
):
    """Get search suggestions based on partial query."""
    try:
        async with get_database() as db:
            # Get suggestions from document titles and keywords
            result = await db.execute(
                text("""
                    SELECT DISTINCT title, keywords
                    FROM research_documents
                    WHERE LOWER(title) LIKE :query
                       OR LOWER(keywords) LIKE :query
                    LIMIT :limit
                """),
                {
                    "query": f"%{q.lower()}%",
                    "limit": limit * 2  # Get more to filter
                }
            )
            
            suggestions = set()
            for row in result:
                # Add title-based suggestions
                if row.title and q.lower() in row.title.lower():
                    suggestions.add(row.title)
                
                # Add keyword-based suggestions
                if row.keywords:
                    for keyword in row.keywords:
                        if q.lower() in keyword.lower():
                            suggestions.add(keyword)
            
            # Limit and sort suggestions
            suggestion_list = sorted(list(suggestions))[:limit]
            
            return {
                "query": q,
                "suggestions": suggestion_list
            }
            
    except Exception as e:
        logger.error(f"Suggestion error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/advanced")
async def advanced_search(
    q: Optional[str] = Query(None, description="Main search query"),
    title: Optional[str] = Query(None, description="Search in title"),
    author: Optional[str] = Query(None, description="Search by author"),
    source_type: Optional[str] = Query(None, description="Filter by source type"),
    language: Optional[str] = Query(None, description="Filter by language"),
    date_from: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    date_to: Optional[str] = Query(None, description="End date (YYYY-MM-DD)"),
    min_credibility: Optional[float] = Query(None, ge=0, le=1, description="Minimum credibility score"),
    limit: int = Query(20, ge=1, le=100, description="Maximum results")
):
    """Advanced search with multiple filters."""
    try:
        async with get_database() as db:
            # Build complex query
            query_parts = ["SELECT * FROM research_documents WHERE 1=1"]
            params = {"limit": limit}
            
            if q:
                query_parts.append("AND (LOWER(content) LIKE :query OR LOWER(content_summary) LIKE :query)")
                params["query"] = f"%{q.lower()}%"
            
            if title:
                query_parts.append("AND LOWER(title) LIKE :title")
                params["title"] = f"%{title.lower()}%"
            
            if author:
                query_parts.append("AND LOWER(author) LIKE :author")
                params["author"] = f"%{author.lower()}%"
            
            if source_type:
                query_parts.append("AND source_type = :source_type")
                params["source_type"] = source_type
            
            if language:
                query_parts.append("AND language = :language")
                params["language"] = language
            
            if date_from:
                query_parts.append("AND created_at >= :date_from")
                params["date_from"] = date_from
            
            if date_to:
                query_parts.append("AND created_at <= :date_to")
                params["date_to"] = date_to
            
            if min_credibility is not None:
                query_parts.append("AND credibility_score >= :min_credibility")
                params["min_credibility"] = min_credibility
            
            query_parts.append("ORDER BY credibility_score DESC, created_at DESC")
            query_parts.append("LIMIT :limit")
            
            # Execute query
            full_query = " ".join(query_parts)
            result = await db.execute(text(full_query), params)
            documents = result.fetchall()
            
            # Format results
            results = [
                {
                    "id": str(doc.id),
                    "title": doc.title,
                    "author": doc.author,
                    "source_url": doc.source_url,
                    "source_type": doc.source_type,
                    "language": doc.language,
                    "credibility_score": doc.credibility_score,
                    "summary": doc.content_summary,
                    "created_at": doc.created_at.isoformat()
                }
                for doc in documents
            ]
            
            return {
                "filters": {
                    "query": q,
                    "title": title,
                    "author": author,
                    "source_type": source_type,
                    "language": language,
                    "date_from": date_from,
                    "date_to": date_to,
                    "min_credibility": min_credibility
                },
                "results": results,
                "count": len(results)
            }
            
    except Exception as e:
        logger.error(f"Advanced search error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
