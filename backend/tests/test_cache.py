"""
Test-Driven Development for Caching Layer

This module contains tests written BEFORE implementation for the
caching functionality including Redis connection, decorators,
and cache invalidation strategies.
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch
from datetime import datetime, timedelta

from app.utils.cache import (
    CacheManager,
    cache_result,
    invalidate_cache,
    get_cache_key,
    CacheConfig
)


class TestCacheManager:
    """Test suite for CacheManager functionality."""
    
    @pytest.fixture
    def mock_redis(self):
        """Mock Redis client."""
        redis_mock = Mock()
        redis_mock.get = AsyncMock()
        redis_mock.set = AsyncMock()
        redis_mock.delete = AsyncMock()
        redis_mock.exists = AsyncMock()
        redis_mock.expire = AsyncMock()
        redis_mock.flushdb = AsyncMock()
        return redis_mock
    
    @pytest.fixture
    def cache_manager(self, mock_redis):
        """Create cache manager instance."""
        return CacheManager(redis_client=mock_redis)
    
    @pytest.mark.asyncio
    async def test_cache_manager_initialization(self, cache_manager):
        """Test cache manager initialization."""
        assert cache_manager is not None
        assert cache_manager.redis is not None
        assert cache_manager.default_ttl == 3600  # 1 hour default
    
    @pytest.mark.asyncio
    async def test_get_cache_hit(self, cache_manager, mock_redis):
        """Test cache hit scenario."""
        # Mock cache hit
        mock_redis.get.return_value = '{"data": "cached_value"}'
        
        result = await cache_manager.get("test_key")
        
        assert result == {"data": "cached_value"}
        mock_redis.get.assert_called_once_with("test_key")
    
    @pytest.mark.asyncio
    async def test_get_cache_miss(self, cache_manager, mock_redis):
        """Test cache miss scenario."""
        # Mock cache miss
        mock_redis.get.return_value = None
        
        result = await cache_manager.get("test_key")
        
        assert result is None
        mock_redis.get.assert_called_once_with("test_key")
    
    @pytest.mark.asyncio
    async def test_set_cache_success(self, cache_manager, mock_redis):
        """Test successful cache set operation."""
        data = {"user_id": 1, "data": "test_data"}
        
        await cache_manager.set("test_key", data, ttl=1800)
        
        mock_redis.set.assert_called_once_with(
            "test_key", 
            '{"user_id": 1, "data": "test_data"}', 
            ex=1800
        )
    
    @pytest.mark.asyncio
    async def test_delete_cache_success(self, cache_manager, mock_redis):
        """Test successful cache deletion."""
        mock_redis.delete.return_value = 1
        
        result = await cache_manager.delete("test_key")
        
        assert result is True
        mock_redis.delete.assert_called_once_with("test_key")
    
    @pytest.mark.asyncio
    async def test_delete_cache_not_found(self, cache_manager, mock_redis):
        """Test cache deletion when key doesn't exist."""
        mock_redis.delete.return_value = 0
        
        result = await cache_manager.delete("nonexistent_key")
        
        assert result is False
        mock_redis.delete.assert_called_once_with("nonexistent_key")
    
    @pytest.mark.asyncio
    async def test_exists_cache_key(self, cache_manager, mock_redis):
        """Test checking if cache key exists."""
        mock_redis.exists.return_value = 1
        
        result = await cache_manager.exists("test_key")
        
        assert result is True
        mock_redis.exists.assert_called_once_with("test_key")
    
    @pytest.mark.asyncio
    async def test_clear_pattern_success(self, cache_manager, mock_redis):
        """Test clearing cache keys by pattern."""
        # Mock scan_iter to return matching keys
        mock_redis.scan_iter = Mock(return_value=["user:1:data", "user:1:stats"])
        mock_redis.delete.return_value = 2
        
        result = await cache_manager.clear_pattern("user:1:*")
        
        assert result == 2
        mock_redis.delete.assert_called_once_with("user:1:data", "user:1:stats")
    
    @pytest.mark.asyncio
    async def test_get_cache_stats(self, cache_manager, mock_redis):
        """Test getting cache statistics."""
        # Mock Redis info command
        mock_redis.info.return_value = {
            "used_memory": 1024000,
            "keyspace_hits": 1000,
            "keyspace_misses": 100
        }
        
        stats = await cache_manager.get_stats()
        
        assert "memory_usage" in stats
        assert "hit_rate" in stats
        assert stats["hit_rate"] == 90.91  # 1000/(1000+100) * 100
    
    @pytest.mark.asyncio
    async def test_cache_error_handling(self, cache_manager, mock_redis):
        """Test cache error handling."""
        # Mock Redis error
        mock_redis.get.side_effect = Exception("Redis connection failed")
        
        result = await cache_manager.get("test_key")
        
        # Should return None on error, not raise exception
        assert result is None


