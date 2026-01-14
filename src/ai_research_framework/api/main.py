"""Main FastAPI application for the AI Research Framework."""

import asyncio
import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
import uvicorn

from ..config import settings
from .routes import auth, research, documents, search, analysis, health, generate
from .middleware import LoggingMiddleware, RateLimitMiddleware
from ..utils.logging import setup_logging


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan manager."""
    # Startup
    logging.info("Starting AI Research Framework...")
    
    # Initialize database
    try:
        from ..storage.database import init_database
        await init_database()
        logging.info("Database initialized successfully")
    except Exception as e:
        logging.error(f"Failed to initialize database: {e}")
        raise
    
    # Initialize ChromaDB
    try:
        from ..storage.vector_storage import init_vector_storage
        await init_vector_storage()
        logging.info("Vector storage initialized successfully")
    except Exception as e:
        logging.error(f"Failed to initialize vector storage: {e}")
        # Don't raise - continue without vector storage
    
    # Initialize Redis
    try:
        from ..storage.cache import init_cache
        await init_cache()
        logging.info("Cache initialized successfully")
    except Exception as e:
        logging.error(f"Failed to initialize cache: {e}")
        raise
    
    logging.info("AI Research Framework started successfully")
    
    yield
    
    # Shutdown
    logging.info("Shutting down AI Research Framework...")
    
    # Close database connections
    try:
        from ..storage.database import close_database
        await close_database()
        logging.info("Database connections closed")
    except Exception as e:
        logging.error(f"Error closing database: {e}")
    
    # Close cache connections
    try:
        from ..storage.cache import close_cache
        await close_cache()
        logging.info("Cache connections closed")
    except Exception as e:
        logging.error(f"Error closing cache: {e}")
    
    logging.info("AI Research Framework shutdown complete")


# Initialize logging
setup_logging()

# Create FastAPI application
app = FastAPI(
    title=settings.app_name,
    description="AI Research Framework for Ancient Indian History",
    version=settings.app_version,
    docs_url="/docs" if settings.is_development else None,
    redoc_url="/redoc" if settings.is_development else None,
    lifespan=lifespan,
)

# Add security middleware
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["*"] if settings.is_development else ["yourdomain.com", "*.yourdomain.com"]
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins if not settings.is_development else ["*"],
    allow_credentials=settings.cors_allow_credentials,
    allow_methods=settings.cors_allow_methods,
    allow_headers=settings.cors_allow_headers,
)

# Add custom middleware
app.add_middleware(LoggingMiddleware)
app.add_middleware(RateLimitMiddleware)

# Include routers
app.include_router(health.router, prefix="/health", tags=["Health"])
app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
app.include_router(research.router, prefix="/api/v1/research", tags=["Research"])
app.include_router(documents.router, prefix="/api/v1/documents", tags=["Documents"])
app.include_router(search.router, prefix="/api/v1/search", tags=["Search"])
app.include_router(analysis.router, prefix="/api/v1/analysis", tags=["Analysis"])
app.include_router(generate.router, prefix="/api/v1/generate", tags=["Generation"])


@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc: HTTPException):
    """Handle HTTP exceptions with consistent error format."""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "code": exc.status_code,
                "message": exc.detail,
                "type": "http_error"
            }
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc: Exception):
    """Handle general exceptions."""
    logging.error(f"Unhandled exception: {exc}", exc_info=True)
    
    if settings.is_development:
        return JSONResponse(
            status_code=500,
            content={
                "error": {
                    "code": 500,
                    "message": str(exc),
                    "type": "internal_error"
                }
            }
        )
    else:
        return JSONResponse(
            status_code=500,
            content={
                "error": {
                    "code": 500,
                    "message": "Internal server error",
                    "type": "internal_error"
                }
            }
        )


@app.get("/")
async def root():
    """Root endpoint with basic information."""
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "description": "AI Research Framework for Ancient Indian History",
        "status": "running",
        "environment": settings.environment,
        "docs_url": "/docs" if settings.is_development else None,
    }


def run_server():
    """Run the server with uvicorn."""
    uvicorn.run(
        "ai_research_framework.api.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.is_development,
        workers=1 if settings.is_development else settings.workers,
        log_level=settings.log_level.lower(),
        access_log=True,
    )


if __name__ == "__main__":
    run_server()

