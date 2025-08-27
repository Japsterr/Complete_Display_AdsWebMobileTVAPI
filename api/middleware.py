from django.utils.deprecation import MiddlewareMixin
from django.conf import settings
from .models import ApiKey
from django.contrib.auth import get_user_model

class ApiKeyMiddleware(MiddlewareMixin):
    """Authenticate requests carrying X-API-KEY header. Sets request.api_key and request.user to business owner if applicable."""
    def process_request(self, request):
        key = request.headers.get('X-API-KEY') or request.META.get('HTTP_X_API_KEY')
        request.api_key = None
        if not key:
            return None
        try:
            ak = ApiKey.objects.get(key=key, revoked=False)
            request.api_key = ak
            # If key is tied to a business, set a pseudo-user context (owner) if available
            if ak.business and hasattr(ak.business, 'owner') and ak.business.owner:
                request.user = ak.business.owner
        except ApiKey.DoesNotExist:
            request.api_key = None
        return None
