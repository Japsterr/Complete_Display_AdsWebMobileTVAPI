# Advanced Caching Layer - Stage 5
import json
import hashlib
import logging
from typing import Any, Optional, Dict, List
from datetime import datetime, timedelta
from django.core.cache import cache
from django.core.cache.backends.base import DEFAULT_TIMEOUT
from django.utils import timezone
from django.conf import settings

logger = logging.getLogger(__name__)


class AdvancedCacheManager:
    """Advanced caching system with intelligent invalidation and performance optimization"""
    
    def __init__(self):
        self.default_timeout = getattr(settings, 'CACHE_DEFAULT_TIMEOUT', 300)  # 5 minutes
        self.cache_prefix = getattr(settings, 'CACHE_PREFIX', 'displayads')
        
        # Cache timeouts for different data types
        self.timeouts = {
            'menu_performance': 300,      # 5 minutes
            'system_metrics': 180,        # 3 minutes
            'menu_data': 600,            # 10 minutes
            'user_profile': 900,         # 15 minutes
            'campaign_data': 240,        # 4 minutes
            'pos_sync_status': 120,      # 2 minutes
            'analytics_summary': 420,    # 7 minutes
            'item_performance': 360,     # 6 minutes
            'promotional_templates': 1800, # 30 minutes
            'real_time_metrics': 60      # 1 minute
        }
    
    def _build_cache_key(self, key_type: str, identifier: str, params: Dict = None) -> str:
        """Build a standardized cache key"""
        key_parts = [self.cache_prefix, key_type, identifier]
        
        if params:
            # Sort params for consistent key generation
            sorted_params = sorted(params.items())
            param_string = '_'.join([f"{k}:{v}" for k, v in sorted_params])
            key_parts.append(param_string)
        
        cache_key = '_'.join(key_parts)
        
        # Hash long keys to avoid cache key length limits
        if len(cache_key) > 200:
            cache_key = f"{self.cache_prefix}_{key_type}_{hashlib.md5(cache_key.encode()).hexdigest()}"
        
        return cache_key
    
    def get(self, key_type: str, identifier: str, params: Dict = None) -> Optional[Any]:
        """Get cached data with error handling"""
        try:
            cache_key = self._build_cache_key(key_type, identifier, params)
            result = cache.get(cache_key)
            
            if result is not None:
                logger.debug(f"Cache hit: {cache_key}")
                
                # Track cache hit
                self._track_cache_operation('hit', cache_key, key_type)
                
                return result
            else:
                logger.debug(f"Cache miss: {cache_key}")
                
                # Track cache miss
                self._track_cache_operation('miss', cache_key, key_type)
                
                return None
                
        except Exception as e:
            logger.error(f"Cache get error for {key_type}:{identifier} - {str(e)}")
            return None
    
    def set(self, key_type: str, identifier: str, data: Any, params: Dict = None, timeout: Optional[int] = None) -> bool:
        """Set cached data with intelligent timeout"""
        try:
            cache_key = self._build_cache_key(key_type, identifier, params)
            
            # Use specific timeout or default for key type
            if timeout is None:
                timeout = self.timeouts.get(key_type, self.default_timeout)
            
            # Add metadata to cached data
            cached_data = {
                'data': data,
                'cached_at': timezone.now().isoformat(),
                'cache_key': cache_key,
                'key_type': key_type,
                'identifier': identifier
            }
            
            success = cache.set(cache_key, cached_data, timeout)
            
            if success:
                logger.debug(f"Cache set: {cache_key} (timeout: {timeout}s)")
                
                # Track cache set operation
                self._track_cache_operation('set', cache_key, key_type, data_size=len(str(data)))
                
                # Add to invalidation groups
                self._add_to_invalidation_group(key_type, identifier, cache_key)
                
            return success
            
        except Exception as e:
            logger.error(f"Cache set error for {key_type}:{identifier} - {str(e)}")
            return False
    
    def delete(self, key_type: str, identifier: str, params: Dict = None) -> bool:
        """Delete specific cached data"""
        try:
            cache_key = self._build_cache_key(key_type, identifier, params)
            success = cache.delete(cache_key)
            
            if success:
                logger.debug(f"Cache delete: {cache_key}")
                
                # Track cache delete operation
                self._track_cache_operation('delete', cache_key, key_type)
                
                # Remove from invalidation groups
                self._remove_from_invalidation_group(key_type, identifier, cache_key)
            
            return success
            
        except Exception as e:
            logger.error(f"Cache delete error for {key_type}:{identifier} - {str(e)}")
            return False
    
    def invalidate_group(self, key_type: str, identifier: str = None) -> int:
        """Invalidate a group of related cache entries"""
        try:
            invalidated_count = 0
            
            if identifier:
                # Invalidate specific identifier group
                group_key = f"{self.cache_prefix}_group_{key_type}_{identifier}"
                cache_keys = cache.get(group_key, [])
                
                for cache_key in cache_keys:
                    if cache.delete(cache_key):
                        invalidated_count += 1
                
                # Clear the group key
                cache.delete(group_key)
                
            else:
                # Invalidate all entries of this key type
                all_groups_key = f"{self.cache_prefix}_groups_{key_type}"
                group_keys = cache.get(all_groups_key, [])
                
                for group_key in group_keys:
                    cache_keys = cache.get(group_key, [])
                    for cache_key in cache_keys:
                        if cache.delete(cache_key):
                            invalidated_count += 1
                    cache.delete(group_key)
                
                # Clear the all groups key
                cache.delete(all_groups_key)
            
            logger.info(f"Invalidated {invalidated_count} cache entries for {key_type}:{identifier}")
            return invalidated_count
            
        except Exception as e:
            logger.error(f"Cache group invalidation error for {key_type}:{identifier} - {str(e)}")
            return 0
    
    def _add_to_invalidation_group(self, key_type: str, identifier: str, cache_key: str):
        """Add cache key to invalidation group for coordinated invalidation"""
        try:
            # Add to specific identifier group
            group_key = f"{self.cache_prefix}_group_{key_type}_{identifier}"
            current_keys = cache.get(group_key, [])
            
            if cache_key not in current_keys:
                current_keys.append(cache_key)
                cache.set(group_key, current_keys, 86400)  # 24 hour timeout for group tracking
            
            # Add to all groups tracking for key type
            all_groups_key = f"{self.cache_prefix}_groups_{key_type}"
            all_groups = cache.get(all_groups_key, [])
            
            if group_key not in all_groups:
                all_groups.append(group_key)
                cache.set(all_groups_key, all_groups, 86400)
                
        except Exception as e:
            logger.error(f"Error adding to invalidation group: {str(e)}")
    
    def _remove_from_invalidation_group(self, key_type: str, identifier: str, cache_key: str):
        """Remove cache key from invalidation group"""
        try:
            group_key = f"{self.cache_prefix}_group_{key_type}_{identifier}"
            current_keys = cache.get(group_key, [])
            
            if cache_key in current_keys:
                current_keys.remove(cache_key)
                if current_keys:
                    cache.set(group_key, current_keys, 86400)
                else:
                    cache.delete(group_key)
                    
        except Exception as e:
            logger.error(f"Error removing from invalidation group: {str(e)}")
    
    def _track_cache_operation(self, operation: str, cache_key: str, key_type: str, data_size: int = 0):
        """Track cache operations for performance monitoring"""
        try:
            # Simple in-memory tracking (in production, use proper metrics)
            stats_key = f"{self.cache_prefix}_stats_{key_type}"
            current_stats = cache.get(stats_key, {
                'hits': 0,
                'misses': 0,
                'sets': 0,
                'deletes': 0,
                'total_size': 0
            })
            
            if operation == 'hit':
                current_stats['hits'] += 1
            elif operation == 'miss':
                current_stats['misses'] += 1
            elif operation == 'set':
                current_stats['sets'] += 1
                current_stats['total_size'] += data_size
            elif operation == 'delete':
                current_stats['deletes'] += 1
            
            # Update stats with short timeout to avoid bloating cache
            cache.set(stats_key, current_stats, 300)
            
        except Exception as e:
            logger.error(f"Error tracking cache operation: {str(e)}")
    
    def get_cache_stats(self, key_type: str = None) -> Dict[str, Any]:
        """Get cache performance statistics"""
        try:
            if key_type:
                # Get stats for specific key type
                stats_key = f"{self.cache_prefix}_stats_{key_type}"
                stats = cache.get(stats_key, {})
                
                if stats:
                    # Calculate hit rate
                    total_requests = stats.get('hits', 0) + stats.get('misses', 0)
                    hit_rate = (stats.get('hits', 0) / total_requests * 100) if total_requests > 0 else 0
                    
                    return {
                        'key_type': key_type,
                        'stats': stats,
                        'hit_rate': round(hit_rate, 2),
                        'total_requests': total_requests
                    }
                else:
                    return {'key_type': key_type, 'stats': None}
            else:
                # Get stats for all key types
                all_stats = {}
                
                for kt in self.timeouts.keys():
                    type_stats = self.get_cache_stats(kt)
                    if type_stats.get('stats'):
                        all_stats[kt] = type_stats
                
                return all_stats
                
        except Exception as e:
            logger.error(f"Error getting cache stats: {str(e)}")
            return {'error': str(e)}
    
    def warm_cache(self, key_type: str, identifiers: List[str], data_fetcher_func, params: Dict = None):
        """Pre-warm cache with frequently accessed data"""
        try:
            warmed_count = 0
            
            for identifier in identifiers:
                cache_key = self._build_cache_key(key_type, identifier, params)
                
                # Check if already cached
                if cache.get(cache_key) is None:
                    try:
                        # Fetch data and cache it
                        data = data_fetcher_func(identifier, params)
                        if data is not None:
                            if self.set(key_type, identifier, data, params):
                                warmed_count += 1
                                logger.debug(f"Warmed cache for {key_type}:{identifier}")
                        
                    except Exception as fetch_error:
                        logger.error(f"Error fetching data for cache warming {identifier}: {str(fetch_error)}")
                        continue
            
            logger.info(f"Cache warming completed: {warmed_count}/{len(identifiers)} entries warmed")
            return warmed_count
            
        except Exception as e:
            logger.error(f"Cache warming error: {str(e)}")
            return 0
    
    def cleanup_expired(self) -> int:
        """Clean up expired cache entries (if backend doesn't handle automatically)"""
        try:
            # This is primarily for debugging and monitoring
            # Most cache backends handle expiration automatically
            
            cleaned_count = 0
            
            # Get all group tracking keys and verify they exist
            for key_type in self.timeouts.keys():
                all_groups_key = f"{self.cache_prefix}_groups_{key_type}"
                group_keys = cache.get(all_groups_key, [])
                
                valid_groups = []
                for group_key in group_keys:
                    if cache.get(group_key) is not None:
                        valid_groups.append(group_key)
                    else:
                        cleaned_count += 1
                
                if len(valid_groups) != len(group_keys):
                    cache.set(all_groups_key, valid_groups, 86400)
            
            logger.info(f"Cache cleanup completed: {cleaned_count} expired entries removed")
            return cleaned_count
            
        except Exception as e:
            logger.error(f"Cache cleanup error: {str(e)}")
            return 0


