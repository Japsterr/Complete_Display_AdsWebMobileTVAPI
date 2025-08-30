from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.db import connection
from django.core.cache import cache
import redis
from django.conf import settings

@csrf_exempt
@require_http_methods(["GET"])
def health_check(request):
    """
    Health check endpoint for Docker and load balancers
    """
    try:
        # Check database connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            db_status = "healthy"
    except Exception as e:
        db_status = f"unhealthy: {str(e)}"
    
    try:
        # Check Redis connection
        cache.set('health_check', 'ok', timeout=10)
        redis_status = "healthy" if cache.get('health_check') == 'ok' else "unhealthy"
    except Exception as e:
        redis_status = f"unhealthy: {str(e)}"
    
    health_data = {
        "status": "healthy" if db_status == "healthy" and "healthy" in redis_status else "unhealthy",
        "database": db_status,
        "cache": redis_status,
        "version": "2.0.0-stage6"
    }
    
    status_code = 200 if health_data["status"] == "healthy" else 503
    return JsonResponse(health_data, status=status_code)