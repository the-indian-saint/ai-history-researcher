"""Hybrid search implementation combining full-text and semantic search."""

from typing import List, Optional, Dict, Any, Tuple
from datetime import datetime
import asyncio

from sqlalchemy.ext.asyncio import AsyncSession

from .fulltext_search import FullTextSearch, SearchFacets
from .semantic_search import SemanticSearch
from ..storage.database import Document, get_database
from ..utils.logging import get_logger

logger = get_logger(__name__)


class SearchResultRanker:
    """Rank and combine search results from multiple sources."""
    
    @staticmethod
    def normalize_score(score: float, min_score: float = 0.0, max_score: float = 1.0) -> float:
        """
        Normalize a score to 0-1 range.
        
        Args:
            score: Score to normalize
            min_score: Minimum possible score
            max_score: Maximum possible score
            
        Returns:
            Normalized score between 0 and 1
        """
        if max_score == min_score:
            return 0.5
        
        return (score - min_score) / (max_score - min_score)
    
    @staticmethod
    def reciprocal_rank_fusion(
        result_sets: List[List[Dict[str, Any]]],
        k: int = 60
    ) -> List[Dict[str, Any]]:
        """
        Combine multiple ranked result sets using Reciprocal Rank Fusion.
        
        Args:
            result_sets: List of result sets, each containing ranked results
            k: Constant for RRF algorithm (default 60)
            
        Returns:
            Combined and re-ranked results
        """
        # Calculate RRF scores
        rrf_scores = {}
        
        for result_set in result_sets:
            for rank, result in enumerate(result_set, 1):
                doc_id = result.get("document_id")
                if doc_id:
                    if doc_id not in rrf_scores:
                        rrf_scores[doc_id] = {
                            "score": 0.0,
                            "result": result,
                            "ranks": []
                        }
                    
                    # Add RRF score: 1 / (k + rank)
                    rrf_scores[doc_id]["score"] += 1.0 / (k + rank)
                    rrf_scores[doc_id]["ranks"].append(rank)
        
        # Sort by RRF score
        sorted_results = sorted(
            rrf_scores.values(),
            key=lambda x: x["score"],
            reverse=True
        )
        
        # Format final results
        final_results = []
        for item in sorted_results:
            result = item["result"].copy()
            result["final_score"] = item["score"]
            result["rank_sources"] = item["ranks"]
            final_results.append(result)
        
        return final_results
    
    @staticmethod
    def weighted_fusion(
        result_sets: List[Tuple[List[Dict[str, Any]], float]],
        normalize: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Combine results using weighted score fusion.
        
        Args:
            result_sets: List of (results, weight) tuples
            normalize: Whether to normalize scores before fusion
            
        Returns:
            Combined results with weighted scores
        """
        combined_scores = {}
        
        for results, weight in result_sets:
            # Get min/max scores for normalization
            if normalize and results:
                scores = [r.get("score", 0) for r in results]
                min_score = min(scores)
                max_score = max(scores)
            else:
                min_score = 0
                max_score = 1
            
            for result in results:
                doc_id = result.get("document_id")
                if doc_id:
                    if doc_id not in combined_scores:
                        combined_scores[doc_id] = {
                            "weighted_score": 0.0,
                            "result": result,
                            "component_scores": {}
                        }
                    
                    # Normalize and weight the score
                    score = result.get("score", 0)
                    if normalize:
                        score = SearchResultRanker.normalize_score(score, min_score, max_score)
                    
                    weighted_score = score * weight
                    combined_scores[doc_id]["weighted_score"] += weighted_score
                    combined_scores[doc_id]["component_scores"][f"weight_{weight}"] = weighted_score
        
        # Sort by combined score
        sorted_results = sorted(
            combined_scores.values(),
            key=lambda x: x["weighted_score"],
            reverse=True
        )
        
        # Format final results
        final_results = []
        for item in sorted_results:
            result = item["result"].copy()
            result["final_score"] = item["weighted_score"]
            result["component_scores"] = item["component_scores"]
            final_results.append(result)
        
        return final_results


class HybridSearch:
    """Hybrid search combining full-text and semantic search."""
    
    def __init__(
        self,
        session: Optional[AsyncSession] = None,
        semantic_weight: float = 0.5,
        fulltext_weight: float = 0.5,
        fusion_method: str = "weighted"  # "weighted" or "rrf"
    ):
        """
        Initialize hybrid search.
        
        Args:
            session: Database session for full-text search
            semantic_weight: Weight for semantic search results
            fulltext_weight: Weight for full-text search results
            fusion_method: Method to combine results ("weighted" or "rrf")
        """
        self.session = session
        self.semantic_search = SemanticSearch()
        self.fulltext_search = None
        self.ranker = SearchResultRanker()
        
        # Weights for combining results
        self.semantic_weight = semantic_weight
        self.fulltext_weight = fulltext_weight
        self.fusion_method = fusion_method
        
        # Initialize full-text search if session provided
        if session:
            self.fulltext_search = FullTextSearch(session)
            self.facets = SearchFacets(session)
    
    async def search(
        self,
        query: str,
        limit: int = 10,
        filters: Optional[Dict[str, Any]] = None,
        search_types: List[str] = None,
        include_facets: bool = False
    ) -> Dict[str, Any]:
        """
        Perform hybrid search combining multiple search methods.
        
        Args:
            query: Search query
            limit: Maximum number of results
            filters: Search filters
            search_types: List of search types to use (["semantic", "fulltext"])
            include_facets: Whether to include facets in results
            
        Returns:
            Search results with metadata
        """
        if search_types is None:
            search_types = ["semantic", "fulltext"]
        
        start_time = datetime.utcnow()
        tasks = []
        result_sets = []
        
        try:
            # Perform semantic search if requested
            if "semantic" in search_types:
                semantic_task = self.semantic_search.search(
                    query=query,
                    limit=limit * 2,  # Get more results for better fusion
                    filters=filters
                )
                tasks.append(("semantic", semantic_task))
            
            # Perform full-text search if requested and available
            if "fulltext" in search_types and self.fulltext_search:
                fulltext_task = self.fulltext_search.search(
                    query=query,
                    limit=limit * 2,
                    filters=filters
                )
                tasks.append(("fulltext", fulltext_task))
            
            # Execute searches in parallel
            if tasks:
                search_results = await asyncio.gather(
                    *[task for _, task in tasks],
                    return_exceptions=True
                )
                
                # Process results
                for i, (search_type, _) in enumerate(tasks):
                    if not isinstance(search_results[i], Exception):
                        if search_type == "semantic":
                            # Format semantic results
                            semantic_results = []
                            for r in search_results[i]:
                                semantic_results.append({
                                    "document_id": r.get("document_id"),
                                    "score": r.get("score", 0),
                                    "text": r.get("text", ""),
                                    "metadata": r.get("metadata", {}),
                                    "search_type": "semantic"
                                })
                            result_sets.append((semantic_results, self.semantic_weight))
                        
                        elif search_type == "fulltext":
                            # Format full-text results
                            documents, total = search_results[i]
                            fulltext_results = []
                            for doc in documents:
                                fulltext_results.append({
                                    "document_id": str(doc.id),
                                    "score": doc.rank if hasattr(doc, 'rank') else 0.5,
                                    "title": doc.title,
                                    "headline": doc.headline if hasattr(doc, 'headline') else "",
                                    "metadata": {
                                        "source_type": doc.source_type,
                                        "language": doc.language,
                                        "author": doc.author
                                    },
                                    "search_type": "fulltext"
                                })
                            result_sets.append((fulltext_results, self.fulltext_weight))
                    else:
                        logger.error(f"Search error for {search_type}: {search_results[i]}")
            
            # Combine results using selected fusion method
            if result_sets:
                if self.fusion_method == "rrf":
                    # Use Reciprocal Rank Fusion
                    all_results = []
                    for results, _ in result_sets:
                        all_results.append(results)
                    combined_results = self.ranker.reciprocal_rank_fusion(all_results)
                else:
                    # Use weighted fusion
                    combined_results = self.ranker.weighted_fusion(result_sets)
                
                # Limit to requested number of results
                combined_results = combined_results[:limit]
            else:
                combined_results = []
            
            # Get facets if requested
            facets = {}
            if include_facets and self.facets:
                facets = await self.facets.get_facets(query)
            
            # Calculate search time
            search_time_ms = (datetime.utcnow() - start_time).total_seconds() * 1000
            
            return {
                "query": query,
                "total_results": len(combined_results),
                "results": combined_results,
                "facets": facets,
                "search_time_ms": search_time_ms,
                "search_types": search_types,
                "fusion_method": self.fusion_method
            }
            
        except Exception as e:
            logger.error(f"Hybrid search error: {e}")
            raise
    
    async def explain_search(
        self,
        query: str,
        document_id: str
    ) -> Dict[str, Any]:
        """
        Explain why a document matched a search query.
        
        Args:
            query: Search query
            document_id: Document ID to explain
            
        Returns:
            Explanation of search match
        """
        explanation = {
            "query": query,
            "document_id": document_id,
            "explanations": {}
        }
        
        try:
            # Get semantic search explanation
            semantic_results = await self.semantic_search.search(
                query=query,
                filters={"document_id": document_id},
                limit=5
            )
            
            if semantic_results:
                explanation["explanations"]["semantic"] = {
                    "score": semantic_results[0].get("score", 0),
                    "matched_chunks": len(semantic_results),
                    "top_chunk": semantic_results[0].get("text", "")[:200]
                }
            
            # Get full-text search explanation if available
            if self.fulltext_search:
                results, _ = await self.fulltext_search.search(
                    query=query,
                    filters={"document_id": document_id},
                    limit=1
                )
                
                if results:
                    explanation["explanations"]["fulltext"] = {
                        "rank": results[0].rank if hasattr(results[0], 'rank') else 0,
                        "headline": results[0].headline if hasattr(results[0], 'headline') else ""
                    }
            
            # Analyze query
            if self.fulltext_search:
                query_analysis = await self.fulltext_search.analyze_query(query)
                explanation["query_analysis"] = query_analysis
            
        except Exception as e:
            logger.error(f"Error explaining search: {e}")
            explanation["error"] = str(e)
        
        return explanation
    
    async def get_recommendations(
        self,
        document_id: str,
        limit: int = 5,
        method: str = "hybrid"  # "semantic", "fulltext", or "hybrid"
    ) -> List[Dict[str, Any]]:
        """
        Get document recommendations based on a reference document.
        
        Args:
            document_id: Reference document ID
            limit: Maximum number of recommendations
            method: Recommendation method
            
        Returns:
            List of recommended documents
        """
        try:
            recommendations = []
            
            if method in ["semantic", "hybrid"]:
                # Get semantic similarity recommendations
                similar = await self.semantic_search.find_similar_documents(
                    document_id=document_id,
                    limit=limit * 2 if method == "hybrid" else limit
                )
                
                for doc in similar:
                    doc["recommendation_type"] = "semantic_similarity"
                    recommendations.append(doc)
            
            if method in ["fulltext", "hybrid"] and self.session:
                # Get document for keyword extraction
                async with get_database() as db:
                    result = await db.execute(
                        text("SELECT title, keywords FROM research_documents WHERE id = :id"),
                        {"id": document_id}
                    )
                    doc = result.fetchone()
                    
                    if doc and doc.keywords:
                        # Search using document keywords
                        keyword_query = " ".join(doc.keywords[:5])  # Use top 5 keywords
                        keyword_results, _ = await self.fulltext_search.search(
                            query=keyword_query,
                            limit=limit * 2 if method == "hybrid" else limit
                        )
                        
                        for result in keyword_results:
                            if str(result.id) != document_id:
                                recommendations.append({
                                    "document_id": str(result.id),
                                    "title": result.title,
                                    "score": result.rank if hasattr(result, 'rank') else 0.5,
                                    "recommendation_type": "keyword_match"
                                })
            
            # Combine and deduplicate recommendations
            if method == "hybrid":
                # Use RRF to combine recommendations
                seen = set()
                final_recommendations = []
                
                for rec in recommendations:
                    doc_id = rec["document_id"]
                    if doc_id not in seen:
                        seen.add(doc_id)
                        final_recommendations.append(rec)
                
                recommendations = final_recommendations[:limit]
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Error getting recommendations: {e}")
            return []
