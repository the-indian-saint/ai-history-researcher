"""Full-text search implementation using PostgreSQL tsvector and tsquery."""

from typing import List, Optional, Dict, Any, Tuple
from datetime import datetime
import re

from sqlalchemy import text, func, Column, Index
from sqlalchemy.dialects.postgresql import TSVECTOR
from sqlalchemy.ext.asyncio import AsyncSession

from ..storage.database import Document, Base
from ..utils.logging import get_logger

logger = get_logger(__name__)


class FullTextSearchMixin:
    """Mixin to add full-text search capabilities to SQLAlchemy models."""
    
    # Add tsvector column for full-text search
    search_vector = Column(TSVECTOR)
    
    @classmethod
    def create_search_indexes(cls, table_name: str):
        """Create GIN indexes for full-text search."""
        return [
            Index(f'idx_{table_name}_search_vector', 'search_vector', postgresql_using='gin'),
        ]


class SearchQueryParser:
    """Parse and process search queries for PostgreSQL full-text search."""
    
    @staticmethod
    def parse_query(query: str, language: str = 'english') -> str:
        """
        Parse user query into PostgreSQL tsquery format.
        
        Args:
            query: User search query
            language: Language configuration for text search
            
        Returns:
            Formatted tsquery string
        """
        # Remove special characters that might break tsquery
        query = re.sub(r'[^\w\s\-\'"&|!()]', ' ', query)
        
        # Handle phrases in quotes
        phrases = re.findall(r'"([^"]+)"', query)
        for phrase in phrases:
            # Replace spaces with <-> for phrase search
            phrase_tsquery = phrase.replace(' ', ' <-> ')
            query = query.replace(f'"{phrase}"', f'({phrase_tsquery})')
        
        # Handle boolean operators
        query = query.replace(' AND ', ' & ')
        query = query.replace(' OR ', ' | ')
        query = query.replace(' NOT ', ' & !')
        
        # Split remaining words and join with AND operator
        words = query.split()
        processed_words = []
        
        for word in words:
            if word not in ['&', '|', '!', '(', ')']:
                # Add prefix matching for partial words
                if len(word) > 3:
                    processed_words.append(f"{word}:*")
                else:
                    processed_words.append(word)
            else:
                processed_words.append(word)
        
        # Join with AND operator by default
        if processed_words:
            result = ' & '.join(w for w in processed_words if w not in ['&', '|'])
            return result
        
        return query


