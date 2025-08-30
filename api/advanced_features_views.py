# Advanced Features Views for Stage 6
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.core.cache import cache
from django.utils import timezone
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
import json
import logging
from typing import Dict, Any, List

from .advanced_features import (
    ab_testing_engine,
    multi_language_manager,
    accessibility_enhancer
)
from .models import Menu, MenuItem, Campaign
from .serializers import MenuSerializer

logger = logging.getLogger(__name__)


class ABTestingViewSet(viewsets.ViewSet):
    """A/B Testing management endpoints"""
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['post'])
    def create_test(self, request):
        """Create a new A/B test"""
        try:
            test_config = request.data
            
            # Validate menu exists
            menu_id = test_config.get('menu_id')
            if not Menu.objects.filter(id=menu_id).exists():
                return Response({
                    'error': 'Menu not found'
                }, status=status.HTTP_404_NOT_FOUND)
            
            # Create test
            result = ab_testing_engine.create_ab_test(test_config)
            
            if result['success']:
                return Response({
                    'success': True,
                    'test_id': result['test_id'],
                    'test': result['test']
                }, status=status.HTTP_201_CREATED)
            else:
                return Response({
                    'error': result['error']
                }, status=status.HTTP_400_BAD_REQUEST)
                
        except Exception as e:
            logger.error(f"Error creating A/B test: {str(e)}")
            return Response({
                'error': 'Failed to create A/B test'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=True, methods=['get'])
    def get_test(self, request, pk=None):
        """Get A/B test details"""
        try:
            test = ab_testing_engine.get_ab_test(pk)
            
            if test:
                return Response(test)
            else:
                return Response({
                    'error': 'Test not found'
                }, status=status.HTTP_404_NOT_FOUND)
                
        except Exception as e:
            logger.error(f"Error getting A/B test: {str(e)}")
            return Response({
                'error': 'Failed to get A/B test'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=True, methods=['post'])
    def assign_variant(self, request, pk=None):
        """Assign user to A/B test variant"""
        try:
            user_identifier = request.data.get('user_identifier')
            if not user_identifier:
                user_identifier = f"user_{request.user.id}" if request.user.is_authenticated else f"anon_{hash(request.META.get('REMOTE_ADDR', ''))}"
            
            assignment = ab_testing_engine.assign_user_to_variant(pk, user_identifier)
            
            return Response(assignment)
            
        except Exception as e:
            logger.error(f"Error assigning A/B test variant: {str(e)}")
            return Response({
                'error': 'Failed to assign variant'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=True, methods=['post'])
    def record_event(self, request, pk=None):
        """Record A/B test event"""
        try:
            user_identifier = request.data.get('user_identifier')
            event_type = request.data.get('event_type')
            event_data = request.data.get('event_data', {})
            
            if not user_identifier:
                user_identifier = f"user_{request.user.id}" if request.user.is_authenticated else f"anon_{hash(request.META.get('REMOTE_ADDR', ''))}"
            
            if not event_type:
                return Response({
                    'error': 'Event type is required'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            success = ab_testing_engine.record_ab_test_event(pk, user_identifier, event_type, event_data)
            
            if success:
                return Response({'success': True})
            else:
                return Response({
                    'error': 'Failed to record event'
                }, status=status.HTTP_400_BAD_REQUEST)
                
        except Exception as e:
            logger.error(f"Error recording A/B test event: {str(e)}")
            return Response({
                'error': 'Failed to record event'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=True, methods=['get'])
    def analytics(self, request, pk=None):
        """Get A/B test analytics"""
        try:
            analytics = ab_testing_engine.get_test_analytics(pk)
            
            if 'error' in analytics:
                return Response(analytics, status=status.HTTP_404_NOT_FOUND)
            
            return Response(analytics)
            
        except Exception as e:
            logger.error(f"Error getting A/B test analytics: {str(e)}")
            return Response({
                'error': 'Failed to get analytics'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['get'])
    def active_tests(self, request):
        """Get active A/B tests for a menu"""
        try:
            menu_id = request.query_params.get('menu_id')
            
            if not menu_id:
                return Response({
                    'error': 'Menu ID is required'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            active_tests = ab_testing_engine.get_active_tests_for_menu(menu_id)
            
            return Response({
                'active_tests': active_tests,
                'count': len(active_tests)
            })
            
        except Exception as e:
            logger.error(f"Error getting active A/B tests: {str(e)}")
            return Response({
                'error': 'Failed to get active tests'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class MultiLanguageViewSet(viewsets.ViewSet):
    """Multi-language support endpoints"""
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['get'])
    def supported_languages(self, request):
        """Get list of supported languages"""
        try:
            languages = multi_language_manager.get_supported_languages()
            return Response(languages)
            
        except Exception as e:
            logger.error(f"Error getting supported languages: {str(e)}")
            return Response({
                'error': 'Failed to get supported languages'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=True, methods=['get'])
    def translate_menu(self, request, pk=None):
        """Translate menu to target language"""
        try:
            target_language = request.query_params.get('language', 'en')
            
            # Get menu data
            try:
                menu = Menu.objects.get(id=pk)
            except Menu.DoesNotExist:
                return Response({
                    'error': 'Menu not found'
                }, status=status.HTTP_404_NOT_FOUND)
            
            # Serialize menu data
            serializer = MenuSerializer(menu)
            menu_data = serializer.data
            
            # Add menu items
            menu_items = MenuItem.objects.filter(menu=menu, is_available=True)
            menu_data['items'] = []
            
            for item in menu_items:
                item_data = {
                    'id': item.id,
                    'name': item.name,
                    'description': item.description,
                    'price': float(item.price),
                    'category': item.category,
                    'is_available': item.is_available,
                    'dietary_info': {
                        'vegetarian': getattr(item, 'is_vegetarian', False),
                        'vegan': getattr(item, 'is_vegan', False),
                        'gluten_free': getattr(item, 'is_gluten_free', False),
                        'contains_nuts': getattr(item, 'contains_nuts', False)
                    }
                }
                
                if hasattr(item, 'image') and item.image:
                    item_data['image_url'] = item.image.url
                
                menu_data['items'].append(item_data)
            
            # Translate menu content
            translated_menu = multi_language_manager.translate_menu_content(menu_data, target_language)
            
            return Response(translated_menu)
            
        except Exception as e:
            logger.error(f"Error translating menu: {str(e)}")
            return Response({
                'error': 'Failed to translate menu'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['post'])
    def detect_language(self, request):
        """Detect user's preferred language"""
        try:
            detected_language = multi_language_manager.detect_user_language(request)
            
            return Response({
                'detected_language': detected_language,
                'supported_languages': multi_language_manager.get_supported_languages()
            })
            
        except Exception as e:
            logger.error(f"Error detecting language: {str(e)}")
            return Response({
                'error': 'Failed to detect language'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class AccessibilityViewSet(viewsets.ViewSet):
    """Accessibility enhancement endpoints"""
    permission_classes = [IsAuthenticated]
    
    @action(detail=True, methods=['post'])
    def enhance_menu(self, request, pk=None):
        """Enhance menu with accessibility features"""
        try:
            accessibility_options = request.data.get('accessibility_options', {})
            
            # Get menu data
            try:
                menu = Menu.objects.get(id=pk)
            except Menu.DoesNotExist:
                return Response({
                    'error': 'Menu not found'
                }, status=status.HTTP_404_NOT_FOUND)
            
            # Serialize menu data
            serializer = MenuSerializer(menu)
            menu_data = serializer.data
            
            # Add menu items
            menu_items = MenuItem.objects.filter(menu=menu, is_available=True)
            menu_data['items'] = []
            
            for item in menu_items:
                item_data = {
                    'id': item.id,
                    'name': item.name,
                    'description': item.description,
                    'price': float(item.price),
                    'category': item.category,
                    'is_available': item.is_available,
                    'dietary_info': {
                        'vegetarian': getattr(item, 'is_vegetarian', False),
                        'vegan': getattr(item, 'is_vegan', False),
                        'gluten_free': getattr(item, 'is_gluten_free', False),
                        'contains_nuts': getattr(item, 'contains_nuts', False)
                    }
                }
                
                if hasattr(item, 'image') and item.image:
                    item_data['image_url'] = item.image.url
                
                menu_data['items'].append(item_data)
            
            # Enhance menu for accessibility
            enhanced_menu = accessibility_enhancer.enhance_menu_for_accessibility(menu_data, accessibility_options)
            
            return Response(enhanced_menu)
            
        except Exception as e:
            logger.error(f"Error enhancing menu for accessibility: {str(e)}")
            return Response({
                'error': 'Failed to enhance menu for accessibility'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=True, methods=['get'])
    def validate_compliance(self, request, pk=None):
        """Validate menu accessibility compliance"""
        try:
            # Get menu data
            try:
                menu = Menu.objects.get(id=pk)
            except Menu.DoesNotExist:
                return Response({
                    'error': 'Menu not found'
                }, status=status.HTTP_404_NOT_FOUND)
            
            # Serialize menu data
            serializer = MenuSerializer(menu)
            menu_data = serializer.data
            
            # Add menu items
            menu_items = MenuItem.objects.filter(menu=menu, is_available=True)
            menu_data['items'] = []
            
            for item in menu_items:
                item_data = {
                    'id': item.id,
                    'name': item.name,
                    'description': item.description,
                    'price': float(item.price),
                    'category': item.category,
                    'is_available': item.is_available
                }
                
                if hasattr(item, 'image') and item.image:
                    item_data['image_url'] = item.image.url
                
                menu_data['items'].append(item_data)
            
            # Validate accessibility compliance
            compliance_report = accessibility_enhancer.validate_accessibility_compliance(menu_data)
            
            return Response(compliance_report)
            
        except Exception as e:
            logger.error(f"Error validating accessibility compliance: {str(e)}")
            return Response({
                'error': 'Failed to validate accessibility compliance'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['get'])
    def available_features(self, request):
        """Get available accessibility features"""
        try:
            features = {
                'features': accessibility_enhancer.accessibility_features,
                'descriptions': {
                    'high_contrast': 'High contrast color scheme for better visibility',
                    'large_text': 'Increased font size for better readability',
                    'screen_reader_support': 'ARIA labels and descriptions for screen readers',
                    'keyboard_navigation': 'Full keyboard navigation support',
                    'voice_commands': 'Voice command recognition and control',
                    'color_blind_friendly': 'Color blind friendly color palette and patterns'
                }
            }
            
            return Response(features)
            
        except Exception as e:
            logger.error(f"Error getting accessibility features: {str(e)}")
            return Response({
                'error': 'Failed to get accessibility features'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class MenuDisplayViewSet(viewsets.ViewSet):
    """Enhanced menu display with advanced features"""
    
    @method_decorator(cache_page(60))  # Cache for 1 minute
    @action(detail=True, methods=['get'])
    def display(self, request, pk=None):
        """Get enhanced menu display with all advanced features"""
        try:
            # Get base menu data
            try:
                menu = Menu.objects.get(id=pk)
            except Menu.DoesNotExist:
                return Response({
                    'error': 'Menu not found'
                }, status=status.HTTP_404_NOT_FOUND)
            
            # Get query parameters
            language = request.query_params.get('language')
            user_identifier = request.query_params.get('user_id', f"anon_{hash(request.META.get('REMOTE_ADDR', ''))}")
            accessibility_options = {}
            
            # Parse accessibility options from query params
            if request.query_params.get('high_contrast'):
                accessibility_options['high_contrast'] = True
            if request.query_params.get('large_text'):
                accessibility_options['large_text'] = True
            if request.query_params.get('screen_reader'):
                accessibility_options['screen_reader_support'] = True
            if request.query_params.get('color_blind_friendly'):
                accessibility_options['color_blind_friendly'] = True
            
            # Serialize menu data
            serializer = MenuSerializer(menu)
            menu_data = serializer.data
            
            # Add menu items
            menu_items = MenuItem.objects.filter(menu=menu, is_available=True)
            menu_data['items'] = []
            
            for item in menu_items:
                item_data = {
                    'id': item.id,
                    'name': item.name,
                    'description': item.description,
                    'price': float(item.price),
                    'category': item.category,
                    'is_available': item.is_available,
                    'dietary_info': {
                        'vegetarian': getattr(item, 'is_vegetarian', False),
                        'vegan': getattr(item, 'is_vegan', False),
                        'gluten_free': getattr(item, 'is_gluten_free', False),
                        'contains_nuts': getattr(item, 'contains_nuts', False)
                    }
                }
                
                if hasattr(item, 'image') and item.image:
                    item_data['image_url'] = item.image.url
                
                menu_data['items'].append(item_data)
            
            # Apply A/B testing
            active_tests = ab_testing_engine.get_active_tests_for_menu(str(pk))
            applied_tests = []
            
            for test in active_tests:
                assignment = ab_testing_engine.assign_user_to_variant(test['test_id'], user_identifier)
                if assignment.get('variant'):
                    # Apply test configuration
                    test_config = assignment.get('test_config', {})
                    if test_config:
                        # Merge test configuration into menu data
                        menu_data.update(test_config)
                    
                    applied_tests.append({
                        'test_id': test['test_id'],
                        'variant': assignment['variant'],
                        'test_type': test['type']
                    })
                    
                    # Record view event
                    ab_testing_engine.record_ab_test_event(test['test_id'], user_identifier, 'view')
            
            # Apply language translation
            if not language:
                language = multi_language_manager.detect_user_language(request)
            
            if language and language != 'en':
                menu_data = multi_language_manager.translate_menu_content(menu_data, language)
            
            # Apply accessibility enhancements
            if accessibility_options:
                menu_data = accessibility_enhancer.enhance_menu_for_accessibility(menu_data, accessibility_options)
            
            # Add metadata
            menu_data['display_metadata'] = {
                'generated_at': timezone.now().isoformat(),
                'language': language,
                'applied_tests': applied_tests,
                'accessibility_features': list(accessibility_options.keys()),
                'user_identifier': user_identifier
            }
            
            return Response(menu_data)
            
        except Exception as e:
            logger.error(f"Error displaying enhanced menu: {str(e)}")
            return Response({
                'error': 'Failed to display menu'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# Event tracking endpoint for A/B testing
@csrf_exempt
def track_menu_event(request):
    """Track menu interaction events for A/B testing"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            
            test_id = data.get('test_id')
            user_identifier = data.get('user_identifier')
            event_type = data.get('event_type')
            event_data = data.get('event_data', {})
            
            if test_id and user_identifier and event_type:
                success = ab_testing_engine.record_ab_test_event(test_id, user_identifier, event_type, event_data)
                
                return JsonResponse({
                    'success': success
                })
            else:
                return JsonResponse({
                    'error': 'Missing required parameters'
                }, status=400)
                
        except Exception as e:
            logger.error(f"Error tracking menu event: {str(e)}")
            return JsonResponse({
                'error': 'Failed to track event'
            }, status=500)
    
    return JsonResponse({
        'error': 'Method not allowed'
    }, status=405)