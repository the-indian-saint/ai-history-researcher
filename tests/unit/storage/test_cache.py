"""Unit tests for cache module."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
import json
from typing import Any, Dict

from src.ai_research_framework.storage.cache import (
    init_cache,
    close_cache,
    CacheManager,
    get_cache,
    check_cache_health,
    cache,
    redis_client
)


@pytest.mark.asyncio
class TestCacheInitialization:
    """Test cache initialization and teardown."""
    
    async def test_init_cache_with_redis_url(self):
        """Test cache initialization with Redis URL."""
        mock_redis = AsyncMock()
        mock_redis.ping = AsyncMock(return_value=True)
        
        with patch('src.ai_research_framework.storage.cache.redis.from_url', return_value=mock_redis):
            with patch('src.ai_research_framework.config.settings') as mock_settings:
                mock_settings.redis_url = "redis://localhost:6379"
                
                await init_cache()
                
                # Verify Redis client was created and pinged
                mock_redis.ping.assert_called_once()
    
    async def test_init_cache_without_redis_url(self):
        """Test cache initialization without Redis URL (fallback mode)."""
        with patch('src.ai_research_framework.config.settings') as mock_settings:
            mock_settings.redis_url = None
            
            await init_cache()
            
            # Should use in-memory fallback
            assert redis_client is None
    
    async def test_init_cache_redis_connection_failure(self):
        """Test cache initialization when Redis connection fails."""
        mock_redis = AsyncMock()
        mock_redis.ping.side_effect = Exception("Connection refused")
        
        with patch('src.ai_research_framework.storage.cache.redis.from_url', return_value=mock_redis):
            with patch('src.ai_research_framework.config.settings') as mock_settings:
                mock_settings.redis_url = "redis://localhost:6379"
                
                await init_cache()
                
                # Should fallback to None on connection failure
                assert redis_client is None
    
    async def test_close_cache_with_redis(self):
        """Test closing cache with active Redis connection."""
        mock_redis = AsyncMock()
        
        with patch('src.ai_research_framework.storage.cache.redis_client', mock_redis):
            await close_cache()
            
            mock_redis.close.assert_called_once()
    
    async def test_close_cache_without_redis(self):
        """Test closing cache without Redis connection."""
        with patch('src.ai_research_framework.storage.cache.redis_client', None):
            # Should not raise any errors
            await close_cache()


@pytest.mark.asyncio
class TestCacheManager:
    """Test CacheManager class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.cache_manager = CacheManager()
    
    async def test_get_with_redis(self):
        """Test getting value from Redis cache."""
        mock_redis = AsyncMock()
        mock_redis.get.return_value = json.dumps({"test": "data"})
        
        with patch('src.ai_research_framework.storage.cache.redis_client', mock_redis):
            result = await self.cache_manager.get("test_key")
            
            assert result == {"test": "data"}
            mock_redis.get.assert_called_once_with("test_key")
    
    async def test_get_with_fallback(self):
        """Test getting value from fallback cache."""
        self.cache_manager.fallback_cache["test_key"] = {"test": "data"}
        
        with patch('src.ai_research_framework.storage.cache.redis_client', None):
            result = await self.cache_manager.get("test_key")
            
            assert result == {"test": "data"}
    
    async def test_get_nonexistent_key(self):
        """Test getting non-existent key."""
        mock_redis = AsyncMock()
        mock_redis.get.return_value = None
        
        with patch('src.ai_research_framework.storage.cache.redis_client', mock_redis):
            result = await self.cache_manager.get("nonexistent")
            
            assert result is None
    
    async def test_get_with_redis_error(self):
        """Test getting value when Redis raises error."""
        mock_redis = AsyncMock()
        mock_redis.get.side_effect = Exception("Redis error")
        
        with patch('src.ai_research_framework.storage.cache.redis_client', mock_redis):
            result = await self.cache_manager.get("test_key")
            
            # Should return None on error
            assert result is None
    
    async def test_set_with_redis(self):
        """Test setting value in Redis cache."""
        mock_redis = AsyncMock()
        mock_redis.setex.return_value = True
        
        test_data = {"test": "data"}
        
        with patch('src.ai_research_framework.storage.cache.redis_client', mock_redis):
            result = await self.cache_manager.set("test_key", test_data, ttl=300)
            
            assert result is True
            mock_redis.setex.assert_called_once_with(
                "test_key",
                300,
                json.dumps(test_data, default=str)
            )
    
    async def test_set_with_default_ttl(self):
        """Test setting value with default TTL."""
        mock_redis = AsyncMock()
        mock_redis.setex.return_value = True
        
        with patch('src.ai_research_framework.storage.cache.redis_client', mock_redis):
            result = await self.cache_manager.set("test_key", {"data": "test"})
            
            assert result is True
            # Should use default TTL (3600)
            mock_redis.setex.assert_called_once_with(
                "test_key",
                3600,
                json.dumps({"data": "test"}, default=str)
            )
    
    async def test_set_with_fallback(self):
        """Test setting value in fallback cache."""
        test_data = {"test": "data"}
        
        with patch('src.ai_research_framework.storage.cache.redis_client', None):
            result = await self.cache_manager.set("test_key", test_data)
            
            assert result is True
            assert self.cache_manager.fallback_cache["test_key"] == test_data
    
    async def test_set_with_redis_error(self):
        """Test setting value when Redis raises error."""
        mock_redis = AsyncMock()
        mock_redis.setex.side_effect = Exception("Redis error")
        
        with patch('src.ai_research_framework.storage.cache.redis_client', mock_redis):
            result = await self.cache_manager.set("test_key", {"data": "test"})
            
            # Should return False on error
            assert result is False
    
    async def test_delete_with_redis(self):
        """Test deleting value from Redis cache."""
        mock_redis = AsyncMock()
        mock_redis.delete.return_value = 1  # Number of keys deleted
        
        with patch('src.ai_research_framework.storage.cache.redis_client', mock_redis):
            result = await self.cache_manager.delete("test_key")
            
            assert result is True
            mock_redis.delete.assert_called_once_with("test_key")
    
    async def test_delete_nonexistent_key_redis(self):
        """Test deleting non-existent key from Redis."""
        mock_redis = AsyncMock()
        mock_redis.delete.return_value = 0  # No keys deleted
        
        with patch('src.ai_research_framework.storage.cache.redis_client', mock_redis):
            result = await self.cache_manager.delete("nonexistent")
            
            assert result is False
    
    async def test_delete_with_fallback(self):
        """Test deleting value from fallback cache."""
        self.cache_manager.fallback_cache["test_key"] = {"test": "data"}
        
        with patch('src.ai_research_framework.storage.cache.redis_client', None):
            result = await self.cache_manager.delete("test_key")
            
            assert result is True
            assert "test_key" not in self.cache_manager.fallback_cache
    
    async def test_delete_nonexistent_key_fallback(self):
        """Test deleting non-existent key from fallback cache."""
        with patch('src.ai_research_framework.storage.cache.redis_client', None):
            result = await self.cache_manager.delete("nonexistent")
            
            assert result is False
    
    async def test_delete_with_redis_error(self):
        """Test deleting value when Redis raises error."""
        mock_redis = AsyncMock()
        mock_redis.delete.side_effect = Exception("Redis error")
        
        with patch('src.ai_research_framework.storage.cache.redis_client', mock_redis):
            result = await self.cache_manager.delete("test_key")
            
            # Should return False on error
            assert result is False


