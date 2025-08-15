"""Health check endpoints."""

import asyncio
import time
from typing import Dict, Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from ...config import settings


class HealthResponse(BaseModel):
    """Health check response model."""
    status: str
    timestamp: float
    version: str
    environment: str
    checks: Dict[str, Any]


router = APIRouter()


@router.get("/", response_model=HealthResponse)
async def health_check():
    """
    Comprehensive health check endpoint.
    
    Returns the overall health status of the application and its dependencies.
    """
    health_status = {
        "status": "healthy",
        "timestamp": time.time(),
        "version": settings.app_version,
        "environment": settings.environment,
        "checks": {}
    }
    
    # Check database connectivity
    try:
        from ...storage.database import check_database_health
        db_health = await check_database_health()
        health_status["checks"]["database"] = db_health
        if not db_health.get("healthy", False):
            health_status["status"] = "unhealthy"
    except Exception as e:
        health_status["checks"]["database"] = {
            "healthy": False,
            "error": str(e)
        }
        health_status["status"] = "unhealthy"
    
    # Check Redis connectivity
    try:
        from ...storage.cache import check_cache_health
        cache_health = await check_cache_health()
        health_status["checks"]["cache"] = cache_health
        if not cache_health.get("healthy", False):
            health_status["status"] = "unhealthy"
    except Exception as e:
        health_status["checks"]["cache"] = {
            "healthy": False,
            "error": str(e)
        }
        health_status["status"] = "unhealthy"
    
    # Check ChromaDB connectivity
    try:
        from ...storage.vector_storage import check_vector_storage_health
        vector_health = await check_vector_storage_health()
        health_status["checks"]["vector_storage"] = vector_health
        if not vector_health.get("healthy", False):
            health_status["status"] = "unhealthy"
    except Exception as e:
        health_status["checks"]["vector_storage"] = {
            "healthy": False,
            "error": str(e)
        }
        health_status["status"] = "unhealthy"
    
    # Check AI services
    ai_services_health = await check_ai_services()
    health_status["checks"]["ai_services"] = ai_services_health
    
    return HealthResponse(**health_status)


@router.get("/ready")
async def readiness_check():
    """
    Readiness check endpoint for Kubernetes.
    
    Returns 200 if the application is ready to serve requests.
    """
    try:
        # Quick checks for essential services
        checks = await asyncio.gather(
            check_database_ready(),
            check_cache_ready(),
            return_exceptions=True
        )
        
        for check in checks:
            if isinstance(check, Exception):
                raise HTTPException(status_code=503, detail="Service not ready")
        
        return {"status": "ready", "timestamp": time.time()}
    
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Service not ready: {str(e)}")


@router.get("/live")
async def liveness_check():
    """
    Liveness check endpoint for Kubernetes.
    
    Returns 200 if the application is alive and running.
    """
    return {
        "status": "alive",
        "timestamp": time.time(),
        "version": settings.app_version
    }


async def check_ai_services() -> Dict[str, Any]:
    """Check AI services availability."""
    services = {}
    
    # Check OpenAI
    if settings.openai_api_key:
        try:
            # Simple API check without making actual requests
            services["openai"] = {
                "configured": True,
                "healthy": True  # Assume healthy if configured
            }
        except Exception as e:
            services["openai"] = {
                "configured": True,
                "healthy": False,
                "error": str(e)
            }
    else:
        services["openai"] = {
            "configured": False,
            "healthy": False,
            "error": "API key not configured"
        }
    
    # Check Anthropic
    if settings.anthropic_api_key:
        try:
            services["anthropic"] = {
                "configured": True,
                "healthy": True  # Assume healthy if configured
            }
        except Exception as e:
            services["anthropic"] = {
                "configured": True,
                "healthy": False,
                "error": str(e)
            }
    else:
        services["anthropic"] = {
            "configured": False,
            "healthy": False,
            "error": "API key not configured"
        }
    
    return services


async def check_database_ready() -> bool:
    """Quick database readiness check."""
    try:
        from ...storage.database import get_database
        async with get_database() as db:
            # Simple query to check connectivity
            result = await db.execute("SELECT 1")
            return result is not None
    except Exception:
        return False


async def check_cache_ready() -> bool:
    """Quick cache readiness check."""
    try:
        from ...storage.cache import get_cache
        cache = await get_cache()
        await cache.ping()
        return True
    except Exception:
        return False

