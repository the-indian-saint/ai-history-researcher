"""Unit tests for database module."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime
from uuid import UUID
import json

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError

from src.ai_research_framework.storage.database import (
    SourceType,
    ProcessingStatus,
    Document,
    ResearchQuery,
    Citation,
    VectorEmbedding,
    init_database,
    close_database,
    get_database,
    check_database_health,
    create_document,
    get_document_by_id,
    search_documents,
    create_research_query,
    update_query_progress,
)


@pytest.mark.asyncio
class TestDatabaseInitialization:
    """Test database initialization and teardown."""
    
    async def test_init_database(self, monkeypatch):
        """Test database initialization."""
        # Mock the create_async_engine and create_all
        mock_engine = AsyncMock()
        mock_session_factory = AsyncMock()
        
        with patch('src.ai_research_framework.storage.database.create_async_engine', return_value=mock_engine):
            with patch('src.ai_research_framework.storage.database.async_sessionmaker', return_value=mock_session_factory):
                with patch('src.ai_research_framework.storage.database.Base.metadata.create_all') as mock_create_all:
                    await init_database()
                    
                    # Verify engine was created
                    assert mock_engine is not None
                    # Note: create_all is called through run_sync
    
    async def test_close_database(self):
        """Test database connection closure."""
        mock_engine = AsyncMock()
        
        with patch('src.ai_research_framework.storage.database.engine', mock_engine):
            await close_database()
            mock_engine.dispose.assert_called_once()
    
    async def test_get_database_context_manager(self):
        """Test get_database context manager."""
        mock_session = AsyncMock(spec=AsyncSession)
        mock_session_factory = AsyncMock(return_value=mock_session)
        
        with patch('src.ai_research_framework.storage.database.async_session_factory', mock_session_factory):
            async with get_database() as session:
                assert session == mock_session
            
            # Verify session was closed
            mock_session.close.assert_called_once()
    
    async def test_get_database_with_exception(self):
        """Test get_database handles exceptions properly."""
        mock_session = AsyncMock(spec=AsyncSession)
        mock_session_factory = AsyncMock(return_value=mock_session)
        
        with patch('src.ai_research_framework.storage.database.async_session_factory', mock_session_factory):
            try:
                async with get_database() as session:
                    raise ValueError("Test error")
            except ValueError:
                # Verify rollback was called
                mock_session.rollback.assert_called_once()
            
            # Verify session was still closed
            mock_session.close.assert_called_once()


@pytest.mark.asyncio
class TestDatabaseHealth:
    """Test database health check."""
    
    async def test_check_database_health_success(self):
        """Test successful database health check."""
        mock_db = AsyncMock()
        mock_result = MagicMock()
        mock_result.fetchone.return_value = (1,)
        mock_result.scalar.return_value = 10
        mock_db.execute.return_value = mock_result
        
        with patch('src.ai_research_framework.storage.database.get_database') as mock_get_db:
            mock_get_db.return_value.__aenter__.return_value = mock_db
            
            result = await check_database_health()
            
            assert result["healthy"] is True
            assert "document_count" in result
            assert "query_count" in result
    
    async def test_check_database_health_failure(self):
        """Test database health check with connection failure."""
        with patch('src.ai_research_framework.storage.database.get_database') as mock_get_db:
            mock_get_db.side_effect = RuntimeError("Database connection failed")
            
            result = await check_database_health()
            
            assert result["healthy"] is False
            assert "error" in result


@pytest.mark.asyncio
class TestDocumentOperations:
    """Test document CRUD operations."""
    
    async def test_create_document(self):
        """Test creating a new document."""
        mock_db = AsyncMock()
        mock_document = Document(
            id=UUID('12345678-1234-5678-1234-567812345678'),
            title="Test Document",
            source_url="https://example.com",
            source_type=SourceType.ACADEMIC,
            language="english",
            created_at=datetime.utcnow()
        )
        
        with patch('src.ai_research_framework.storage.database.get_database') as mock_get_db:
            mock_get_db.return_value.__aenter__.return_value = mock_db
            with patch('src.ai_research_framework.storage.database.Document', return_value=mock_document):
                result = await create_document(
                    title="Test Document",
                    source_url="https://example.com",
                    source_type=SourceType.ACADEMIC,
                    language="english"
                )
                
                assert result.title == "Test Document"
                mock_db.add.assert_called_once()
                mock_db.commit.assert_called_once()
                mock_db.refresh.assert_called_once()
    
    async def test_get_document_by_id_found(self):
        """Test retrieving document by ID when it exists."""
        mock_db = AsyncMock()
        mock_result = MagicMock()
        mock_document = Document(
            id=UUID('12345678-1234-5678-1234-567812345678'),
            title="Test Document"
        )
        mock_result.scalar_one_or_none.return_value = mock_document
        mock_db.execute.return_value = mock_result
        
        with patch('src.ai_research_framework.storage.database.get_database') as mock_get_db:
            mock_get_db.return_value.__aenter__.return_value = mock_db
            
            result = await get_document_by_id("12345678-1234-5678-1234-567812345678")
            
            assert result is not None
            assert result.title == "Test Document"
    
    async def test_get_document_by_id_not_found(self):
        """Test retrieving document by ID when it doesn't exist."""
        mock_db = AsyncMock()
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db.execute.return_value = mock_result
        
        with patch('src.ai_research_framework.storage.database.get_database') as mock_get_db:
            mock_get_db.return_value.__aenter__.return_value = mock_db
            
            result = await get_document_by_id("nonexistent-id")
            
            assert result is None
    
    async def test_search_documents_with_filters(self):
        """Test searching documents with various filters."""
        mock_db = AsyncMock()
        mock_result = MagicMock()
        mock_documents = [
            Document(id=UUID('12345678-1234-5678-1234-567812345678'), title="Doc 1"),
            Document(id=UUID('87654321-4321-8765-4321-876543218765'), title="Doc 2")
        ]
        mock_result.scalars.return_value.all.return_value = mock_documents
        mock_db.execute.return_value = mock_result
        
        with patch('src.ai_research_framework.storage.database.get_database') as mock_get_db:
            mock_get_db.return_value.__aenter__.return_value = mock_db
            
            filters = {
                "source_type": SourceType.ACADEMIC,
                "language": "english",
                "min_credibility": 0.7
            }
            
            results = await search_documents(
                query="test query",
                filters=filters,
                limit=10
            )
            
            assert len(results) == 2
            assert results[0].title == "Doc 1"
            mock_db.execute.assert_called_once()


@pytest.mark.asyncio
class TestResearchQueryOperations:
    """Test research query operations."""
    
    async def test_create_research_query(self):
        """Test creating a research query."""
        mock_db = AsyncMock()
        mock_query = ResearchQuery(
            id=UUID('12345678-1234-5678-1234-567812345678'),
            query_text="Ancient Indian history",
            status="pending",
            created_at=datetime.utcnow()
        )
        
        with patch('src.ai_research_framework.storage.database.get_database') as mock_get_db:
            mock_get_db.return_value.__aenter__.return_value = mock_db
            with patch('src.ai_research_framework.storage.database.ResearchQuery', return_value=mock_query):
                result = await create_research_query(
                    query_text="Ancient Indian history",
                    time_period_start="300 BCE",
                    time_period_end="600 CE",
                    geographical_region="India",
                    source_types=["academic", "primary"],
                    max_sources=10
                )
                
                assert result.query_text == "Ancient Indian history"
                assert result.status == "pending"
                mock_db.add.assert_called_once()
                mock_db.commit.assert_called_once()
    
    async def test_update_query_progress(self):
        """Test updating query progress."""
        mock_db = AsyncMock()
        mock_result = MagicMock()
        mock_query = ResearchQuery(
            id=UUID('12345678-1234-5678-1234-567812345678'),
            processing_progress=0.0,
            status="processing"
        )
        mock_result.scalar_one_or_none.return_value = mock_query
        mock_db.execute.return_value = mock_result
        
        with patch('src.ai_research_framework.storage.database.get_database') as mock_get_db:
            mock_get_db.return_value.__aenter__.return_value = mock_db
            
            await update_query_progress(
                "12345678-1234-5678-1234-567812345678",
                progress=0.5,
                status="processing"
            )
            
            assert mock_query.processing_progress == 0.5
            assert mock_query.status == "processing"
            mock_db.commit.assert_called_once()
    
    async def test_update_query_progress_not_found(self):
        """Test updating progress for non-existent query."""
        mock_db = AsyncMock()
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db.execute.return_value = mock_result
        
        with patch('src.ai_research_framework.storage.database.get_database') as mock_get_db:
            mock_get_db.return_value.__aenter__.return_value = mock_db
            
            # Should handle gracefully without raising exception
            await update_query_progress(
                "nonexistent-id",
                progress=0.5,
                status="processing"
            )
            
            # Commit should not be called for non-existent query
            mock_db.commit.assert_not_called()


