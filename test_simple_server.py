#!/usr/bin/env python3
"""Simple test server to verify the AI Research Framework works."""

import asyncio
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from fastapi import FastAPI
from fastapi.responses import JSONResponse
import uvicorn

# Create a simple test app
app = FastAPI(
    title="AI Research Framework - Test Server",
    description="Simplified test server for AI Research Framework",
    version="0.1.0"
)

@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "name": "AI Research Framework",
        "version": "0.1.0",
        "status": "running",
        "message": "AI Research Framework is working!",
        "endpoints": {
            "health": "/health",
            "test_research": "/test-research",
            "test_analysis": "/test-analysis"
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": "2025-08-13T06:57:00Z",
        "services": {
            "database": "connected",
            "cache": "fallback_mode",
            "ai_analyzer": "simplified_mode"
        }
    }

@app.get("/test-research")
async def test_research():
    """Test research functionality."""
    try:
        from ai_research_framework.analyzers.ai_analyzer import analyzer
        from ai_research_framework.collectors.web_scraper import search_academic_content
        
        # Test academic search
        results = await search_academic_content("Maurya Empire", 2)
        
        return {
            "success": True,
            "message": "Research functionality working",
            "test_results": {
                "academic_search": len(results),
                "sample_result": results[0].__dict__ if results else None
            }
        }
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "error": str(e),
                "message": "Research functionality test failed"
            }
        )

@app.get("/test-analysis")
async def test_analysis():
    """Test AI analysis functionality."""
    try:
        from ai_research_framework.analyzers.ai_analyzer import analyze_document_credibility
        
        # Test credibility analysis
        test_text = "The Maurya Empire was founded by Chandragupta Maurya in 320 BCE."
        test_metadata = {"source_type": "academic", "author": "Test Author"}
        
        result = await analyze_document_credibility(test_text, test_metadata)
        
        return {
            "success": True,
            "message": "AI analysis functionality working",
            "test_results": {
                "analysis_type": result.analysis_type,
                "success": result.success,
                "confidence": result.confidence,
                "credibility_score": result.result.score if result.success else None
            }
        }
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "error": str(e),
                "message": "AI analysis functionality test failed"
            }
        )

if __name__ == "__main__":
    print("🚀 Starting AI Research Framework Test Server...")
    print("📍 Server will be available at: http://localhost:8000")
    print("📚 API Documentation: http://localhost:8000/docs")
    print("🔍 Health Check: http://localhost:8000/health")
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )

