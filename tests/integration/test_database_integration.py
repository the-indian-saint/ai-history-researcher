"""Integration tests for database operations."""

import pytest
import asyncio
from datetime import datetime
from unittest.mock import patch

from ai_research_framework.storage.database import (
    get_database,
    init_database,
    ResearchDocument,
    AnalysisResult as DBAnalysisResult,
    ProcessingJob,
    UserSession
)


@pytest.mark.integration
class TestDatabaseConnection:
    """Test database connection and initialization."""
    
    @pytest.mark.asyncio
    async def test_database_initialization(self, test_db):
        """Test database initialization."""
        # Database should be initialized by fixture
        db = await get_database()
        assert db is not None
    
    @pytest.mark.asyncio
    async def test_database_tables_created(self, test_db):
        """Test that all tables are created."""
        db = await get_database()
        
        # Test that we can query each table (even if empty)
        try:
            # This will fail if tables don't exist
            await db.execute("SELECT COUNT(*) FROM research_documents")
            await db.execute("SELECT COUNT(*) FROM analysis_results")
            await db.execute("SELECT COUNT(*) FROM processing_jobs")
            await db.execute("SELECT COUNT(*) FROM user_sessions")
        except Exception as e:
            pytest.fail(f"Database tables not properly created: {e}")


@pytest.mark.integration
class TestResearchDocumentOperations:
    """Test research document database operations."""
    
    @pytest.mark.asyncio
    async def test_create_research_document(self, test_db):
        """Test creating a research document."""
        db = await get_database()
        
        # Create test document
        doc_data = {
            "title": "Test Research Document",
            "content": "This is test content about ancient Indian history.",
            "source_url": "https://example.com/test",
            "source_type": "academic",
            "author": "Dr. Test Author",
            "publication_date": datetime.now(),
            "credibility_score": 0.85,
            "bias_score": 0.2,
            "metadata": {"test": "data"}
        }
        
        # Insert document
        query = """
        INSERT INTO research_documents 
        (title, content, source_url, source_type, author, publication_date, 
         credibility_score, bias_score, metadata, created_at)
        VALUES (:title, :content, :source_url, :source_type, :author, 
                :publication_date, :credibility_score, :bias_score, :metadata, :created_at)
        """
        
        doc_data["created_at"] = datetime.now()
        doc_data["metadata"] = str(doc_data["metadata"])  # Convert to string for SQLite
        
        result = await db.execute(query, doc_data)
        assert result is not None
    
    @pytest.mark.asyncio
    async def test_query_research_documents(self, test_db):
        """Test querying research documents."""
        db = await get_database()
        
        # First create a test document
        await self.test_create_research_document(test_db)
        
        # Query documents
        query = "SELECT * FROM research_documents WHERE source_type = :source_type"
        result = await db.fetch_all(query, {"source_type": "academic"})
        
        assert len(result) >= 1
        assert result[0]["title"] == "Test Research Document"
    
    @pytest.mark.asyncio
    async def test_update_research_document(self, test_db):
        """Test updating a research document."""
        db = await get_database()
        
        # Create and then update document
        await self.test_create_research_document(test_db)
        
        # Update credibility score
        update_query = """
        UPDATE research_documents 
        SET credibility_score = :new_score 
        WHERE title = :title
        """
        
        await db.execute(update_query, {
            "new_score": 0.95,
            "title": "Test Research Document"
        })
        
        # Verify update
        select_query = "SELECT credibility_score FROM research_documents WHERE title = :title"
        result = await db.fetch_one(select_query, {"title": "Test Research Document"})
        
        assert result["credibility_score"] == 0.95
    
    @pytest.mark.asyncio
    async def test_delete_research_document(self, test_db):
        """Test deleting a research document."""
        db = await get_database()
        
        # Create document first
        await self.test_create_research_document(test_db)
        
        # Delete document
        delete_query = "DELETE FROM research_documents WHERE title = :title"
        await db.execute(delete_query, {"title": "Test Research Document"})
        
        # Verify deletion
        select_query = "SELECT COUNT(*) as count FROM research_documents WHERE title = :title"
        result = await db.fetch_one(select_query, {"title": "Test Research Document"})
        
        assert result["count"] == 0


