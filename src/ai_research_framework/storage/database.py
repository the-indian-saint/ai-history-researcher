"""Database connection and management with SQLAlchemy models."""

import asyncio
from datetime import datetime
from typing import Dict, Any, AsyncGenerator, Optional, List
from contextlib import asynccontextmanager
from enum import Enum

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy import (
    Column, Integer, String, Text, DateTime, Float, Boolean, 
    ForeignKey, JSON, text, Index, UniqueConstraint, Enum as SQLEnum
)
from sqlalchemy.dialects.postgresql import UUID
import uuid

from ..config import settings

# Database engine and session
engine = None
async_session_factory = None
Base = declarative_base()


class UserRole(str, Enum):
    """User roles for authorization."""
    USER = "user"
    RESEARCHER = "researcher"
    ADMIN = "admin"
    SUPERADMIN = "superadmin"


class User(Base):
    """User model for authentication and authorization."""
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False)
    username = Column(String(100), unique=True, nullable=False)
    full_name = Column(String(255))
    
    # Authentication
    password_hash = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)
    email_verified_at = Column(DateTime)
    
    # Authorization
    role = Column(SQLEnum(UserRole), default=UserRole.USER, nullable=False)
    permissions = Column(JSON, default=list)  # List of specific permissions
    
    # API keys for external services (encrypted)
    api_keys = Column(JSON, default=dict)  # {"openai": "encrypted_key", ...}
    
    # Settings and preferences
    preferences = Column(JSON, default=dict)
    language = Column(String(10), default="english")
    timezone = Column(String(50), default="UTC")
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login_at = Column(DateTime)
    login_count = Column(Integer, default=0)
    
    # Relationships
    research_queries = relationship("ResearchQuery", back_populates="user")
    api_tokens = relationship("APIToken", back_populates="user", cascade="all, delete-orphan")
    
    # Indexes
    __table_args__ = (
        Index('idx_users_email', 'email'),
        Index('idx_users_username', 'username'),
        Index('idx_users_role', 'role'),
        Index('idx_users_is_active', 'is_active'),
        Index('idx_users_created_at', 'created_at'),
    )


class APIToken(Base):
    """API tokens for user authentication."""
    __tablename__ = "api_tokens"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    
    token = Column(String(255), unique=True, nullable=False)
    name = Column(String(100))  # Optional name for the token
    
    # Token metadata
    scopes = Column(JSON, default=list)  # List of allowed scopes
    last_used_at = Column(DateTime)
    expires_at = Column(DateTime)
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Rate limiting
    rate_limit = Column(Integer, default=100)  # Requests per minute
    rate_limit_window = Column(Integer, default=60)  # Window in seconds
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="api_tokens")
    
    # Indexes
    __table_args__ = (
        Index('idx_api_tokens_token', 'token'),
        Index('idx_api_tokens_user_id', 'user_id'),
        Index('idx_api_tokens_is_active', 'is_active'),
        Index('idx_api_tokens_expires_at', 'expires_at'),
    )


class SourceType(str, Enum):
    """Types of historical sources."""
    ACADEMIC = "academic"
    PRIMARY = "primary"
    ARCHAEOLOGICAL = "archaeological"
    MANUSCRIPT = "manuscript"
    INSCRIPTION = "inscription"
    LITERARY = "literary"
    DIGITAL_ARCHIVE = "digital_archive"


class ProcessingStatus(str, Enum):
    """Document processing status."""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    ARCHIVED = "archived"


class Document(Base):
    """Document model for storing processed historical documents."""
    __tablename__ = "research_documents"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String(500), nullable=False)
    source_url = Column(Text)
    source_type = Column(String(50), nullable=False)
    language = Column(String(10), default="english")
    
    # Content
    raw_text = Column(Text)
    processed_text = Column(Text)
    summary = Column(Text)
    keywords = Column(JSON)  # List of extracted keywords
    entities = Column(JSON)  # Named entities (people, places, dates)
    
    # Metadata
    author = Column(String(200))
    publication_date = Column(DateTime)
    time_period_start = Column(String(50))  # e.g., "320 CE"
    time_period_end = Column(String(50))    # e.g., "550 CE"
    geographical_region = Column(String(100))
    dynasty = Column(String(100))
    
    # Processing info
    processing_status = Column(String(20), default=ProcessingStatus.PENDING)
    ocr_confidence = Column(Float)
    credibility_score = Column(Float)
    bias_assessment = Column(JSON)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    processed_at = Column(DateTime)
    
    # Relationships
    citations = relationship("Citation", back_populates="document")
    research_queries = relationship("ResearchQuery", secondary="query_documents", back_populates="documents")
    
    # Indexes
    __table_args__ = (
        Index('idx_documents_source_type', 'source_type'),
        Index('idx_documents_language', 'language'),
        Index('idx_documents_dynasty', 'dynasty'),
        Index('idx_documents_status', 'processing_status'),
        Index('idx_documents_created', 'created_at'),
    )