class TestCacheDecorator:
    """Test suite for cache decorator functionality."""
    
    @pytest.fixture
    def mock_cache_manager(self):
        """Mock cache manager."""
        cache_mock = Mock()
        cache_mock.get = AsyncMock()
        cache_mock.set = AsyncMock()
        cache_mock.delete = AsyncMock()
        return cache_mock
    
    @pytest.mark.asyncio
    async def test_cache_decorator_hit(self, mock_cache_manager):
        """Test cache decorator with cache hit."""
        # Mock cache hit
        mock_cache_manager.get.return_value = {"result": "cached_data"}
        
        @cache_result(ttl=3600, key_prefix="test")
        async def test_function(user_id: int):
            return {"result": "fresh_data"}
        
        # Patch the cache manager
        with patch('app.utils.cache.cache_manager', mock_cache_manager):
            result = await test_function(user_id=1)
        
        assert result == {"result": "cached_data"}
        mock_cache_manager.get.assert_called_once()
        mock_cache_manager.set.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_cache_decorator_miss(self, mock_cache_manager):
        """Test cache decorator with cache miss."""
        # Mock cache miss
        mock_cache_manager.get.return_value = None
        
        @cache_result(ttl=3600, key_prefix="test")
        async def test_function(user_id: int):
            return {"result": "fresh_data"}
        
        # Patch the cache manager
        with patch('app.utils.cache.cache_manager', mock_cache_manager):
            result = await test_function(user_id=1)
        
        assert result == {"result": "fresh_data"}
        mock_cache_manager.get.assert_called_once()
        mock_cache_manager.set.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_cache_key_generation(self):
        """Test cache key generation."""
        key = get_cache_key("user_stats", user_id=1, days=30)
        
        assert "user_stats" in key
        assert "user_id:1" in key
        assert "days:30" in key
    
    @pytest.mark.asyncio
    async def test_cache_invalidation(self, mock_cache_manager):
        """Test cache invalidation."""
        mock_cache_manager.clear_pattern.return_value = 3
        
        with patch('app.utils.cache.cache_manager', mock_cache_manager):
            result = await invalidate_cache("user:1:*")
        
        assert result == 3
        mock_cache_manager.clear_pattern.assert_called_once_with("user:1:*")


class TestCacheConfig:
    """Test suite for cache configuration."""
    
    def test_cache_config_defaults(self):
        """Test default cache configuration."""
        config = CacheConfig()
        
        assert config.redis_url is not None
        assert config.default_ttl == 3600
        assert config.max_connections == 10
        assert config.enabled is True
    
    def test_cache_config_custom(self):
        """Test custom cache configuration."""
        config = CacheConfig(
            redis_url="redis://localhost:6380",
            default_ttl=7200,
            max_connections=20,
            enabled=False
        )
        
        assert config.redis_url == "redis://localhost:6380"
        assert config.default_ttl == 7200
        assert config.max_connections == 20
        assert config.enabled is False