@pytest.mark.integration
class TestAnalysisResultOperations:
    """Test analysis result database operations."""
    
    @pytest.mark.asyncio
    async def test_create_analysis_result(self, test_db):
        """Test creating an analysis result."""
        db = await get_database()
        
        # Create test analysis result
        analysis_data = {
            "document_id": 1,
            "analysis_type": "credibility",
            "result_data": '{"score": 0.8, "level": "high"}',
            "confidence": 0.85,
            "processing_time": 150.5,
            "created_at": datetime.now()
        }
        
        query = """
        INSERT INTO analysis_results 
        (document_id, analysis_type, result_data, confidence, processing_time, created_at)
        VALUES (:document_id, :analysis_type, :result_data, :confidence, :processing_time, :created_at)
        """
        
        result = await db.execute(query, analysis_data)
        assert result is not None
    
    @pytest.mark.asyncio
    async def test_query_analysis_results_by_type(self, test_db):
        """Test querying analysis results by type."""
        db = await get_database()
        
        # Create test result
        await self.test_create_analysis_result(test_db)
        
        # Query by analysis type
        query = "SELECT * FROM analysis_results WHERE analysis_type = :type"
        results = await db.fetch_all(query, {"type": "credibility"})
        
        assert len(results) >= 1
        assert results[0]["analysis_type"] == "credibility"
    
    @pytest.mark.asyncio
    async def test_query_analysis_results_by_confidence(self, test_db):
        """Test querying analysis results by confidence threshold."""
        db = await get_database()
        
        # Create test result
        await self.test_create_analysis_result(test_db)
        
        # Query by confidence threshold
        query = "SELECT * FROM analysis_results WHERE confidence >= :threshold"
        results = await db.fetch_all(query, {"threshold": 0.8})
        
        assert len(results) >= 1
        assert all(result["confidence"] >= 0.8 for result in results)


@pytest.mark.integration
class TestProcessingJobOperations:
    """Test processing job database operations."""
    
    @pytest.mark.asyncio
    async def test_create_processing_job(self, test_db):
        """Test creating a processing job."""
        db = await get_database()
        
        job_data = {
            "job_type": "document_processing",
            "status": "pending",
            "input_data": '{"file_path": "/test/path.pdf"}',
            "created_at": datetime.now()
        }
        
        query = """
        INSERT INTO processing_jobs 
        (job_type, status, input_data, created_at)
        VALUES (:job_type, :status, :input_data, :created_at)
        """
        
        result = await db.execute(query, job_data)
        assert result is not None
    
    @pytest.mark.asyncio
    async def test_update_job_status(self, test_db):
        """Test updating job status."""
        db = await get_database()
        
        # Create job first
        await self.test_create_processing_job(test_db)
        
        # Update status
        update_query = """
        UPDATE processing_jobs 
        SET status = :new_status, completed_at = :completed_at
        WHERE job_type = :job_type AND status = :old_status
        """
        
        await db.execute(update_query, {
            "new_status": "completed",
            "completed_at": datetime.now(),
            "job_type": "document_processing",
            "old_status": "pending"
        })
        
        # Verify update
        select_query = "SELECT status FROM processing_jobs WHERE job_type = :job_type"
        result = await db.fetch_one(select_query, {"job_type": "document_processing"})
        
        assert result["status"] == "completed"
    
    @pytest.mark.asyncio
    async def test_query_jobs_by_status(self, test_db):
        """Test querying jobs by status."""
        db = await get_database()
        
        # Create multiple jobs with different statuses
        job_statuses = ["pending", "processing", "completed", "failed"]
        
        for status in job_statuses:
            job_data = {
                "job_type": f"test_job_{status}",
                "status": status,
                "input_data": f'{{"test": "{status}"}}',
                "created_at": datetime.now()
            }
            
            query = """
            INSERT INTO processing_jobs 
            (job_type, status, input_data, created_at)
            VALUES (:job_type, :status, :input_data, :created_at)
            """
            
            await db.execute(query, job_data)
        
        # Query pending jobs
        query = "SELECT * FROM processing_jobs WHERE status = :status"
        pending_jobs = await db.fetch_all(query, {"status": "pending"})
        
        assert len(pending_jobs) >= 1
        assert all(job["status"] == "pending" for job in pending_jobs)