@pytest.mark.asyncio
class TestGetCache:
    """Test get_cache function."""
    
    async def test_get_cache_with_redis(self):
        """Test getting Redis client when available."""
        mock_redis = AsyncMock()
        
        with patch('src.ai_research_framework.storage.cache.redis_client', mock_redis):
            result = await get_cache()
            
            assert result == mock_redis
    
    async def test_get_cache_without_redis(self):
        """Test getting Redis client when not initialized."""
        with patch('src.ai_research_framework.storage.cache.redis_client', None):
            with pytest.raises(RuntimeError, match="Cache not initialized"):
                await get_cache()


@pytest.mark.asyncio
class TestCacheHealth:
    """Test cache health check."""
    
    async def test_check_cache_health_with_redis(self):
        """Test cache health check with Redis connected."""
        mock_redis = AsyncMock()
        mock_redis.ping.return_value = True
        mock_redis.info.return_value = {
            "used_memory_human": "10MB",
            "connected_clients": 5,
            "total_commands_processed": 1000,
            "keyspace_hits": 800,
            "keyspace_misses": 200
        }
        
        with patch('src.ai_research_framework.storage.cache.redis_client', mock_redis):
            result = await check_cache_health()
            
            assert result["healthy"] is True
            assert result["connected"] is True
            assert result["used_memory"] == "10MB"
            assert result["connected_clients"] == 5
            assert result["total_commands_processed"] == 1000
            assert result["keyspace_hits"] == 800
            assert result["keyspace_misses"] == 200
    
    async def test_check_cache_health_with_fallback(self):
        """Test cache health check with fallback cache."""
        # Create a cache manager with some items
        test_cache = CacheManager()
        test_cache.fallback_cache = {"key1": "val1", "key2": "val2"}
        
        with patch('src.ai_research_framework.storage.cache.redis_client', None):
            with patch('src.ai_research_framework.storage.cache.cache', test_cache):
                result = await check_cache_health()
                
                assert result["healthy"] is True
                assert result["connected"] is False
                assert result["fallback_cache_size"] == 2
                assert result["type"] == "in_memory_fallback"
    
    async def test_check_cache_health_redis_error(self):
        """Test cache health check when Redis raises error."""
        mock_redis = AsyncMock()
        mock_redis.ping.side_effect = Exception("Connection error")
        
        with patch('src.ai_research_framework.storage.cache.redis_client', mock_redis):
            result = await check_cache_health()
            
            assert result["healthy"] is False
            assert result["connected"] is False
            assert "error" in result