class ResearchQuery(Base):
    """Research query model for tracking user research requests."""
    __tablename__ = "research_queries"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    query_text = Column(Text, nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"))
    
    # Query parameters
    time_period_start = Column(String(50))
    time_period_end = Column(String(50))
    geographical_region = Column(String(100))
    source_types = Column(JSON)  # List of source types to search
    max_sources = Column(Integer, default=10)
    
    # Results
    status = Column(String(20), default="pending")
    total_sources_found = Column(Integer, default=0)
    processing_progress = Column(Float, default=0.0)
    results_summary = Column(Text)
    generated_script = Column(Text)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime)
    
    # Relationships
    user = relationship("User", back_populates="research_queries")
    documents = relationship("Document", secondary="query_documents", back_populates="research_queries")
    
    # Indexes
    __table_args__ = (
        Index('idx_queries_user', 'user_id'),
        Index('idx_queries_status', 'status'),
        Index('idx_queries_created', 'created_at'),
    )


class Citation(Base):
    """Citation model for tracking source citations."""
    __tablename__ = "citations"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    document_id = Column(UUID(as_uuid=True), ForeignKey("research_documents.id"), nullable=False)
    
    # Citation details
    citation_text = Column(Text, nullable=False)
    page_number = Column(String(20))
    section = Column(String(100))
    quote = Column(Text)
    context = Column(Text)
    
    # Verification
    verified = Column(Boolean, default=False)
    verification_notes = Column(Text)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    document = relationship("Document", back_populates="citations")


# Association table for many-to-many relationship between queries and documents
query_documents = Base.metadata.tables.get('query_documents') or \
    Column('query_id', UUID(as_uuid=True), ForeignKey('research_queries.id'), primary_key=True), \
    Column('document_id', UUID(as_uuid=True), ForeignKey('research_documents.id'), primary_key=True)

# Create the association table properly
from sqlalchemy import Table
query_documents = Table(
    'query_documents',
    Base.metadata,
    Column('query_id', UUID(as_uuid=True), ForeignKey('research_queries.id'), primary_key=True),
    Column('document_id', UUID(as_uuid=True), ForeignKey('research_documents.id'), primary_key=True)
)


class AnalysisResult(Base):
    """Analysis results for processed documents."""
    __tablename__ = "analysis_results"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    document_id = Column(UUID(as_uuid=True), ForeignKey("research_documents.id"), nullable=False)
    
    # Analysis data
    analysis_type = Column(String(50), nullable=False)  # credibility, bias, entity_extraction, etc.
    result = Column(JSON, nullable=False)  # JSON result of the analysis
    confidence = Column(Float)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Indexes
    __table_args__ = (
        Index('idx_analysis_document', 'document_id'),
        Index('idx_analysis_type', 'analysis_type'),
    )


class ProcessingJob(Base):
    """Background processing jobs."""
    __tablename__ = "processing_jobs"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Job details
    job_type = Column(String(50), nullable=False)  # document_processing, web_scraping, etc.
    status = Column(String(20), default="pending")  # pending, processing, completed, failed
    input_data = Column(JSON)  # Input parameters for the job
    result = Column(JSON)  # Result of the job
    error_message = Column(Text)
    progress = Column(Float, default=0.0)  # 0.0 to 100.0
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    started_at = Column(DateTime)
    completed_at = Column(DateTime)
    
    # Indexes
    __table_args__ = (
        Index('idx_jobs_status', 'status'),
        Index('idx_jobs_type', 'job_type'),
        Index('idx_jobs_created', 'created_at'),
    )


class UserSession(Base):
    """User sessions for authentication and tracking."""
    __tablename__ = "user_sessions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # User data
    user_id = Column(String(100), nullable=False)
    username = Column(String(100))
    email = Column(String(200))
    
    # Session data
    token = Column(String(500), nullable=False)
    is_active = Column(Boolean, default=True)
    ip_address = Column(String(50))
    user_agent = Column(String(500))
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    last_activity = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime)
    
    # Indexes
    __table_args__ = (
        Index('idx_sessions_user', 'user_id'),
        Index('idx_sessions_token', 'token'),
        Index('idx_sessions_active', 'is_active'),
    )


