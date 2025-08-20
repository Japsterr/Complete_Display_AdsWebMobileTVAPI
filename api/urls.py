from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    UserRegistrationView, CampaignViewSet, MediaViewSet, DisplayViewSet,
    TeamInviteView, AndroidTVDisplayView, LogoutView, UserProfileViewSet, user_profile,
    CustomLoginView, CampaignMediaViewSet, request_activation_code, activate_device, 
    check_activation_status, get_device_campaign, tv_simulator_view,
    device_heartbeat, record_media_impression, analytics_dashboard, health_check,
    PasswordResetRequestView, PasswordResetConfirmView, EmailVerificationView,
    ResendVerificationEmailView
)
from .stripe_views import CreateCheckoutSessionView, get_stripe_config, stripe_webhook
from rest_framework_simplejwt.views import TokenRefreshView, TokenObtainPairView

router = DefaultRouter()
router.register(r'campaigns', CampaignViewSet)
router.register(r'media', MediaViewSet)
router.register(r'displays', DisplayViewSet)
router.register(r'userprofiles', UserProfileViewSet)
router.register(r'campaign-media', CampaignMediaViewSet)

urlpatterns = [
    # Health check for mobile app
    path('health/', health_check, name='health-check'),
    
    path('register/', UserRegistrationView.as_view(), name='register'),
    path('auth/register/', UserRegistrationView.as_view(), name='auth_register'),  # Alternative endpoint
    path('login/', CustomLoginView.as_view(), name='login'),
    path('login-simple/', TokenObtainPairView.as_view(), name='login_simple'),  # Test this
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('logout/', LogoutView.as_view(), name='logout'),
    
    # Email verification and password reset endpoints
    path('auth/password-reset-request/', PasswordResetRequestView.as_view(), name='password-reset-request'),
    path('auth/password-reset-confirm/', PasswordResetConfirmView.as_view(), name='password-reset-confirm'),
    path('auth/verify-email/', EmailVerificationView.as_view(), name='verify-email'),
    path('auth/resend-verification/', ResendVerificationEmailView.as_view(), name='resend-verification'),
    
    path('auth/profile/', user_profile, name='user_profile'),
    path('team/invite/', TeamInviteView.as_view(), name='team-invite'),
    path('android-tv/', AndroidTVDisplayView.as_view(), name='android-tv'),
    
    # Device activation endpoints for TV app
    path('devices/request-activation/', request_activation_code, name='request-activation-code'),
    path('devices/activate/', activate_device, name='activate-device'),
    path('devices/check-activation/', check_activation_status, name='check-activation-status'),
    path('devices/current-campaign/', get_device_campaign, name='get-device-campaign'),
    
    # TV Simulator
    path('tv-simulator/', tv_simulator_view, name='tv-simulator'),
    
    # Analytics and Tracking
    path('analytics/heartbeat/', device_heartbeat, name='device-heartbeat'),
    path('analytics/impression/', record_media_impression, name='record-impression'),
    path('analytics/dashboard/', analytics_dashboard, name='analytics-dashboard'),
    
    # Stripe payment endpoints
    path('payments/create-checkout-session/', CreateCheckoutSessionView.as_view(), name='create-checkout-session'),
    path('payments/stripe-config/', get_stripe_config, name='stripe-config'),
    path('payments/stripe-webhook/', stripe_webhook, name='stripe-webhook'),
    
    path('', include(router.urls)),
]

# Swagger/OpenAPI schema views
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions

schema_view = get_schema_view(
    openapi.Info(
        title="Signage API",
        default_version='v1',
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns += [
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]