class SmartCacheDecorator:
    """Decorator for automatic caching of expensive operations"""
    
    def __init__(self, cache_manager: AdvancedCacheManager):
        self.cache_manager = cache_manager
    
    def cache_result(self, key_type: str, timeout: Optional[int] = None, invalidate_on: List[str] = None):
        """Decorator to cache function results"""
        def decorator(func):
            def wrapper(*args, **kwargs):
                # Build cache identifier from function name and arguments
                func_name = func.__name__
                args_str = '_'.join([str(arg) for arg in args])
                kwargs_str = '_'.join([f"{k}_{v}" for k, v in sorted(kwargs.items())])
                identifier = f"{func_name}_{args_str}_{kwargs_str}"
                
                # Try to get from cache
                cached_result = self.cache_manager.get(key_type, identifier)
                
                if cached_result is not None:
                    return cached_result['data']
                
                # Execute function and cache result
                try:
                    result = func(*args, **kwargs)
                    self.cache_manager.set(key_type, identifier, result, timeout=timeout)
                    return result
                    
                except Exception as e:
                    logger.error(f"Function execution error in cached function {func_name}: {str(e)}")
                    raise
            
            return wrapper
        return decorator


# Global cache manager instance
advanced_cache_manager = AdvancedCacheManager()
smart_cache_decorator = SmartCacheDecorator(advanced_cache_manager)