class VectorEmbedding(Base):
    """Vector embeddings for semantic search."""
    __tablename__ = "vector_embeddings"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    document_id = Column(UUID(as_uuid=True), ForeignKey("research_documents.id"), nullable=False)
    
    # Embedding data
    text_chunk = Column(Text, nullable=False)
    embedding_model = Column(String(100), nullable=False)
    chunk_index = Column(Integer, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Indexes
    __table_args__ = (
        Index('idx_embeddings_document', 'document_id'),
        Index('idx_embeddings_model', 'embedding_model'),
        UniqueConstraint('document_id', 'chunk_index', name='uq_document_chunk'),
    )


async def init_database() -> None:
    """Initialize database connection and create tables."""
    global engine, async_session_factory
    
    # Handle SQLite for development
    if settings.database_url.startswith("sqlite"):
        # Convert async SQLite URL for development
        database_url = settings.database_url.replace("sqlite+aiosqlite://", "sqlite+aiosqlite:///")
        engine = create_async_engine(
            database_url,
            echo=settings.is_development,
        )
    else:
        engine = create_async_engine(
            settings.database_url,
            pool_size=settings.database_pool_size,
            max_overflow=settings.database_max_overflow,
            echo=settings.is_development,
        )
    
    async_session_factory = async_sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )
    
    # Create tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def close_database() -> None:
    """Close database connections."""
    global engine
    if engine:
        await engine.dispose()


@asynccontextmanager
async def get_database() -> AsyncGenerator[AsyncSession, None]:
    """Get database session."""
    if not async_session_factory:
        raise RuntimeError("Database not initialized")
    
    async with async_session_factory() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def check_database_health() -> Dict[str, Any]:
    """Check database health."""
    try:
        async with get_database() as db:
            result = await db.execute(text("SELECT 1"))
            row = result.fetchone()
            
            # Get table counts
            document_count = await db.execute(text("SELECT COUNT(*) FROM research_documents"))
            query_count = await db.execute(text("SELECT COUNT(*) FROM research_queries"))
            
            return {
                "healthy": row is not None,
                "connection_pool_size": engine.pool.size() if engine and hasattr(engine, 'pool') else 0,
                "checked_out_connections": engine.pool.checkedout() if engine and hasattr(engine, 'pool') else 0,
                "document_count": document_count.scalar(),
                "query_count": query_count.scalar(),
            }
    except Exception as e:
        return {
            "healthy": False,
            "error": str(e)
        }


# Database utility functions
async def create_document(
    title: str,
    source_url: Optional[str] = None,
    source_type: str = SourceType.ACADEMIC,
    language: str = "english",
    **kwargs
) -> Document:
    """Create a new document record."""
    async with get_database() as db:
        document = Document(
            title=title,
            source_url=source_url,
            source_type=source_type,
            language=language,
            **kwargs
        )
        db.add(document)
        await db.commit()
        await db.refresh(document)
        return document


async def get_document_by_id(document_id: str) -> Optional[Document]:
    """Get document by ID."""
    async with get_database() as db:
        result = await db.execute(
            text("SELECT * FROM research_documents WHERE id = :id"),
            {"id": document_id}
        )
        return result.fetchone()


async def search_documents(
    query: str,
    source_types: Optional[List[str]] = None,
    language: Optional[str] = None,
    limit: int = 10
) -> List[Document]:
    """Search documents by text query."""
    async with get_database() as db:
        sql = "SELECT * FROM research_documents WHERE processed_text ILIKE :query"
        params = {"query": f"%{query}%"}
        
        if source_types:
            sql += " AND source_type = ANY(:source_types)"
            params["source_types"] = source_types
        
        if language:
            sql += " AND language = :language"
            params["language"] = language
        
        sql += " ORDER BY created_at DESC LIMIT :limit"
        params["limit"] = limit
        
        result = await db.execute(text(sql), params)
        return result.fetchall()


async def create_research_query(
    query_text: str,
    user_id: Optional[str] = None,
    **kwargs
) -> ResearchQuery:
    """Create a new research query."""
    async with get_database() as db:
        query = ResearchQuery(
            query_text=query_text,
            user_id=user_id,
            **kwargs
        )
        db.add(query)
        await db.commit()
        await db.refresh(query)
        return query


async def update_query_progress(query_id: str, progress: float, status: str = None) -> None:
    """Update research query progress."""
    async with get_database() as db:
        update_data = {"processing_progress": progress}
        if status:
            update_data["status"] = status
        
        await db.execute(
            text("UPDATE research_queries SET processing_progress = :progress, status = :status WHERE id = :id"),
            {"progress": progress, "status": status, "id": query_id}
        )
        await db.commit()