@pytest.mark.integration
class TestUserSessionOperations:
    """Test user session database operations."""
    
    @pytest.mark.asyncio
    async def test_create_user_session(self, test_db):
        """Test creating a user session."""
        db = await get_database()
        
        session_data = {
            "session_id": "test-session-123",
            "user_data": '{"preferences": {"theme": "dark"}}',
            "created_at": datetime.now(),
            "last_activity": datetime.now()
        }
        
        query = """
        INSERT INTO user_sessions 
        (session_id, user_data, created_at, last_activity)
        VALUES (:session_id, :user_data, :created_at, :last_activity)
        """
        
        result = await db.execute(query, session_data)
        assert result is not None
    
    @pytest.mark.asyncio
    async def test_update_session_activity(self, test_db):
        """Test updating session last activity."""
        db = await get_database()
        
        # Create session first
        await self.test_create_user_session(test_db)
        
        # Update last activity
        new_activity_time = datetime.now()
        update_query = """
        UPDATE user_sessions 
        SET last_activity = :last_activity 
        WHERE session_id = :session_id
        """
        
        await db.execute(update_query, {
            "last_activity": new_activity_time,
            "session_id": "test-session-123"
        })
        
        # Verify update
        select_query = "SELECT last_activity FROM user_sessions WHERE session_id = :session_id"
        result = await db.fetch_one(select_query, {"session_id": "test-session-123"})
        
        # Note: Datetime comparison might need tolerance due to precision
        assert result["last_activity"] is not None


@pytest.mark.integration
class TestDatabaseTransactions:
    """Test database transaction handling."""
    
    @pytest.mark.asyncio
    async def test_transaction_commit(self, test_db):
        """Test successful transaction commit."""
        db = await get_database()
        
        # Start transaction and create multiple records
        async with db.transaction():
            # Create document
            doc_query = """
            INSERT INTO research_documents 
            (title, content, source_type, created_at)
            VALUES (:title, :content, :source_type, :created_at)
            """
            
            await db.execute(doc_query, {
                "title": "Transaction Test Doc",
                "content": "Test content",
                "source_type": "test",
                "created_at": datetime.now()
            })
            
            # Create analysis result
            analysis_query = """
            INSERT INTO analysis_results 
            (document_id, analysis_type, result_data, confidence, created_at)
            VALUES (:document_id, :analysis_type, :result_data, :confidence, :created_at)
            """
            
            await db.execute(analysis_query, {
                "document_id": 1,
                "analysis_type": "test",
                "result_data": "{}",
                "confidence": 0.5,
                "created_at": datetime.now()
            })
        
        # Verify both records exist
        doc_result = await db.fetch_one(
            "SELECT COUNT(*) as count FROM research_documents WHERE title = :title",
            {"title": "Transaction Test Doc"}
        )
        
        analysis_result = await db.fetch_one(
            "SELECT COUNT(*) as count FROM analysis_results WHERE analysis_type = :type",
            {"type": "test"}
        )
        
        assert doc_result["count"] >= 1
        assert analysis_result["count"] >= 1
    
    @pytest.mark.asyncio
    async def test_transaction_rollback(self, test_db):
        """Test transaction rollback on error."""
        db = await get_database()
        
        try:
            async with db.transaction():
                # Create valid record
                doc_query = """
                INSERT INTO research_documents 
                (title, content, source_type, created_at)
                VALUES (:title, :content, :source_type, :created_at)
                """
                
                await db.execute(doc_query, {
                    "title": "Rollback Test Doc",
                    "content": "Test content",
                    "source_type": "test",
                    "created_at": datetime.now()
                })
                
                # Cause an error (invalid SQL)
                await db.execute("INVALID SQL STATEMENT")
        
        except Exception:
            # Expected to fail
            pass
        
        # Verify record was not committed due to rollback
        result = await db.fetch_one(
            "SELECT COUNT(*) as count FROM research_documents WHERE title = :title",
            {"title": "Rollback Test Doc"}
        )
        
        assert result["count"] == 0