class CacheMiddleware:
    """Middleware for automatic cache management"""
    
    def __init__(self, get_response):
        self.get_response = get_response
        self.cache_manager = advanced_cache_manager
    
    def __call__(self, request):
        # Process request
        response = self.get_response(request)
        
        # Add cache headers for API responses
        if request.path.startswith('/api/') and response.status_code == 200:
            # Add cache-related headers
            response['X-Cache-Status'] = 'MISS'  # This would be determined by actual cache logic
            response['X-Cache-Age'] = '0'
        
        return response
    
    def process_view(self, request, view_func, view_args, view_kwargs):
        """Process view for cache optimization"""
        # Add cache warming for frequently accessed endpoints
        if request.path.startswith('/api/analytics/'):
            # Pre-warm related cache entries
            pass
        
        return None


# Cache invalidation signals
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver


@receiver(post_save, sender='api.Menu')
def invalidate_menu_cache(sender, instance, created, **kwargs):
    """Invalidate menu-related cache when menu is updated"""
    try:
        advanced_cache_manager.invalidate_group('menu_data', instance.menu_id)
        advanced_cache_manager.invalidate_group('menu_performance', instance.menu_id)
        advanced_cache_manager.invalidate_group('analytics_summary')
        logger.info(f"Invalidated cache for menu: {instance.menu_id}")
    except Exception as e:
        logger.error(f"Error invalidating menu cache: {str(e)}")


