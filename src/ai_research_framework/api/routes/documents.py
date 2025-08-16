"""Document management API routes."""

import os
from typing import List, Optional
from datetime import datetime

from fastapi import APIRouter, HTTPException, UploadFile, File, Query, Form
from pydantic import BaseModel, Field
from sqlalchemy import text

from ...storage.database import get_database, create_document, get_document_by_id
from ...processors.document_processor import (
    process_document_file, 
    process_document_url,
    get_supported_document_formats
)
from ...utils.logging import get_logger
from ...config import settings

logger = get_logger(__name__)
router = APIRouter()


class DocumentMetadata(BaseModel):
    """Document metadata model."""
    title: str = Field(..., description="Document title")
    author: Optional[str] = Field(None, description="Document author")
    publication_date: Optional[str] = Field(None, description="Publication date")
    source_type: str = Field(default="academic", description="Source type")
    language: str = Field(default="english", description="Document language")
    tags: List[str] = Field(default=[], description="Document tags")


class DocumentResponse(BaseModel):
    """Document response model."""
    id: str
    title: str
    source_url: Optional[str]
    source_type: str
    author: Optional[str]
    content_summary: Optional[str]
    language: str
    word_count: int
    processing_status: str
    credibility_score: Optional[float]
    created_at: datetime


class DocumentListResponse(BaseModel):
    """Document list response model."""
    documents: List[DocumentResponse]
    total: int
    page: int
    per_page: int


@router.post("/upload", response_model=DocumentResponse)
async def upload_document(
    file: UploadFile = File(...),
    title: Optional[str] = Form(None),
    author: Optional[str] = Form(None),
    source_type: str = Form("academic"),
    language: str = Form("english")
):
    """Upload and process a document file."""
    try:
        # Check file size
        file_size = 0
        content = await file.read()
        file_size = len(content)
        
        if file_size > settings.max_file_size:
            raise HTTPException(
                status_code=413,
                detail=f"File size exceeds maximum allowed size of {settings.max_file_size} bytes"
            )
        
        # Check file format
        file_extension = os.path.splitext(file.filename)[1].lower().strip('.')
        if file_extension not in settings.supported_formats:
            raise HTTPException(
                status_code=415,
                detail=f"Unsupported file format. Supported formats: {', '.join(settings.supported_formats)}"
            )
        
        # Save temporary file
        temp_path = os.path.join(settings.temp_path, file.filename)
        with open(temp_path, "wb") as f:
            f.write(content)
        
        try:
            # Process document
            result = await process_document_file(
                file_path=temp_path,
                metadata={
                    "title": title or file.filename,
                    "author": author,
                    "source_type": source_type,
                    "language": language,
                    "original_filename": file.filename
                }
            )
            
            # Create database record
            document = await create_document(
                title=result.title,
                source_type=source_type,
                language=language,
                author=author,
                content_summary=result.summary,
                word_count=result.word_count,
                processing_status="completed",
                file_path=temp_path
            )
            
            logger.info(f"Document uploaded and processed: {document.id}")
            
            return DocumentResponse(
                id=str(document.id),
                title=document.title,
                source_url=document.source_url,
                source_type=document.source_type,
                author=document.author,
                content_summary=document.content_summary,
                language=document.language,
                word_count=document.word_count,
                processing_status=document.processing_status,
                credibility_score=document.credibility_score,
                created_at=document.created_at
            )
            
        finally:
            # Clean up temp file if needed
            if os.path.exists(temp_path) and not settings.is_development:
                os.remove(temp_path)
                
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error uploading document: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/url", response_model=DocumentResponse)
async def process_url(url: str, metadata: Optional[DocumentMetadata] = None):
    """Process a document from URL."""
    try:
        # Process document from URL
        result = await process_document_url(
            url=url,
            metadata=metadata.dict() if metadata else {}
        )
        
        # Create database record
        document = await create_document(
            title=result.title,
            source_url=url,
            source_type=metadata.source_type if metadata else "web",
            language=metadata.language if metadata else "english",
            author=metadata.author if metadata else result.author,
            content_summary=result.summary,
            word_count=result.word_count,
            processing_status="completed"
        )
        
        logger.info(f"Document processed from URL: {document.id}")
        
        return DocumentResponse(
            id=str(document.id),
            title=document.title,
            source_url=document.source_url,
            source_type=document.source_type,
            author=document.author,
            content_summary=document.content_summary,
            language=document.language,
            word_count=document.word_count,
            processing_status=document.processing_status,
            credibility_score=document.credibility_score,
            created_at=document.created_at
        )
        
    except Exception as e:
        logger.error(f"Error processing URL: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{document_id}", response_model=DocumentResponse)
