# Advanced Features URL Configuration for Stage 6
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .advanced_features_views import (
    ABTestingViewSet,
    MultiLanguageViewSet,
    AccessibilityViewSet,
    MenuDisplayViewSet,
    track_menu_event
)

# Create router for viewsets
router = DefaultRouter()
router.register(r'ab-testing', ABTestingViewSet, basename='ab-testing')
router.register(r'multi-language', MultiLanguageViewSet, basename='multi-language')
router.register(r'accessibility', AccessibilityViewSet, basename='accessibility')
router.register(r'enhanced-display', MenuDisplayViewSet, basename='enhanced-display')

# Advanced features URL patterns
urlpatterns = [
    # Include router URLs
    path('', include(router.urls)),
    
    # Event tracking endpoint
    path('track-event/', track_menu_event, name='track-menu-event'),
    
    # A/B Testing specific endpoints
    path('ab-testing/create/', ABTestingViewSet.as_view({'post': 'create_test'}), name='ab-test-create'),
    path('ab-testing/<str:pk>/assign/', ABTestingViewSet.as_view({'post': 'assign_variant'}), name='ab-test-assign'),
    path('ab-testing/<str:pk>/event/', ABTestingViewSet.as_view({'post': 'record_event'}), name='ab-test-event'),
    path('ab-testing/<str:pk>/analytics/', ABTestingViewSet.as_view({'get': 'analytics'}), name='ab-test-analytics'),
    path('ab-testing/active/', ABTestingViewSet.as_view({'get': 'active_tests'}), name='ab-test-active'),
    
    # Multi-language specific endpoints
    path('multi-language/languages/', MultiLanguageViewSet.as_view({'get': 'supported_languages'}), name='supported-languages'),
    path('multi-language/<int:pk>/translate/', MultiLanguageViewSet.as_view({'get': 'translate_menu'}), name='translate-menu'),
    path('multi-language/detect/', MultiLanguageViewSet.as_view({'post': 'detect_language'}), name='detect-language'),
    
    # Accessibility specific endpoints
    path('accessibility/<int:pk>/enhance/', AccessibilityViewSet.as_view({'post': 'enhance_menu'}), name='enhance-accessibility'),
    path('accessibility/<int:pk>/validate/', AccessibilityViewSet.as_view({'get': 'validate_compliance'}), name='validate-accessibility'),
    path('accessibility/features/', AccessibilityViewSet.as_view({'get': 'available_features'}), name='accessibility-features'),
    
    # Enhanced display endpoint
    path('enhanced-display/<int:pk>/display/', MenuDisplayViewSet.as_view({'get': 'display'}), name='enhanced-menu-display'),
]