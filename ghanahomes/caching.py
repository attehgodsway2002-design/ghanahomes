"""
Caching utilities for performance optimization
"""
from django.views.decorators.cache import cache_page, cache_control
from functools import wraps
from django.middleware.cache import UpdateCacheMiddleware, FetchFromCacheMiddleware
from django.views.decorators.http import condition


def cache_response(seconds=3600, cache_alias='default'):
    """
    Decorator to cache view responses
    
    Args:
        seconds: Cache timeout in seconds (default: 1 hour)
        cache_alias: Cache backend alias (default: 'default')
    """
    def decorator(view_func):
        return cache_page(seconds, cache_alias=cache_alias)(view_func)
    return decorator


def browser_cache_control(**kwargs):
    """
    Set cache control headers for browser caching
    
    Args:
        max_age: Cache timeout in seconds
        private: If True, cache only in private cache
        public: If True, cache in public cache
        no_cache: If True, revalidate before using cached copy
        no_store: If True, don't cache at all
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            response = view_func(request, *args, **kwargs)
            
            # Set cache headers
            if 'max_age' in kwargs:
                response['Cache-Control'] = f"max-age={kwargs['max_age']}"
                if kwargs.get('private'):
                    response['Cache-Control'] += ', private'
                if kwargs.get('public'):
                    response['Cache-Control'] += ', public'
            
            return response
        
        return wrapper
    
    return decorator


# Caching configuration for settings.py

CACHING_CONFIG = {
    'CACHES': {
        'default': {
            'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
            'LOCATION': 'ghanahomes-cache',
            'TIMEOUT': 300,
            'OPTIONS': {
                'MAX_ENTRIES': 1000
            }
        }
    },
    # Cache timeout values for different views
    'CACHE_TIMEOUTS': {
        'property_list': 600,        # 10 minutes
        'property_detail': 1800,     # 30 minutes
        'home_page': 300,            # 5 minutes
        'categories': 3600,          # 1 hour
        'user_profile': 600,         # 10 minutes (don't cache user-specific data)
    }
}


# Suggested settings.py additions:
"""
# Cache Configuration
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'ghanahomes-cache',
        'TIMEOUT': 300,  # 5 minutes default
        'OPTIONS': {
            'MAX_ENTRIES': 1000
        }
    }
}

# Cache Middleware (optional, for full page caching)
MIDDLEWARE = [
    # ... other middleware ...
    'django.middleware.cache.UpdateCacheMiddleware',
    # ... other middleware ...
    'django.middleware.cache.FetchFromCacheMiddleware',
]

# Cache timeout for middleware
CACHE_MIDDLEWARE_SECONDS = 600  # 10 minutes

# Cache key prefix for multiple environments
CACHE_MIDDLEWARE_KEY_PREFIX = 'ghanahomes'

"""
