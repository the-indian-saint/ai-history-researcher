"""Cache management with Redis support."""

import asyncio
import json
import logging
from typing import Any, Optional, Dict, List
from datetime import datetime, timedelta

import redis.asyncio as redis
from redis.asyncio import Redis

from ..config import settings
from ..utils.logging import get_logger

logger = get_logger(__name__)

# Global Redis client
redis_client: Optional[Redis] = None


async def init_cache() -> None:
    """Initialize Redis cache connection."""
    global redis_client
    
    try:
        # Handle different Redis URL formats
        if hasattr(settings, 'redis_url') and settings.redis_url:
            redis_client = redis.from_url(
                settings.redis_url,
                encoding="utf-8",
                decode_responses=True,
                socket_connect_timeout=5,
                socket_timeout=5,
                retry_on_timeout=True,
                health_check_interval=30
            )
            # Test connection
            await redis_client.ping()
            logger.info("Redis cache initialized successfully")
        else:
            # Fallback for development without Redis
            logger.warning("Redis URL not configured, using in-memory cache fallback")
            redis_client = None
        
    except Exception as e:
        logger.error(f"Failed to initialize Redis cache: {e}")
        redis_client = None


async def close_cache() -> None:
    """Close Redis cache connection."""
    global redis_client
    
    if redis_client:
        try:
            await redis_client.close()
            logger.info("Redis cache connection closed")
        except Exception as e:
            logger.error(f"Error closing Redis cache: {e}")
        finally:
            redis_client = None


class CacheManager:
    """Cache manager for storing and retrieving data."""
    
    def __init__(self):
        self.fallback_cache: Dict[str, Any] = {}
        self.default_ttl = 3600  # 1 hour
    
    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        try:
            if redis_client:
                value = await redis_client.get(key)
                if value:
                    return json.loads(value)
            else:
                # Fallback to in-memory cache
                return self.fallback_cache.get(key)
        except Exception as e:
            logger.warning(f"Cache get error for key {key}: {e}")
        
        return None
    
    async def set(
        self, 
        key: str, 
        value: Any, 
        ttl: Optional[int] = None
    ) -> bool:
        """Set value in cache with optional TTL."""
        try:
            ttl = ttl or self.default_ttl
            
            if redis_client:
                serialized_value = json.dumps(value, default=str)
                await redis_client.setex(key, ttl, serialized_value)
                return True
            else:
                # Fallback to in-memory cache
                self.fallback_cache[key] = value
                return True
                
        except Exception as e:
            logger.warning(f"Cache set error for key {key}: {e}")
            return False
    
    async def delete(self, key: str) -> bool:
        """Delete value from cache."""
        try:
            if redis_client:
                result = await redis_client.delete(key)
                return result > 0
            else:
                # Fallback to in-memory cache
                if key in self.fallback_cache:
                    del self.fallback_cache[key]
                    return True
                return False
                
        except Exception as e:
            logger.warning(f"Cache delete error for key {key}: {e}")
            return False


# Global cache manager instance
cache = CacheManager()


async def get_cache() -> Redis:
    """Get Redis client."""
    if not redis_client:
        raise RuntimeError("Cache not initialized")
    return redis_client


async def check_cache_health() -> Dict[str, Any]:
    """Check cache health status."""
    try:
        if redis_client:
            await redis_client.ping()
            info = await redis_client.info()
            
            return {
                "healthy": True,
                "connected": True,
                "used_memory": info.get("used_memory_human", "Unknown"),
                "connected_clients": info.get("connected_clients", 0),
                "total_commands_processed": info.get("total_commands_processed", 0),
                "keyspace_hits": info.get("keyspace_hits", 0),
                "keyspace_misses": info.get("keyspace_misses", 0),
            }
        else:
            return {
                "healthy": True,
                "connected": False,
                "fallback_cache_size": len(cache.fallback_cache),
                "type": "in_memory_fallback"
            }
            
    except Exception as e:
        return {
            "healthy": False,
            "error": str(e),
            "connected": False
        }

