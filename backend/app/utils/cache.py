"""
Caching Layer - Task 9.2 Implementation

This module provides comprehensive caching functionality including
Redis connection management, caching decorators, cache invalidation
strategies, and performance monitoring.
"""

import json
import logging
import hashlib
from typing import Any, Dict, Optional, List, Callable, Union
from datetime import datetime, timedelta
from functools import wraps
import asyncio

import redis.asyncio as redis
from pydantic import BaseModel

from app.core.config import settings

logger = logging.getLogger(__name__)


class CacheConfig(BaseModel):
    """Configuration for caching system."""
    redis_url: str = "redis://localhost:6379"
    default_ttl: int = 3600  # 1 hour
    max_connections: int = 10
    enabled: bool = True
    key_prefix: str = "klymate:"
    
    class Config:
        env_prefix = "CACHE_"


class CacheManager:
    """
    Redis-based cache manager with comprehensive functionality.
    
    Provides async Redis operations, error handling, and performance monitoring.
    """
    
    def __init__(self, redis_client: Optional[redis.Redis] = None, config: Optional[CacheConfig] = None):
        """
        Initialize cache manager.
        
        Args:
            redis_client: Optional Redis client instance
            config: Optional cache configuration
        """
        self.config = config or CacheConfig()
        self.redis = redis_client
        self.default_ttl = self.config.default_ttl
        self._stats = {
            "hits": 0,
            "misses": 0,
            "errors": 0,
            "sets": 0,
            "deletes": 0
        }
        
        if not self.redis and self.config.enabled:
            self._initialize_redis()
        
        logger.info("Cache Manager initialized")
    
    def _initialize_redis(self):
        """Initialize Redis connection."""
        try:
            self.redis = redis.from_url(
                self.config.redis_url,
                max_connections=self.config.max_connections,
                decode_responses=True
            )
            logger.info(f"Redis connection initialized: {self.config.redis_url}")
        except Exception as e:
            logger.error(f"Failed to initialize Redis: {str(e)}")
            self.redis = None
    
    async def get(self, key: str) -> Optional[Any]:
        """
        Get value from cache.
        
        Args:
            key: Cache key
            
        Returns:
            Cached value or None if not found/error
        """
        if not self.config.enabled or not self.redis:
            return None
        
        try:
            full_key = f"{self.config.key_prefix}{key}"
            value = await self.redis.get(full_key)
            
            if value is not None:
                self._stats["hits"] += 1
                logger.debug(f"Cache hit: {key}")
                return json.loads(value)
            else:
                self._stats["misses"] += 1
                logger.debug(f"Cache miss: {key}")
                return None
                
        except Exception as e:
            self._stats["errors"] += 1
            logger.error(f"Cache get error for key {key}: {str(e)}")
            return None
    
    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """
        Set value in cache.
        
        Args:
            key: Cache key
            value: Value to cache
            ttl: Time to live in seconds
            
        Returns:
            True if successful, False otherwise
        """
        if not self.config.enabled or not self.redis:
            return False
        
        try:
            full_key = f"{self.config.key_prefix}{key}"
            ttl = ttl or self.default_ttl
            
            serialized_value = json.dumps(value, default=str)
            await self.redis.set(full_key, serialized_value, ex=ttl)
            
            self._stats["sets"] += 1
            logger.debug(f"Cache set: {key} (TTL: {ttl}s)")
            return True
            
        except Exception as e:
            self._stats["errors"] += 1
            logger.error(f"Cache set error for key {key}: {str(e)}")
            return False
    
    async def delete(self, key: str) -> bool:
        """
        Delete key from cache.
        
        Args:
            key: Cache key to delete
            
        Returns:
            True if key was deleted, False otherwise
        """
        if not self.config.enabled or not self.redis:
            return False
        
        try:
            full_key = f"{self.config.key_prefix}{key}"
            result = await self.redis.delete(full_key)
            
            if result > 0:
                self._stats["deletes"] += 1
                logger.debug(f"Cache delete: {key}")
                return True
            else:
                logger.debug(f"Cache delete failed (key not found): {key}")
                return False
                
        except Exception as e:
            self._stats["errors"] += 1
            logger.error(f"Cache delete error for key {key}: {str(e)}")
            return False
    
    async def exists(self, key: str) -> bool:
        """
        Check if key exists in cache.
        
        Args:
            key: Cache key to check
            
        Returns:
            True if key exists, False otherwise
        """
        if not self.config.enabled or not self.redis:
            return False
        
        try:
            full_key = f"{self.config.key_prefix}{key}"
            result = await self.redis.exists(full_key)
            return result > 0
            
        except Exception as e:
            logger.error(f"Cache exists error for key {key}: {str(e)}")
            return False
    
    async def clear_pattern(self, pattern: str) -> int:
        """
        Clear all keys matching a pattern.
        
        Args:
            pattern: Pattern to match (e.g., "user:*")
            
        Returns:
            Number of keys deleted
        """
        if not self.config.enabled or not self.redis:
            return 0
        
        try:
            full_pattern = f"{self.config.key_prefix}{pattern}"
            keys = []
            
            # Use scan_iter to get matching keys
            async for key in self.redis.scan_iter(match=full_pattern):
                keys.append(key)
            
            if keys:
                deleted = await self.redis.delete(*keys)
                logger.info(f"Cleared {deleted} cache keys matching pattern: {pattern}")
                return deleted
            else:
                logger.debug(f"No keys found matching pattern: {pattern}")
                return 0
                
        except Exception as e:
            self._stats["errors"] += 1
            logger.error(f"Cache clear pattern error for {pattern}: {str(e)}")
            return 0
    
    async def get_stats(self) -> Dict[str, Any]:
        """
        Get cache performance statistics.
        
        Returns:
            Dictionary containing cache statistics
        """
        try:
            total_requests = self._stats["hits"] + self._stats["misses"]
            hit_rate = (self._stats["hits"] / total_requests * 100) if total_requests > 0 else 0
            
            stats = {
                "hit_rate": round(hit_rate, 2),
                "total_requests": total_requests,
                "hits": self._stats["hits"],
                "misses": self._stats["misses"],
                "errors": self._stats["errors"],
                "sets": self._stats["sets"],
                "deletes": self._stats["deletes"],
                "enabled": self.config.enabled
            }
            
            # Add Redis info if available
            if self.redis:
                try:
                    redis_info = await self.redis.info()
                    stats.update({
                        "memory_usage": redis_info.get("used_memory", 0),
                        "connected_clients": redis_info.get("connected_clients", 0),
                        "keyspace_hits": redis_info.get("keyspace_hits", 0),
                        "keyspace_misses": redis_info.get("keyspace_misses", 0)
                    })
                except Exception as e:
                    logger.warning(f"Could not get Redis info: {str(e)}")
            
            return stats
            
        except Exception as e:
            logger.error(f"Error getting cache stats: {str(e)}")
            return {"error": str(e)}
    
    async def health_check(self) -> Dict[str, Any]:
        """
        Perform cache health check.
        
        Returns:
            Health check results
        """
        try:
            if not self.config.enabled:
                return {"status": "disabled", "message": "Caching is disabled"}
            
            if not self.redis:
                return {"status": "error", "message": "Redis client not initialized"}
            
            # Test Redis connection
            test_key = f"health_check_{datetime.utcnow().timestamp()}"
            test_value = {"test": True, "timestamp": datetime.utcnow().isoformat()}
            
            # Test set
            await self.set(test_key, test_value, ttl=60)
            
            # Test get
            retrieved = await self.get(test_key)
            
            # Test delete
            await self.delete(test_key)
            
            if retrieved and retrieved.get("test") is True:
                return {
                    "status": "healthy",
                    "message": "Cache is working properly",
                    "redis_connected": True
                }
            else:
                return {
                    "status": "error",
                    "message": "Cache test failed",
                    "redis_connected": False
                }
                
        except Exception as e:
            return {
                "status": "error",
                "message": f"Health check failed: {str(e)}",
                "redis_connected": False
            }
    
    async def close(self):
        """Close Redis connection."""
        if self.redis:
            await self.redis.close()
            logger.info("Redis connection closed")