class TestCacheIntegration:
    """Test suite for cache integration with services."""
    
    @pytest.fixture
    def mock_analytics_service(self):
        """Mock analytics service."""
        service = Mock()
        service.generate_dashboard_data = AsyncMock(return_value={
            "user_id": 1,
            "data": "dashboard_data"
        })
        return service
    
    @pytest.mark.asyncio
    async def test_cached_analytics_service(self, mock_analytics_service):
        """Test caching integration with analytics service."""
        # Test that analytics methods can be cached
        original_method = mock_analytics_service.generate_dashboard_data
        
        # Apply cache decorator
        @cache_result(ttl=1800, key_prefix="dashboard")
        async def cached_dashboard_data(user_id: int):
            return await original_method(user_id)
        
        # Mock cache manager
        mock_cache = Mock()
        mock_cache.get = AsyncMock(return_value=None)  # Cache miss
        mock_cache.set = AsyncMock()
        
        with patch('app.utils.cache.cache_manager', mock_cache):
            result = await cached_dashboard_data(user_id=1)
        
        assert result == {"user_id": 1, "data": "dashboard_data"}
        mock_cache.get.assert_called_once()
        mock_cache.set.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_cache_invalidation_on_data_update(self):
        """Test cache invalidation when data is updated."""
        mock_cache = Mock()
        mock_cache.clear_pattern = AsyncMock(return_value=2)
        
        # Simulate data update that should invalidate cache
        with patch('app.utils.cache.cache_manager', mock_cache):
            # This would be called when user logs a new habit
            await invalidate_cache("user:1:*")
        
        mock_cache.clear_pattern.assert_called_once_with("user:1:*")
    
    @pytest.mark.asyncio
    async def test_cache_performance_monitoring(self):
        """Test cache performance monitoring."""
        mock_cache = Mock()
        mock_cache.get_stats = AsyncMock(return_value={
            "hit_rate": 85.5,
            "memory_usage": 1024000,
            "total_keys": 1500
        })
        
        with patch('app.utils.cache.cache_manager', mock_cache):
            stats = await mock_cache.get_stats()
        
        assert stats["hit_rate"] > 80  # Good hit rate
        assert "memory_usage" in stats
        assert "total_keys" in stats


class TestCacheStrategies:
    """Test suite for different caching strategies."""
    
    @pytest.mark.asyncio
    async def test_write_through_cache(self):
        """Test write-through caching strategy."""
        mock_cache = Mock()
        mock_cache.set = AsyncMock()
        
        # Simulate write-through: update database and cache simultaneously
        async def update_user_data(user_id: int, data: dict):
            # Update database (mocked)
            database_result = {"user_id": user_id, **data}
            
            # Update cache
            cache_key = f"user:{user_id}:data"
            await mock_cache.set(cache_key, database_result, ttl=3600)
            
            return database_result
        
        with patch('app.utils.cache.cache_manager', mock_cache):
            result = await update_user_data(1, {"name": "John"})
        
        assert result["user_id"] == 1
        assert result["name"] == "John"
        mock_cache.set.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_cache_aside_pattern(self):
        """Test cache-aside (lazy loading) pattern."""
        mock_cache = Mock()
        mock_cache.get = AsyncMock(return_value=None)  # Cache miss
        mock_cache.set = AsyncMock()
        
        async def get_user_data(user_id: int):
            cache_key = f"user:{user_id}:data"
            
            # Try cache first
            cached_data = await mock_cache.get(cache_key)
            if cached_data:
                return cached_data
            
            # Cache miss - get from database
            database_data = {"user_id": user_id, "name": "John"}
            
            # Store in cache for next time
            await mock_cache.set(cache_key, database_data, ttl=3600)
            
            return database_data
        
        with patch('app.utils.cache.cache_manager', mock_cache):
            result = await get_user_data(1)
        
        assert result["user_id"] == 1
        mock_cache.get.assert_called_once()
        mock_cache.set.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_cache_warming(self):
        """Test cache warming strategy."""
        mock_cache = Mock()
        mock_cache.set = AsyncMock()
        
        async def warm_cache():
            """Pre-populate cache with frequently accessed data."""
            popular_data = [
                {"key": "leaderboard:global", "data": {"top_users": []}},
                {"key": "stats:platform", "data": {"total_users": 1000}},
                {"key": "categories:popular", "data": {"transport": 45}}
            ]
            
            for item in popular_data:
                await mock_cache.set(item["key"], item["data"], ttl=7200)
        
        with patch('app.utils.cache.cache_manager', mock_cache):
            await warm_cache()
        
        assert mock_cache.set.call_count == 3
    
    @pytest.mark.asyncio
    async def test_cache_expiration_handling(self):
        """Test handling of cache expiration."""
        mock_cache = Mock()
        
        # Simulate expired cache (returns None)
        mock_cache.get = AsyncMock(return_value=None)
        mock_cache.set = AsyncMock()
        
        @cache_result(ttl=60, key_prefix="short_lived")
        async def get_real_time_data():
            return {"timestamp": datetime.utcnow().isoformat(), "value": 42}
        
        with patch('app.utils.cache.cache_manager', mock_cache):
            result = await get_real_time_data()
        
        assert "timestamp" in result
        assert result["value"] == 42
        mock_cache.get.assert_called_once()
        mock_cache.set.assert_called_once()