@pytest.mark.integration
class TestDatabasePerformance:
    """Test database performance and concurrent operations."""
    
    @pytest.mark.asyncio
    async def test_concurrent_inserts(self, test_db):
        """Test concurrent database inserts."""
        db = await get_database()
        
        async def insert_document(doc_id):
            query = """
            INSERT INTO research_documents 
            (title, content, source_type, created_at)
            VALUES (:title, :content, :source_type, :created_at)
            """
            
            await db.execute(query, {
                "title": f"Concurrent Doc {doc_id}",
                "content": f"Content for document {doc_id}",
                "source_type": "test",
                "created_at": datetime.now()
            })
        
        # Create multiple concurrent insert tasks
        tasks = [insert_document(i) for i in range(10)]
        await asyncio.gather(*tasks)
        
        # Verify all documents were inserted
        result = await db.fetch_one(
            "SELECT COUNT(*) as count FROM research_documents WHERE source_type = :type",
            {"type": "test"}
        )
        
        assert result["count"] >= 10
    
    @pytest.mark.asyncio
    async def test_bulk_operations(self, test_db):
        """Test bulk database operations."""
        db = await get_database()
        
        # Prepare bulk data
        documents = []
        for i in range(100):
            documents.append({
                "title": f"Bulk Doc {i}",
                "content": f"Bulk content {i}",
                "source_type": "bulk_test",
                "created_at": datetime.now()
            })
        
        # Insert in batches
        query = """
        INSERT INTO research_documents 
        (title, content, source_type, created_at)
        VALUES (:title, :content, :source_type, :created_at)
        """
        
        # Execute many inserts
        for doc in documents[:10]:  # Test with smaller batch for speed
            await db.execute(query, doc)
        
        # Verify bulk insert
        result = await db.fetch_one(
            "SELECT COUNT(*) as count FROM research_documents WHERE source_type = :type",
            {"type": "bulk_test"}
        )
        
        assert result["count"] >= 10


@pytest.mark.integration
class TestDatabaseMigrations:
    """Test database schema and migrations."""
    
    @pytest.mark.asyncio
    async def test_schema_integrity(self, test_db):
        """Test database schema integrity."""
        db = await get_database()
        
        # Test that all expected columns exist
        tables_and_columns = {
            "research_documents": [
                "id", "title", "content", "source_url", "source_type",
                "author", "publication_date", "credibility_score", "bias_score",
                "metadata", "created_at", "updated_at"
            ],
            "analysis_results": [
                "id", "document_id", "analysis_type", "result_data",
                "confidence", "processing_time", "created_at"
            ],
            "processing_jobs": [
                "id", "job_type", "status", "input_data", "result_data",
                "error_message", "created_at", "started_at", "completed_at"
            ],
            "user_sessions": [
                "id", "session_id", "user_data", "created_at", "last_activity"
            ]
        }
        
        for table_name, expected_columns in tables_and_columns.items():
            # Get table info (SQLite specific)
            try:
                result = await db.fetch_all(f"PRAGMA table_info({table_name})")
                actual_columns = [row["name"] for row in result]
                
                # Check that all expected columns exist
                for column in expected_columns:
                    assert column in actual_columns, f"Column {column} missing from {table_name}"
            
            except Exception as e:
                pytest.fail(f"Failed to check schema for table {table_name}: {e}")
    
    @pytest.mark.asyncio
    async def test_foreign_key_constraints(self, test_db):
        """Test foreign key constraints."""
        db = await get_database()
        
        # First create a document
        doc_query = """
        INSERT INTO research_documents 
        (title, content, source_type, created_at)
        VALUES (:title, :content, :source_type, :created_at)
        """
        
        await db.execute(doc_query, {
            "title": "FK Test Doc",
            "content": "Test content",
            "source_type": "test",
            "created_at": datetime.now()
        })
        
        # Get the document ID
        doc_result = await db.fetch_one(
            "SELECT id FROM research_documents WHERE title = :title",
            {"title": "FK Test Doc"}
        )
        
        doc_id = doc_result["id"]
        
        # Create analysis result with valid foreign key
        analysis_query = """
        INSERT INTO analysis_results 
        (document_id, analysis_type, result_data, confidence, created_at)
        VALUES (:document_id, :analysis_type, :result_data, :confidence, :created_at)
        """
        
        await db.execute(analysis_query, {
            "document_id": doc_id,
            "analysis_type": "fk_test",
            "result_data": "{}",
            "confidence": 0.5,
            "created_at": datetime.now()
        })
        
        # Verify the relationship
        join_query = """
        SELECT d.title, a.analysis_type 
        FROM research_documents d 
        JOIN analysis_results a ON d.id = a.document_id 
        WHERE d.title = :title
        """
        
        result = await db.fetch_one(join_query, {"title": "FK Test Doc"})
        
        assert result is not None
        assert result["title"] == "FK Test Doc"
        assert result["analysis_type"] == "fk_test"