# Global cache manager instance
cache_manager = CacheManager()


def get_cache_key(prefix: str, **kwargs) -> str:
    """
    Generate cache key from prefix and parameters.
    
    Args:
        prefix: Key prefix
        **kwargs: Key parameters
        
    Returns:
        Generated cache key
    """
    try:
        # Sort parameters for consistent key generation
        sorted_params = sorted(kwargs.items())
        param_string = ":".join([f"{k}:{v}" for k, v in sorted_params])
        
        if param_string:
            return f"{prefix}:{param_string}"
        else:
            return prefix
            
    except Exception as e:
        logger.error(f"Error generating cache key: {str(e)}")
        # Fallback to simple key
        return f"{prefix}:{hash(str(kwargs))}"


def cache_result(ttl: int = 3600, key_prefix: str = "default"):
    """
    Decorator to cache function results.
    
    Args:
        ttl: Time to live in seconds
        key_prefix: Cache key prefix
        
    Returns:
        Decorated function
    """
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            try:
                # Generate cache key from function arguments
                func_name = f"{func.__module__}.{func.__name__}"
                
                # Create key from function arguments
                key_parts = [key_prefix, func_name]
                
                # Add positional arguments
                if args:
                    key_parts.extend([str(arg) for arg in args])
                
                # Add keyword arguments
                if kwargs:
                    sorted_kwargs = sorted(kwargs.items())
                    key_parts.extend([f"{k}:{v}" for k, v in sorted_kwargs])
                
                cache_key = ":".join(key_parts)
                
                # Try to get from cache
                cached_result = await cache_manager.get(cache_key)
                if cached_result is not None:
                    logger.debug(f"Cache hit for {func_name}")
                    return cached_result
                
                # Cache miss - execute function
                logger.debug(f"Cache miss for {func_name}")
                result = await func(*args, **kwargs)
                
                # Store result in cache
                await cache_manager.set(cache_key, result, ttl=ttl)
                
                return result
                
            except Exception as e:
                logger.error(f"Cache decorator error for {func.__name__}: {str(e)}")
                # Execute function without caching on error
                return await func(*args, **kwargs)
        
        return wrapper
    return decorator


async def invalidate_cache(pattern: str) -> int:
    """
    Invalidate cache keys matching a pattern.
    
    Args:
        pattern: Pattern to match for invalidation
        
    Returns:
        Number of keys invalidated
    """
    try:
        return await cache_manager.clear_pattern(pattern)
    except Exception as e:
        logger.error(f"Cache invalidation error for pattern {pattern}: {str(e)}")
        return 0


class CacheInvalidationStrategy:
    """
    Strategies for cache invalidation based on data changes.
    """
    
    @staticmethod
    async def invalidate_user_cache(user_id: int):
        """Invalidate all cache entries for a specific user."""
        patterns = [
            f"user:{user_id}:*",
            f"dashboard:*:user_id:{user_id}",
            f"analytics:*:user_id:{user_id}",
            f"trends:*:user_id:{user_id}"
        ]
        
        total_invalidated = 0
        for pattern in patterns:
            count = await invalidate_cache(pattern)
            total_invalidated += count
        
        logger.info(f"Invalidated {total_invalidated} cache entries for user {user_id}")
        return total_invalidated
    
    @staticmethod
    async def invalidate_leaderboard_cache():
        """Invalidate leaderboard-related cache entries."""
        patterns = [
            "leaderboard:*",
            "platform_stats:*",
            "top_users:*"
        ]
        
        total_invalidated = 0
        for pattern in patterns:
            count = await invalidate_cache(pattern)
            total_invalidated += count
        
        logger.info(f"Invalidated {total_invalidated} leaderboard cache entries")
        return total_invalidated
    
    @staticmethod
    async def invalidate_analytics_cache():
        """Invalidate analytics-related cache entries."""
        patterns = [
            "analytics:*",
            "trends:*",
            "dashboard:*",
            "performance:*"
        ]
        
        total_invalidated = 0
        for pattern in patterns:
            count = await invalidate_cache(pattern)
            total_invalidated += count
        
        logger.info(f"Invalidated {total_invalidated} analytics cache entries")
        return total_invalidated


class CacheWarmer:
    """
    Cache warming strategies to pre-populate frequently accessed data.
    """
    
    def __init__(self, cache_manager: CacheManager):
        """Initialize cache warmer."""
        self.cache_manager = cache_manager
    
    async def warm_popular_data(self):
        """Warm cache with popular/frequently accessed data."""
        try:
            # This would be called during application startup
            # or periodically to ensure hot data is cached
            
            warming_tasks = [
                self._warm_platform_stats(),
                self._warm_popular_categories(),
                self._warm_leaderboard_data()
            ]
            
            await asyncio.gather(*warming_tasks, return_exceptions=True)
            logger.info("Cache warming completed")
            
        except Exception as e:
            logger.error(f"Cache warming error: {str(e)}")
    
    async def _warm_platform_stats(self):
        """Warm platform statistics cache."""
        try:
            # Mock platform stats - in real implementation, 
            # this would fetch from analytics service
            stats = {
                "total_users": 1000,
                "total_habits": 25000,
                "total_co2_saved": 50000.0,
                "generated_at": datetime.utcnow().isoformat()
            }
            
            await self.cache_manager.set("platform_stats:global", stats, ttl=7200)
            logger.debug("Warmed platform stats cache")
            
        except Exception as e:
            logger.error(f"Error warming platform stats: {str(e)}")
    
    async def _warm_popular_categories(self):
        """Warm popular categories cache."""
        try:
            # Mock popular categories
            categories = {
                "transport": {"count": 15000, "co2_saved": 30000},
                "energy": {"count": 8000, "co2_saved": 15000},
                "diet": {"count": 2000, "co2_saved": 5000}
            }
            
            await self.cache_manager.set("categories:popular", categories, ttl=3600)
            logger.debug("Warmed popular categories cache")
            
        except Exception as e:
            logger.error(f"Error warming categories: {str(e)}")
    
    async def _warm_leaderboard_data(self):
        """Warm leaderboard cache."""
        try:
            # Mock leaderboard data
            leaderboard = {
                "top_users": [
                    {"user_id": 1, "eco_score": 1000, "rank": 1},
                    {"user_id": 2, "eco_score": 950, "rank": 2},
                    {"user_id": 3, "eco_score": 900, "rank": 3}
                ],
                "generated_at": datetime.utcnow().isoformat()
            }
            
            await self.cache_manager.set("leaderboard:global", leaderboard, ttl=1800)
            logger.debug("Warmed leaderboard cache")
            
        except Exception as e:
            logger.error(f"Error warming leaderboard: {str(e)}")