@receiver(post_save, sender='api.MenuItem')
def invalidate_menu_item_cache(sender, instance, created, **kwargs):
    """Invalidate item-related cache when menu item is updated"""
    try:
        if instance.menu:
            advanced_cache_manager.invalidate_group('menu_data', instance.menu.menu_id)
            advanced_cache_manager.invalidate_group('item_performance', instance.item_id)
            advanced_cache_manager.invalidate_group('menu_performance', instance.menu.menu_id)
        logger.info(f"Invalidated cache for menu item: {instance.item_id}")
    except Exception as e:
        logger.error(f"Error invalidating menu item cache: {str(e)}")


@receiver(post_save, sender='api.Campaign')
def invalidate_campaign_cache(sender, instance, created, **kwargs):
    """Invalidate campaign-related cache when campaign is updated"""
    try:
        advanced_cache_manager.invalidate_group('campaign_data', str(instance.id))
        advanced_cache_manager.invalidate_group('analytics_summary')
        if instance.menu_id:
            advanced_cache_manager.invalidate_group('menu_performance', instance.menu_id)
        logger.info(f"Invalidated cache for campaign: {instance.id}")
    except Exception as e:
        logger.error(f"Error invalidating campaign cache: {str(e)}")


@receiver(post_save, sender='api.POSUpdateLog')
def invalidate_pos_cache(sender, instance, created, **kwargs):
    """Invalidate POS-related cache when sync occurs"""
    try:
        if created:  # Only on new sync events
            advanced_cache_manager.invalidate_group('pos_sync_status', str(instance.pos_integration_id))
            advanced_cache_manager.invalidate_group('system_metrics')
            logger.info(f"Invalidated POS cache for integration: {instance.pos_integration_id}")
    except Exception as e:
        logger.error(f"Error invalidating POS cache: {str(e)}")