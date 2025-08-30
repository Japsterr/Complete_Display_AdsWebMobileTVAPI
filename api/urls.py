from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    UserRegistrationView, CampaignViewSet, MediaViewSet, DisplayViewSet,
    TeamInviteView, AndroidTVDisplayView, LogoutView, UserProfileViewSet, user_profile,
    CustomLoginView, CampaignMediaViewSet, request_activation_code, activate_device, 
    check_activation_status, get_device_campaign, tv_simulator_view,
    device_heartbeat, record_media_impression, analytics_dashboard, health_check,
    analytics_summary, export_impressions_csv, export_devices_csv, analytics_campaign_breakdown,
    OrganizationViewSet, MembershipViewSet, InvitationViewSet, AuditLogViewSet,
    DisplayGroupViewSet, TagViewSet, MediaApprovalViewSet,
    assign_campaign_to_displays, assign_campaign_to_group, broadcast_campaign, queue_campaign_for_displays,
    dry_run_campaign_action, bulk_unassign_displays, bulk_unassign_group, bulk_unassign_all
)
from .stripe_views import CreateCheckoutSessionView, get_stripe_config, stripe_webhook
from rest_framework_simplejwt.views import TokenRefreshView, TokenObtainPairView

# Menu System Imports
from .menu_views import (
    MenuViewSet, MenuCategoryViewSet, MenuItemViewSet, ApiKeyViewSet, POSIntegrationViewSet as MenuPOSIntegrationViewSet,
    pos_update_menu_items, pos_webhook_handler, pos_sync_logs, menu_analytics
)
from .promotional_views import PromotionalTemplateViewSet
# Stage 4 Advanced POS Synchronization Imports
from .pos_views import POSIntegrationViewSet, POSUpdateLogViewSet, POSWebhookView

router = DefaultRouter()
router.register(r'campaigns', CampaignViewSet)
router.register(r'media', MediaViewSet)
router.register(r'displays', DisplayViewSet)
router.register(r'userprofiles', UserProfileViewSet)
router.register(r'campaign-media', CampaignMediaViewSet)
router.register(r'organizations', OrganizationViewSet)
router.register(r'memberships', MembershipViewSet)
router.register(r'invitations', InvitationViewSet)
router.register(r'audit-logs', AuditLogViewSet)
router.register(r'display-groups', DisplayGroupViewSet)
router.register(r'tags', TagViewSet)
router.register(r'media-approvals', MediaApprovalViewSet)

# Menu System Routes
router.register(r'menus', MenuViewSet, basename='menu')
router.register(r'menu-categories', MenuCategoryViewSet, basename='menucategory')
router.register(r'menu-items', MenuItemViewSet, basename='menuitem')
router.register(r'api-keys', ApiKeyViewSet, basename='apikey')
router.register(r'pos-integrations-menu', MenuPOSIntegrationViewSet, basename='posintegration')
router.register(r'promotional-templates', PromotionalTemplateViewSet, basename='promotionaltemplate')
# Stage 4 Advanced POS Synchronization Routes
router.register(r'pos-integrations', POSIntegrationViewSet, basename='pos-integration')
router.register(r'pos-logs', POSUpdateLogViewSet, basename='pos-logs')

urlpatterns = [
    # Health check for mobile app
    path('health/', health_check, name='health-check'),
    
    path('register/', UserRegistrationView.as_view(), name='register'),
    path('auth/register/', UserRegistrationView.as_view(), name='auth_register'),  # Alternative endpoint
    path('login/', CustomLoginView.as_view(), name='login'),
    path('login-simple/', TokenObtainPairView.as_view(), name='login_simple'),  # Test this
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('logout/', LogoutView.as_view(), name='logout'),
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
    path('analytics/summary/', analytics_summary, name='analytics-summary'),
    path('analytics/campaign-breakdown/', analytics_campaign_breakdown, name='analytics-campaign-breakdown'),
    path('analytics/export/impressions.csv', export_impressions_csv, name='export-impressions-csv'),
    path('analytics/export/devices.csv', export_devices_csv, name='export-devices-csv'),

    # Assignment & Broadcast
    path('campaigns/assign/displays/', assign_campaign_to_displays, name='assign-campaign-displays'),
    path('campaigns/assign/group/', assign_campaign_to_group, name='assign-campaign-group'),
    path('campaigns/broadcast/', broadcast_campaign, name='broadcast-campaign'),
    path('campaigns/queue/displays/', queue_campaign_for_displays, name='queue-campaign-displays'),
    path('campaigns/dry-run/', dry_run_campaign_action, name='campaign-dry-run'),
    path('campaigns/unassign/displays/', bulk_unassign_displays, name='bulk-unassign-displays'),
    path('campaigns/unassign/group/', bulk_unassign_group, name='bulk-unassign-group'),
    path('campaigns/unassign/all/', bulk_unassign_all, name='bulk-unassign-all'),
    
    # Stripe payment endpoints
    path('payments/create-checkout-session/', CreateCheckoutSessionView.as_view(), name='create-checkout-session'),
    path('payments/stripe-config/', get_stripe_config, name='stripe-config'),
    path('payments/stripe-webhook/', stripe_webhook, name='stripe-webhook'),
    
    # Menu System & POS Integration Endpoints
    path('menus/pos-update/', pos_update_menu_items, name='pos-update-menu-items'),
    path('pos/webhook/', pos_webhook_handler, name='pos-webhook'),
    path('pos/sync-logs/', pos_sync_logs, name='pos-sync-logs'),
    path('analytics/menu-performance/', menu_analytics, name='menu-analytics'),
    
    # Stage 4 Advanced POS Synchronization Endpoints
    path('pos-webhook/<int:pos_integration_id>/', POSWebhookView.as_view(), name='pos-webhook-advanced'),
    
    # Stage 6 Advanced Features
    path('advanced/', include('api.advanced_features_urls')),
    
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