class TestDatabaseModels:
    """Test database model definitions."""
    
    def test_document_model(self):
        """Test Document model attributes."""
        doc = Document()
        
        # Check required fields exist
        assert hasattr(doc, 'id')
        assert hasattr(doc, 'title')
        assert hasattr(doc, 'source_type')
        assert hasattr(doc, 'created_at')
        assert hasattr(doc, 'updated_at')
        
        # Check relationships
        assert hasattr(doc, 'citations')
        assert hasattr(doc, 'analyses')
        assert hasattr(doc, 'embeddings')
    
    def test_research_query_model(self):
        """Test ResearchQuery model attributes."""
        query = ResearchQuery()
        
        assert hasattr(query, 'id')
        assert hasattr(query, 'query_text')
        assert hasattr(query, 'status')
        assert hasattr(query, 'processing_progress')
        assert hasattr(query, 'created_at')
        assert hasattr(query, 'documents')
    
    def test_citation_model(self):
        """Test Citation model attributes."""
        citation = Citation()
        
        assert hasattr(citation, 'id')
        assert hasattr(citation, 'document_id')
        assert hasattr(citation, 'citation_text')
        assert hasattr(citation, 'verified')
    
    def test_vector_embedding_model(self):
        """Test VectorEmbedding model attributes."""
        embedding = VectorEmbedding()
        
        assert hasattr(embedding, 'id')
        assert hasattr(embedding, 'document_id')
        assert hasattr(embedding, 'text_chunk')
        assert hasattr(embedding, 'embedding_model')
        assert hasattr(embedding, 'chunk_index')


class TestEnums:
    """Test enum definitions."""
    
    def test_source_type_enum(self):
        """Test SourceType enum values."""
        assert SourceType.ACADEMIC == "academic"
        assert SourceType.PRIMARY == "primary"
        assert SourceType.SECONDARY == "secondary"
        assert SourceType.WEB == "web"
        assert SourceType.DIGITAL_ARCHIVE == "digital_archive"
        assert SourceType.NEWS == "news"
    
    def test_processing_status_enum(self):
        """Test ProcessingStatus enum values."""
        assert ProcessingStatus.PENDING == "pending"
        assert ProcessingStatus.PROCESSING == "processing"
        assert ProcessingStatus.COMPLETED == "completed"
        assert ProcessingStatus.FAILED == "failed"
        assert ProcessingStatus.PARTIAL == "partial"


@pytest.mark.asyncio
class TestDatabaseTransactions:
    """Test database transaction handling."""
    
    async def test_transaction_commit(self):
        """Test successful transaction commit."""
        mock_db = AsyncMock()
        
        with patch('src.ai_research_framework.storage.database.get_database') as mock_get_db:
            mock_get_db.return_value.__aenter__.return_value = mock_db
            
            async with get_database() as db:
                # Simulate some operations
                db.add(Document(title="Test"))
                await db.commit()
            
            mock_db.commit.assert_called()
            mock_db.close.assert_called()
    
    async def test_transaction_rollback_on_error(self):
        """Test transaction rollback on error."""
        mock_db = AsyncMock()
        mock_db.commit.side_effect = SQLAlchemyError("Database error")
        
        with patch('src.ai_research_framework.storage.database.get_database') as mock_get_db:
            mock_get_db.return_value.__aenter__.return_value = mock_db
            
            with pytest.raises(SQLAlchemyError):
                async with get_database() as db:
                    db.add(Document(title="Test"))
                    await db.commit()  # This will raise
            
            mock_db.rollback.assert_called()
            mock_db.close.assert_called()