class TestCacheManagerSerialization:
    """Test CacheManager serialization/deserialization."""
    
    @pytest.mark.asyncio
    async def test_set_with_complex_object(self):
        """Test setting complex object in cache."""
        cache_manager = CacheManager()
        mock_redis = AsyncMock()
        mock_redis.setex.return_value = True
        
        complex_data = {
            "id": 123,
            "name": "Test",
            "nested": {
                "list": [1, 2, 3],
                "date": "2024-01-01"
            },
            "none_value": None
        }
        
        with patch('src.ai_research_framework.storage.cache.redis_client', mock_redis):
            result = await cache_manager.set("complex_key", complex_data)
            
            assert result is True
            # Verify JSON serialization was called
            mock_redis.setex.assert_called_once()
            call_args = mock_redis.setex.call_args[0]
            assert call_args[0] == "complex_key"
            assert json.loads(call_args[2]) == complex_data
    
    @pytest.mark.asyncio
    async def test_get_with_json_parsing(self):
        """Test getting value with JSON parsing."""
        cache_manager = CacheManager()
        mock_redis = AsyncMock()
        
        test_data = {"test": "data", "number": 42}
        mock_redis.get.return_value = json.dumps(test_data)
        
        with patch('src.ai_research_framework.storage.cache.redis_client', mock_redis):
            result = await cache_manager.get("test_key")
            
            assert result == test_data
            assert isinstance(result["number"], int)


class TestCachePatterns:
    """Test common cache patterns."""
    
    @pytest.mark.asyncio
    async def test_cache_aside_pattern(self):
        """Test cache-aside pattern implementation."""
        cache_manager = CacheManager()
        mock_redis = AsyncMock()
        
        # Simulate cache miss
        mock_redis.get.return_value = None
        
        with patch('src.ai_research_framework.storage.cache.redis_client', mock_redis):
            # Cache miss
            cached_value = await cache_manager.get("user:123")
            assert cached_value is None
            
            # Load from database (simulated)
            db_value = {"id": 123, "name": "Test User"}
            
            # Store in cache
            await cache_manager.set("user:123", db_value, ttl=300)
            
            # Verify stored
            mock_redis.setex.assert_called_once_with(
                "user:123",
                300,
                json.dumps(db_value, default=str)
            )
    
    @pytest.mark.asyncio
    async def test_cache_invalidation(self):
        """Test cache invalidation pattern."""
        cache_manager = CacheManager()
        mock_redis = AsyncMock()
        mock_redis.delete.return_value = 1
        
        with patch('src.ai_research_framework.storage.cache.redis_client', mock_redis):
            # Invalidate cache entry
            result = await cache_manager.delete("user:123")
            
            assert result is True
            mock_redis.delete.assert_called_once_with("user:123")


@pytest.mark.asyncio
class TestCacheIntegration:
    """Integration tests for cache module."""
    
    async def test_global_cache_instance(self):
        """Test that global cache instance works correctly."""
        from src.ai_research_framework.storage.cache import cache
        
        assert isinstance(cache, CacheManager)
        assert hasattr(cache, 'get')
        assert hasattr(cache, 'set')
        assert hasattr(cache, 'delete')
        assert hasattr(cache, 'fallback_cache')
    
    async def test_cache_operations_without_redis(self):
        """Test complete cache operations without Redis."""
        cache_manager = CacheManager()
        
        with patch('src.ai_research_framework.storage.cache.redis_client', None):
            # Test set
            assert await cache_manager.set("key1", {"data": 1}) is True
            
            # Test get
            assert await cache_manager.get("key1") == {"data": 1}
            
            # Test delete
            assert await cache_manager.delete("key1") is True
            
            # Verify deleted
            assert await cache_manager.get("key1") is None