# Cache monitoring and metrics
class CacheMetrics:
    """
    Cache performance monitoring and metrics collection.
    """
    
    def __init__(self, cache_manager: CacheManager):
        """Initialize cache metrics."""
        self.cache_manager = cache_manager
        self.start_time = datetime.utcnow()
    
    async def get_performance_report(self) -> Dict[str, Any]:
        """
        Generate comprehensive cache performance report.
        
        Returns:
            Performance report dictionary
        """
        try:
            stats = await self.cache_manager.get_stats()
            uptime = datetime.utcnow() - self.start_time
            
            report = {
                "uptime_seconds": int(uptime.total_seconds()),
                "cache_stats": stats,
                "performance_indicators": {
                    "hit_rate_status": "excellent" if stats.get("hit_rate", 0) > 80 else 
                                     "good" if stats.get("hit_rate", 0) > 60 else "poor",
                    "error_rate": (stats.get("errors", 0) / max(stats.get("total_requests", 1), 1)) * 100,
                    "memory_usage_mb": stats.get("memory_usage", 0) / (1024 * 1024)
                },
                "recommendations": self._generate_recommendations(stats)
            }
            
            return report
            
        except Exception as e:
            logger.error(f"Error generating performance report: {str(e)}")
            return {"error": str(e)}
    
    def _generate_recommendations(self, stats: Dict[str, Any]) -> List[str]:
        """Generate performance recommendations based on stats."""
        recommendations = []
        
        hit_rate = stats.get("hit_rate", 0)
        if hit_rate < 60:
            recommendations.append("Consider increasing cache TTL or reviewing cache keys")
        
        error_rate = (stats.get("errors", 0) / max(stats.get("total_requests", 1), 1)) * 100
        if error_rate > 5:
            recommendations.append("High error rate detected - check Redis connection")
        
        memory_usage = stats.get("memory_usage", 0)
        if memory_usage > 100 * 1024 * 1024:  # 100MB
            recommendations.append("Consider implementing cache eviction policies")
        
        if not recommendations:
            recommendations.append("Cache performance is optimal")
        
        return recommendations


# Convenience functions for backward compatibility
def cached(key_prefix: str = "default", ttl: int = 3600, expire: int = None):
    """
    Decorator for caching function results (backward compatibility).
    
    Args:
        key_prefix: Cache key prefix
        ttl: Time to live in seconds
        expire: Alternative name for ttl (for backward compatibility)
    """
    # Use expire if provided, otherwise use ttl
    cache_ttl = expire if expire is not None else ttl
    return cache_result(ttl=cache_ttl, key_prefix=key_prefix)


def cache_invalidate(*patterns: str):
    """
    Decorator to invalidate cache patterns after function execution.
    
    Args:
        *patterns: Cache patterns to invalidate
        
    Returns:
        Decorated function
    """
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            try:
                # Execute the original function
                result = await func(*args, **kwargs)
                
                # Invalidate cache patterns after successful execution
                for pattern in patterns:
                    try:
                        await invalidate_cache(pattern)
                        logger.debug(f"Invalidated cache pattern: {pattern}")
                    except Exception as e:
                        logger.error(f"Failed to invalidate cache pattern {pattern}: {str(e)}")
                
                return result
                
            except Exception as e:
                logger.error(f"Error in cache_invalidate decorator for {func.__name__}: {str(e)}")
                raise
        
        return wrapper
    return decorator


async def invalidate_cache_pattern(pattern: str) -> int:
    """
    Invalidate cache entries matching pattern.
    
    Args:
        pattern: Pattern to match for invalidation
        
    Returns:
        Number of keys invalidated
    """
    return await invalidate_cache(pattern)


# Initialize cache warmer and metrics
cache_warmer = CacheWarmer(cache_manager)
cache_metrics = CacheMetrics(cache_manager)