class FullTextSearch:
    """Full-text search implementation for documents."""
    
    def __init__(self, session: AsyncSession):
        """Initialize full-text search with database session."""
        self.session = session
        self.parser = SearchQueryParser()
    
    async def search(
        self,
        query: str,
        filters: Optional[Dict[str, Any]] = None,
        limit: int = 10,
        offset: int = 0,
        language: str = 'english',
        rank_by: str = 'relevance'
    ) -> Tuple[List[Document], int]:
        """
        Perform full-text search on documents.
        
        Args:
            query: Search query string
            filters: Additional filters to apply
            limit: Maximum number of results
            offset: Offset for pagination
            language: Language configuration for search
            rank_by: Ranking method ('relevance', 'date', 'credibility')
            
        Returns:
            Tuple of (results, total_count)
        """
        try:
            # Parse query into tsquery format
            tsquery = self.parser.parse_query(query, language)
            
            # Build base query with full-text search
            base_query = f"""
                SELECT 
                    *,
                    ts_rank(search_vector, to_tsquery('{language}', :query)) as rank,
                    ts_headline(
                        '{language}',
                        processed_text,
                        to_tsquery('{language}', :query),
                        'MaxWords=50, MinWords=25, StartSel=<mark>, StopSel=</mark>'
                    ) as headline
                FROM research_documents
                WHERE search_vector @@ to_tsquery('{language}', :query)
            """
            
            # Add filters
            conditions = []
            params = {'query': tsquery}
            
            if filters:
                if 'source_type' in filters:
                    conditions.append("source_type = :source_type")
                    params['source_type'] = filters['source_type']
                
                if 'language' in filters:
                    conditions.append("language = :lang")
                    params['lang'] = filters['language']
                
                if 'date_from' in filters:
                    conditions.append("created_at >= :date_from")
                    params['date_from'] = filters['date_from']
                
                if 'date_to' in filters:
                    conditions.append("created_at <= :date_to")
                    params['date_to'] = filters['date_to']
                
                if 'min_credibility' in filters:
                    conditions.append("credibility_score >= :min_cred")
                    params['min_cred'] = filters['min_credibility']
            
            if conditions:
                base_query += " AND " + " AND ".join(conditions)
            
            # Add ordering
            if rank_by == 'relevance':
                base_query += " ORDER BY rank DESC"
            elif rank_by == 'date':
                base_query += " ORDER BY created_at DESC"
            elif rank_by == 'credibility':
                base_query += " ORDER BY credibility_score DESC NULLS LAST"
            else:
                base_query += " ORDER BY rank DESC"
            
            # Get total count
            count_query = f"""
                SELECT COUNT(*) FROM research_documents
                WHERE search_vector @@ to_tsquery('{language}', :query)
            """
            if conditions:
                count_query += " AND " + " AND ".join(conditions)
            
            count_result = await self.session.execute(text(count_query), params)
            total_count = count_result.scalar()
            
            # Add pagination
            base_query += " LIMIT :limit OFFSET :offset"
            params['limit'] = limit
            params['offset'] = offset
            
            # Execute search query
            result = await self.session.execute(text(base_query), params)
            documents = result.fetchall()
            
            logger.info(f"Full-text search for '{query}' returned {len(documents)} results")
            
            return documents, total_count
            
        except Exception as e:
            logger.error(f"Full-text search error: {e}")
            raise
    
    async def update_search_vector(
        self,
        document_id: str,
        fields: List[str] = None
    ) -> None:
        """
        Update the search vector for a document.
        
        Args:
            document_id: Document ID to update
            fields: List of fields to include in search vector
        """
        if fields is None:
            fields = ['title', 'processed_text', 'summary', 'author']
        
        # Build the tsvector update query
        vector_parts = []
        weights = {'title': 'A', 'summary': 'B', 'processed_text': 'C', 'author': 'D'}
        
        for field in fields:
            weight = weights.get(field, 'D')
            vector_parts.append(f"setweight(to_tsvector('english', COALESCE({field}, '')), '{weight}')")
        
        update_query = f"""
            UPDATE research_documents
            SET search_vector = {' || '.join(vector_parts)}
            WHERE id = :document_id
        """
        
        await self.session.execute(
            text(update_query),
            {'document_id': document_id}
        )
        await self.session.commit()
        
        logger.info(f"Updated search vector for document {document_id}")
    
    async def create_search_indexes(self) -> None:
        """Create necessary indexes for full-text search."""
        try:
            # Create GIN index on search_vector column
            await self.session.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_documents_search_vector 
                ON research_documents USING gin(search_vector)
            """))
            
            # Create index on language for filtering
            await self.session.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_documents_language 
                ON research_documents(language)
            """))
            
            # Create composite index for common filters
            await self.session.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_documents_search_filters 
                ON research_documents(source_type, created_at DESC)
            """))
            
            await self.session.commit()
            logger.info("Created full-text search indexes")
            
        except Exception as e:
            logger.error(f"Error creating search indexes: {e}")
            raise
    
    async def analyze_query(self, query: str) -> Dict[str, Any]:
        """
        Analyze a search query for debugging and optimization.
        
        Args:
            query: Search query to analyze
            
        Returns:
            Analysis results including parsed query and statistics
        """
        tsquery = self.parser.parse_query(query)
        
        # Get query statistics
        stats_query = text("""
            SELECT 
                COUNT(*) as total_matches,
                AVG(ts_rank(search_vector, to_tsquery('english', :query))) as avg_rank,
                MAX(ts_rank(search_vector, to_tsquery('english', :query))) as max_rank
            FROM research_documents
            WHERE search_vector @@ to_tsquery('english', :query)
        """)
        
        result = await self.session.execute(stats_query, {'query': tsquery})
        stats = result.fetchone()
        
        return {
            'original_query': query,
            'parsed_query': tsquery,
            'total_matches': stats.total_matches or 0,
            'avg_relevance': float(stats.avg_rank) if stats.avg_rank else 0,
            'max_relevance': float(stats.max_rank) if stats.max_rank else 0
        }


class SearchFacets:
    """Generate facets for search filtering."""
    
    def __init__(self, session: AsyncSession):
        """Initialize search facets with database session."""
        self.session = session
    
    async def get_facets(
        self,
        query: Optional[str] = None,
        facet_fields: List[str] = None
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        Get facets for search results.
        
        Args:
            query: Optional search query to filter facets
            facet_fields: List of fields to generate facets for
            
        Returns:
            Dictionary of facets with counts
        """
        if facet_fields is None:
            facet_fields = ['source_type', 'language', 'dynasty']
        
        facets = {}
        
        for field in facet_fields:
            # Build facet query
            if query:
                facet_query = text(f"""
                    SELECT {field}, COUNT(*) as count
                    FROM research_documents
                    WHERE search_vector @@ to_tsquery('english', :query)
                    AND {field} IS NOT NULL
                    GROUP BY {field}
                    ORDER BY count DESC
                    LIMIT 20
                """)
                params = {'query': SearchQueryParser.parse_query(query)}
            else:
                facet_query = text(f"""
                    SELECT {field}, COUNT(*) as count
                    FROM research_documents
                    WHERE {field} IS NOT NULL
                    GROUP BY {field}
                    ORDER BY count DESC
                    LIMIT 20
                """)
                params = {}
            
            result = await self.session.execute(facet_query, params)
            facets[field] = [
                {'value': row[0], 'count': row[1]}
                for row in result.fetchall()
            ]
        
        return facets