async def get_document(document_id: str):
    """Get document by ID."""
    try:
        document = await get_document_by_id(document_id)
        
        if not document:
            raise HTTPException(
                status_code=404,
                detail="Document not found"
            )
        
        return DocumentResponse(
            id=str(document.id),
            title=document.title,
            source_url=document.source_url,
            source_type=document.source_type,
            author=document.author,
            content_summary=document.content_summary,
            language=document.language,
            word_count=document.word_count,
            processing_status=document.processing_status,
            credibility_score=document.credibility_score,
            created_at=document.created_at
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting document: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/", response_model=DocumentListResponse)
async def list_documents(
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(20, ge=1, le=100, description="Items per page"),
    source_type: Optional[str] = Query(None, description="Filter by source type"),
    language: Optional[str] = Query(None, description="Filter by language"),
    min_credibility: Optional[float] = Query(None, ge=0, le=1, description="Minimum credibility score")
):
    """List documents with pagination and filters."""
    try:
        async with get_database() as db:
            # Build query with filters
            query = "SELECT * FROM research_documents WHERE 1=1"
            params = {}
            
            if source_type:
                query += " AND source_type = :source_type"
                params["source_type"] = source_type
            
            if language:
                query += " AND language = :language"
                params["language"] = language
            
            if min_credibility is not None:
                query += " AND credibility_score >= :min_credibility"
                params["min_credibility"] = min_credibility
            
            # Get total count
            count_query = query.replace("SELECT *", "SELECT COUNT(*)")
            total_result = await db.execute(text(count_query), params)
            total = total_result.scalar()
            
            # Add pagination
            offset = (page - 1) * per_page
            query += " ORDER BY created_at DESC LIMIT :limit OFFSET :offset"
            params["limit"] = per_page
            params["offset"] = offset
            
            # Execute query
            result = await db.execute(text(query), params)
            documents = result.fetchall()
            
            # Format response
            document_list = [
                DocumentResponse(
                    id=str(doc.id),
                    title=doc.title,
                    source_url=doc.source_url,
                    source_type=doc.source_type,
                    author=doc.author,
                    content_summary=doc.content_summary,
                    language=doc.language,
                    word_count=doc.word_count,
                    processing_status=doc.processing_status,
                    credibility_score=doc.credibility_score,
                    created_at=doc.created_at
                )
                for doc in documents
            ]
            
            return DocumentListResponse(
                documents=document_list,
                total=total,
                page=page,
                per_page=per_page
            )
            
    except Exception as e:
        logger.error(f"Error listing documents: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.delete("/{document_id}")
async def delete_document(document_id: str):
    """Delete a document."""
    try:
        async with get_database() as db:
            # Check if document exists
            result = await db.execute(
                text("SELECT id FROM research_documents WHERE id = :id"),
                {"id": document_id}
            )
            if not result.fetchone():
                raise HTTPException(
                    status_code=404,
                    detail="Document not found"
                )
            
            # Delete document
            await db.execute(
                text("DELETE FROM research_documents WHERE id = :id"),
                {"id": document_id}
            )
            await db.commit()
            
            logger.info(f"Document deleted: {document_id}")
            
            return {"message": "Document deleted successfully"}
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting document: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/formats/supported")
async def get_supported_formats():
    """Get list of supported document formats."""
    return {
        "formats": get_supported_document_formats(),
        "max_file_size": settings.max_file_size,
        "max_file_size_mb": settings.max_file_size / (1024 * 1024)
    }
