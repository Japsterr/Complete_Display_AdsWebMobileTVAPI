# Stage 6: Advanced Features & Polish
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from django.core.cache import cache
from django.utils import timezone
from django.conf import settings
from django.utils.translation import gettext as _
from django.utils.translation import activate, get_language
import random

logger = logging.getLogger(__name__)


class ABTestingEngine:
    """Advanced A/B testing system for menu optimization"""
    
    def __init__(self):
        self.cache_timeout = 300  # 5 minutes
    
    def create_ab_test(self, test_config: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new A/B test"""
        try:
            test_id = f"ab_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{random.randint(1000, 9999)}"
            
            # Validate test configuration
            validation_result = self._validate_test_config(test_config)
            if not validation_result['valid']:
                return {
                    'success': False,
                    'error': validation_result['errors']
                }
            
            # Create test structure
            ab_test = {
                'test_id': test_id,
                'name': test_config['name'],
                'description': test_config.get('description', ''),
                'type': test_config['type'],  # menu_layout, pricing, promotional, content
                'menu_id': test_config['menu_id'],
                'status': 'active',
                'created_at': timezone.now().isoformat(),
                'start_date': test_config.get('start_date', timezone.now().isoformat()),
                'end_date': test_config.get('end_date', (timezone.now() + timedelta(days=7)).isoformat()),
                'traffic_split': test_config.get('traffic_split', 50),  # Percentage for variant B
                'variants': {
                    'control': {
                        'name': 'Control (A)',
                        'config': test_config['control_config'],
                        'traffic_percentage': 100 - test_config.get('traffic_split', 50)
                    },
                    'variant': {
                        'name': 'Variant (B)',
                        'config': test_config['variant_config'],
                        'traffic_percentage': test_config.get('traffic_split', 50)
                    }
                },
                'metrics': {
                    'primary_metric': test_config.get('primary_metric', 'view_time'),
                    'secondary_metrics': test_config.get('secondary_metrics', ['click_rate', 'engagement'])
                },
                'results': {
                    'control': {'views': 0, 'conversions': 0, 'total_time': 0, 'interactions': 0},
                    'variant': {'views': 0, 'conversions': 0, 'total_time': 0, 'interactions': 0}
                },
                'statistical_significance': False,
                'confidence_level': test_config.get('confidence_level', 95)
            }
            
            # Store test
            cache_key = f"ab_test_{test_id}"
            cache.set(cache_key, ab_test, timeout=86400 * 30)  # 30 days
            
            # Add to active tests list
            self._add_to_active_tests(test_id, test_config['menu_id'])
            
            logger.info(f"Created A/B test: {test_id}")
            
            return {
                'success': True,
                'test_id': test_id,
                'test': ab_test
            }
            
        except Exception as e:
            logger.error(f"Error creating A/B test: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def assign_user_to_variant(self, test_id: str, user_identifier: str) -> Dict[str, Any]:
        """Assign user to A/B test variant"""
        try:
            # Get test configuration
            test = self.get_ab_test(test_id)
            if not test or test.get('status') != 'active':
                return {'variant': 'control', 'reason': 'test_inactive'}
            
            # Check if user already assigned
            assignment_key = f"ab_assignment_{test_id}_{user_identifier}"
            existing_assignment = cache.get(assignment_key)
            
            if existing_assignment:
                return existing_assignment
            
            # Assign based on traffic split
            traffic_split = test.get('traffic_split', 50)
            
            # Use deterministic assignment based on user identifier
            user_hash = hash(user_identifier) % 100
            variant = 'variant' if user_hash < traffic_split else 'control'
            
            assignment = {
                'test_id': test_id,
                'user_identifier': user_identifier,
                'variant': variant,
                'assigned_at': timezone.now().isoformat(),
                'test_config': test['variants'][variant]['config']
            }
            
            # Cache assignment for test duration
            test_end = datetime.fromisoformat(test['end_date'].replace('Z', '+00:00'))
            cache_timeout = int((test_end - timezone.now()).total_seconds())
            cache.set(assignment_key, assignment, timeout=max(cache_timeout, 3600))
            
            logger.debug(f"Assigned user {user_identifier} to variant {variant} for test {test_id}")
            
            return assignment
            
        except Exception as e:
            logger.error(f"Error assigning user to A/B test variant: {str(e)}")
            return {'variant': 'control', 'reason': 'error'}
    
    def record_ab_test_event(self, test_id: str, user_identifier: str, event_type: str, event_data: Dict = None) -> bool:
        """Record A/B test event"""
        try:
            # Get user assignment
            assignment = self.assign_user_to_variant(test_id, user_identifier)
            variant = assignment.get('variant', 'control')
            
            # Get test
            test = self.get_ab_test(test_id)
            if not test:
                return False
            
            # Update test results
            if variant in test['results']:
                if event_type == 'view':
                    test['results'][variant]['views'] += 1
                elif event_type == 'conversion':
                    test['results'][variant]['conversions'] += 1
                elif event_type == 'interaction':
                    test['results'][variant]['interactions'] += 1
                elif event_type == 'time_spent':
                    time_spent = event_data.get('time_spent', 0) if event_data else 0
                    test['results'][variant]['total_time'] += time_spent
            
            # Update statistical significance
            test['statistical_significance'] = self._calculate_statistical_significance(test)
            
            # Save updated test
            cache_key = f"ab_test_{test_id}"
            cache.set(cache_key, test, timeout=86400 * 30)
            
            logger.debug(f"Recorded A/B test event: {test_id}, {variant}, {event_type}")
            
            return True
            
        except Exception as e:
            logger.error(f"Error recording A/B test event: {str(e)}")
            return False
    
    def get_ab_test(self, test_id: str) -> Optional[Dict[str, Any]]:
        """Get A/B test configuration and results"""
        try:
            cache_key = f"ab_test_{test_id}"
            return cache.get(cache_key)
        except Exception as e:
            logger.error(f"Error getting A/B test: {str(e)}")
            return None
    
    def get_active_tests_for_menu(self, menu_id: str) -> List[Dict[str, Any]]:
        """Get active A/B tests for a menu"""
        try:
            active_tests_key = f"active_ab_tests_{menu_id}"
            test_ids = cache.get(active_tests_key, [])
            
            active_tests = []
            for test_id in test_ids:
                test = self.get_ab_test(test_id)
                if test and test.get('status') == 'active':
                    # Check if test is still within date range
                    end_date = datetime.fromisoformat(test['end_date'].replace('Z', '+00:00'))
                    if timezone.now() <= end_date:
                        active_tests.append(test)
                    else:
                        # Test expired, mark as completed
                        test['status'] = 'completed'
                        cache_key = f"ab_test_{test_id}"
                        cache.set(cache_key, test, timeout=86400 * 30)
            
            return active_tests
            
        except Exception as e:
            logger.error(f"Error getting active A/B tests: {str(e)}")
            return []
    
    def _validate_test_config(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Validate A/B test configuration"""
        errors = []
        
        required_fields = ['name', 'type', 'menu_id', 'control_config', 'variant_config']
        for field in required_fields:
            if field not in config:
                errors.append(f"Missing required field: {field}")
        
        if 'traffic_split' in config:
            traffic_split = config['traffic_split']
            if not isinstance(traffic_split, (int, float)) or traffic_split < 1 or traffic_split > 99:
                errors.append("Traffic split must be between 1 and 99")
        
        valid_types = ['menu_layout', 'pricing', 'promotional', 'content']
        if config.get('type') not in valid_types:
            errors.append(f"Test type must be one of: {', '.join(valid_types)}")
        
        return {
            'valid': len(errors) == 0,
            'errors': errors
        }
    
    def _add_to_active_tests(self, test_id: str, menu_id: str):
        """Add test to active tests list"""
        try:
            active_tests_key = f"active_ab_tests_{menu_id}"
            current_tests = cache.get(active_tests_key, [])
            
            if test_id not in current_tests:
                current_tests.append(test_id)
                cache.set(active_tests_key, current_tests, timeout=86400 * 30)
                
        except Exception as e:
            logger.error(f"Error adding to active tests: {str(e)}")
    
    def _calculate_statistical_significance(self, test: Dict[str, Any]) -> bool:
        """Calculate statistical significance of A/B test results"""
        try:
            control_results = test['results']['control']
            variant_results = test['results']['variant']
            
            # Simple significance calculation (in production, use proper statistical tests)
            control_rate = control_results['conversions'] / max(control_results['views'], 1)
            variant_rate = variant_results['conversions'] / max(variant_results['views'], 1)
            
            # Minimum sample size check
            min_sample_size = 100
            if control_results['views'] < min_sample_size or variant_results['views'] < min_sample_size:
                return False
            
            # Simple difference threshold (replace with proper statistical test)
            difference = abs(variant_rate - control_rate)
            significance_threshold = 0.05  # 5% difference
            
            return difference >= significance_threshold
            
        except Exception as e:
            logger.error(f"Error calculating statistical significance: {str(e)}")
            return False
    
    def get_test_analytics(self, test_id: str) -> Dict[str, Any]:
        """Get comprehensive A/B test analytics"""
        try:
            test = self.get_ab_test(test_id)
            if not test:
                return {'error': 'Test not found'}
            
            control = test['results']['control']
            variant = test['results']['variant']
            
            # Calculate conversion rates
            control_conversion_rate = (control['conversions'] / max(control['views'], 1)) * 100
            variant_conversion_rate = (variant['conversions'] / max(variant['views'], 1)) * 100
            
            # Calculate average time spent
            control_avg_time = control['total_time'] / max(control['views'], 1)
            variant_avg_time = variant['total_time'] / max(variant['views'], 1)
            
            # Calculate interaction rates
            control_interaction_rate = (control['interactions'] / max(control['views'], 1)) * 100
            variant_interaction_rate = (variant['interactions'] / max(variant['views'], 1)) * 100
            
            # Determine winner
            winner = None
            if test['statistical_significance']:
                if variant_conversion_rate > control_conversion_rate:
                    winner = 'variant'
                elif control_conversion_rate > variant_conversion_rate:
                    winner = 'control'
            
            return {
                'test_id': test_id,
                'test_name': test['name'],
                'status': test['status'],
                'statistical_significance': test['statistical_significance'],
                'winner': winner,
                'control': {
                    'views': control['views'],
                    'conversions': control['conversions'],
                    'conversion_rate': round(control_conversion_rate, 2),
                    'avg_time_spent': round(control_avg_time, 2),
                    'interaction_rate': round(control_interaction_rate, 2)
                },
                'variant': {
                    'views': variant['views'],
                    'conversions': variant['conversions'],
                    'conversion_rate': round(variant_conversion_rate, 2),
                    'avg_time_spent': round(variant_avg_time, 2),
                    'interaction_rate': round(variant_interaction_rate, 2)
                },
                'improvement': {
                    'conversion_rate': round(variant_conversion_rate - control_conversion_rate, 2),
                    'avg_time_spent': round(variant_avg_time - control_avg_time, 2),
                    'interaction_rate': round(variant_interaction_rate - control_interaction_rate, 2)
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting test analytics: {str(e)}")
            return {'error': str(e)}


class MultiLanguageManager:
    """Advanced multi-language support for menu content"""
    
    def __init__(self):
        self.supported_languages = getattr(settings, 'SUPPORTED_LANGUAGES', [
            ('en', 'English'),
            ('es', 'Español'),
            ('fr', 'Français'),
            ('de', 'Deutsch'),
            ('it', 'Italiano'),
            ('pt', 'Português'),
            ('zh', '中文'),
            ('ja', '日本語'),
            ('ko', '한국어'),
            ('ar', 'العربية')
        ])
        self.default_language = getattr(settings, 'LANGUAGE_CODE', 'en')
    
    def get_supported_languages(self) -> List[Dict[str, str]]:
        """Get list of supported languages"""
        return [
            {'code': code, 'name': name, 'is_default': code == self.default_language}
            for code, name in self.supported_languages
        ]
    
    def translate_menu_content(self, menu_data: Dict[str, Any], target_language: str) -> Dict[str, Any]:
        """Translate menu content to target language"""
        try:
            # Cache translated content
            cache_key = f"translated_menu_{menu_data.get('menu_id')}_{target_language}"
            cached_translation = cache.get(cache_key)
            
            if cached_translation:
                logger.debug(f"Cache hit for menu translation: {target_language}")
                return cached_translation
            
            # Create translated copy
            translated_menu = menu_data.copy()
            
            # Translate menu fields
            translated_menu['name'] = self._translate_text(menu_data['name'], target_language)
            translated_menu['description'] = self._translate_text(menu_data.get('description', ''), target_language)
            
            # Translate categories
            if 'categories' in translated_menu:
                for category in translated_menu['categories']:
                    category['name'] = self._translate_text(category['name'], target_language)
                    category['description'] = self._translate_text(category.get('description', ''), target_language)
            
            # Translate menu items
            if 'items' in translated_menu:
                for item in translated_menu['items']:
                    item['name'] = self._translate_text(item['name'], target_language)
                    item['description'] = self._translate_text(item.get('description', ''), target_language)
                    
                    # Translate dietary information
                    if 'dietary_info' in item:
                        for key, value in item['dietary_info'].items():
                            if isinstance(value, str):
                                item['dietary_info'][key] = self._translate_text(value, target_language)
            
            # Add translation metadata
            translated_menu['translation'] = {
                'target_language': target_language,
                'translated_at': timezone.now().isoformat(),
                'translation_method': 'ai_assisted'
            }
            
            # Cache translation
            cache.set(cache_key, translated_menu, timeout=3600)  # 1 hour
            
            logger.info(f"Translated menu {menu_data.get('menu_id')} to {target_language}")
            
            return translated_menu
            
        except Exception as e:
            logger.error(f"Error translating menu content: {str(e)}")
            return menu_data
    
    def _translate_text(self, text: str, target_language: str) -> str:
        """Translate individual text using AI or translation service"""
        try:
            if not text or text.strip() == '':
                return text
            
            # Simple mock translation system - replace with actual translation service
            translations = {
                'es': {
                    'Menu': 'Menú',
                    'Appetizers': 'Aperitivos',
                    'Main Course': 'Plato Principal',
                    'Desserts': 'Postres',
                    'Beverages': 'Bebidas',
                    'Special': 'Especial',
                    'Available': 'Disponible',
                    'Unavailable': 'No disponible'
                },
                'fr': {
                    'Menu': 'Menu',
                    'Appetizers': 'Entrées',
                    'Main Course': 'Plat Principal',
                    'Desserts': 'Desserts',
                    'Beverages': 'Boissons',
                    'Special': 'Spécial',
                    'Available': 'Disponible',
                    'Unavailable': 'Indisponible'
                }
            }
            
            # Simple lookup translation (in production, use proper translation API)
            if target_language in translations and text in translations[target_language]:
                return translations[target_language][text]
            
            # For demo purposes, add language prefix
            if target_language != self.default_language:
                return f"[{target_language.upper()}] {text}"
            
            return text
            
        except Exception as e:
            logger.error(f"Error translating text '{text}': {str(e)}")
            return text
    
    def detect_user_language(self, request) -> str:
        """Detect user's preferred language"""
        try:
            # Check explicit language parameter
            lang_param = request.GET.get('lang') or request.POST.get('lang')
            if lang_param and self._is_supported_language(lang_param):
                return lang_param
            
            # Check user preferences (if authenticated)
            if hasattr(request, 'user') and request.user.is_authenticated:
                user_profile = getattr(request.user, 'profile', None)
                if user_profile and hasattr(user_profile, 'preferred_language'):
                    if self._is_supported_language(user_profile.preferred_language):
                        return user_profile.preferred_language
            
            # Check Accept-Language header
            accept_language = request.META.get('HTTP_ACCEPT_LANGUAGE', '')
            if accept_language:
                # Parse Accept-Language header
                for lang_range in accept_language.split(','):
                    lang_code = lang_range.split(';')[0].strip().split('-')[0]
                    if self._is_supported_language(lang_code):
                        return lang_code
            
            # Return default language
            return self.default_language
            
        except Exception as e:
            logger.error(f"Error detecting user language: {str(e)}")
            return self.default_language
    
    def _is_supported_language(self, language_code: str) -> bool:
        """Check if language is supported"""
        return language_code in [code for code, _ in self.supported_languages]


class AccessibilityEnhancer:
    """Accessibility features for menu displays"""
    
    def __init__(self):
        self.accessibility_features = [
            'high_contrast',
            'large_text',
            'screen_reader_support',
            'keyboard_navigation',
            'voice_commands',
            'color_blind_friendly'
        ]
    
    def enhance_menu_for_accessibility(self, menu_data: Dict[str, Any], accessibility_options: Dict[str, Any]) -> Dict[str, Any]:
        """Enhance menu data with accessibility features"""
        try:
            enhanced_menu = menu_data.copy()
            
            # Add accessibility metadata
            enhanced_menu['accessibility'] = {
                'features_enabled': [],
                'enhanced_at': timezone.now().isoformat(),
                'compliance_level': 'WCAG_2.1_AA'
            }
            
            # High contrast mode
            if accessibility_options.get('high_contrast', False):
                enhanced_menu['accessibility']['features_enabled'].append('high_contrast')
                enhanced_menu['display_options'] = enhanced_menu.get('display_options', {})
                enhanced_menu['display_options']['theme'] = 'high_contrast'
                enhanced_menu['display_options']['background_color'] = '#000000'
                enhanced_menu['display_options']['text_color'] = '#FFFFFF'
            
            # Large text mode
            if accessibility_options.get('large_text', False):
                enhanced_menu['accessibility']['features_enabled'].append('large_text')
                enhanced_menu['display_options'] = enhanced_menu.get('display_options', {})
                enhanced_menu['display_options']['font_size_multiplier'] = 1.5
                enhanced_menu['display_options']['line_height_multiplier'] = 1.4
            
            # Screen reader support
            if accessibility_options.get('screen_reader_support', False):
                enhanced_menu['accessibility']['features_enabled'].append('screen_reader_support')
                self._add_screen_reader_attributes(enhanced_menu)
            
            # Color blind friendly
            if accessibility_options.get('color_blind_friendly', False):
                enhanced_menu['accessibility']['features_enabled'].append('color_blind_friendly')
                self._apply_color_blind_friendly_palette(enhanced_menu)
            
            # Voice command support
            if accessibility_options.get('voice_commands', False):
                enhanced_menu['accessibility']['features_enabled'].append('voice_commands')
                self._add_voice_command_attributes(enhanced_menu)
            
            logger.info(f"Enhanced menu for accessibility: {enhanced_menu['accessibility']['features_enabled']}")
            
            return enhanced_menu
            
        except Exception as e:
            logger.error(f"Error enhancing menu for accessibility: {str(e)}")
            return menu_data
    
    def _add_screen_reader_attributes(self, menu_data: Dict[str, Any]):
        """Add screen reader specific attributes"""
        try:
            # Add ARIA labels and descriptions
            if 'items' in menu_data:
                for item in menu_data['items']:
                    # Create descriptive text for screen readers
                    description_parts = [item['name']]
                    
                    if item.get('price'):
                        description_parts.append(f"Price: ${item['price']}")
                    
                    if item.get('description'):
                        description_parts.append(item['description'])
                    
                    if item.get('dietary_info'):
                        dietary_labels = []
                        for key, value in item['dietary_info'].items():
                            if value:
                                dietary_labels.append(key.replace('_', ' ').title())
                        if dietary_labels:
                            description_parts.append(f"Dietary: {', '.join(dietary_labels)}")
                    
                    item['accessibility'] = {
                        'aria_label': item['name'],
                        'aria_description': '. '.join(description_parts),
                        'role': 'menuitem',
                        'tabindex': '0'
                    }
            
        except Exception as e:
            logger.error(f"Error adding screen reader attributes: {str(e)}")
    
    def _apply_color_blind_friendly_palette(self, menu_data: Dict[str, Any]):
        """Apply color blind friendly color palette"""
        try:
            # Color blind friendly palette
            color_palette = {
                'primary': '#1f77b4',      # Blue
                'secondary': '#ff7f0e',    # Orange
                'success': '#2ca02c',      # Green (adjusted)
                'warning': '#d62728',      # Red (adjusted)
                'info': '#9467bd',         # Purple
                'background': '#f7f7f7',   # Light gray
                'text': '#2c3e50'          # Dark gray
            }
            
            menu_data['display_options'] = menu_data.get('display_options', {})
            menu_data['display_options']['color_palette'] = color_palette
            menu_data['display_options']['use_patterns'] = True  # Use patterns in addition to colors
            
        except Exception as e:
            logger.error(f"Error applying color blind friendly palette: {str(e)}")
    
    def _add_voice_command_attributes(self, menu_data: Dict[str, Any]):
        """Add voice command support attributes"""
        try:
            voice_commands = {
                'navigation': [
                    'next item',
                    'previous item',
                    'go to category',
                    'show details',
                    'back to menu'
                ],
                'actions': [
                    'add to order',
                    'remove from order',
                    'view ingredients',
                    'check availability'
                ],
                'accessibility': [
                    'enable high contrast',
                    'increase text size',
                    'read description',
                    'repeat information'
                ]
            }
            
            menu_data['accessibility'] = menu_data.get('accessibility', {})
            menu_data['accessibility']['voice_commands'] = voice_commands
            
            # Add phonetic pronunciations for difficult item names
            if 'items' in menu_data:
                for item in menu_data['items']:
                    item_name = item['name'].lower()
                    # Simple phonetic mapping (expand as needed)
                    phonetic_mappings = {
                        'bruschetta': 'broo-sket-tah',
                        'quinoa': 'keen-wah',
                        'gnocchi': 'nyoh-kee',
                        'acai': 'ah-sigh-ee'
                    }
                    
                    if item_name in phonetic_mappings:
                        item['accessibility'] = item.get('accessibility', {})
                        item['accessibility']['phonetic'] = phonetic_mappings[item_name]
            
        except Exception as e:
            logger.error(f"Error adding voice command attributes: {str(e)}")
    
    def validate_accessibility_compliance(self, menu_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate menu accessibility compliance"""
        try:
            compliance_report = {
                'overall_score': 0,
                'compliance_level': 'none',
                'passed_checks': [],
                'failed_checks': [],
                'recommendations': []
            }
            
            checks = [
                ('color_contrast', self._check_color_contrast(menu_data)),
                ('text_size', self._check_text_size(menu_data)),
                ('alt_text', self._check_alt_text(menu_data)),
                ('keyboard_navigation', self._check_keyboard_navigation(menu_data)),
                ('screen_reader_support', self._check_screen_reader_support(menu_data))
            ]
            
            passed_count = 0
            for check_name, check_result in checks:
                if check_result['passed']:
                    compliance_report['passed_checks'].append(check_name)
                    passed_count += 1
                else:
                    compliance_report['failed_checks'].append({
                        'check': check_name,
                        'issue': check_result['issue'],
                        'recommendation': check_result['recommendation']
                    })
            
            # Calculate overall score
            compliance_report['overall_score'] = round((passed_count / len(checks)) * 100, 2)
            
            # Determine compliance level
            if compliance_report['overall_score'] >= 90:
                compliance_report['compliance_level'] = 'WCAG_2.1_AAA'
            elif compliance_report['overall_score'] >= 70:
                compliance_report['compliance_level'] = 'WCAG_2.1_AA'
            elif compliance_report['overall_score'] >= 50:
                compliance_report['compliance_level'] = 'WCAG_2.1_A'
            else:
                compliance_report['compliance_level'] = 'non_compliant'
            
            return compliance_report
            
        except Exception as e:
            logger.error(f"Error validating accessibility compliance: {str(e)}")
            return {'error': str(e)}
    
    def _check_color_contrast(self, menu_data: Dict[str, Any]) -> Dict[str, Any]:
        """Check color contrast compliance"""
        # Simplified check - in production, calculate actual contrast ratios
        display_options = menu_data.get('display_options', {})
        
        if 'color_palette' in display_options:
            return {'passed': True, 'details': 'Color palette configured'}
        else:
            return {
                'passed': False,
                'issue': 'No color palette specified',
                'recommendation': 'Configure color palette with sufficient contrast ratios'
            }
    
    def _check_text_size(self, menu_data: Dict[str, Any]) -> Dict[str, Any]:
        """Check text size accessibility"""
        display_options = menu_data.get('display_options', {})
        font_size = display_options.get('font_size_multiplier', 1.0)
        
        if font_size >= 1.2:
            return {'passed': True, 'details': f'Font size multiplier: {font_size}'}
        else:
            return {
                'passed': False,
                'issue': 'Text size may be too small',
                'recommendation': 'Consider increasing font size multiplier to at least 1.2'
            }
    
    def _check_alt_text(self, menu_data: Dict[str, Any]) -> Dict[str, Any]:
        """Check alternative text for images"""
        items_with_images = 0
        items_with_alt_text = 0
        
        if 'items' in menu_data:
            for item in menu_data['items']:
                if 'image' in item or 'image_url' in item:
                    items_with_images += 1
                    if item.get('accessibility', {}).get('alt_text'):
                        items_with_alt_text += 1
        
        if items_with_images == 0:
            return {'passed': True, 'details': 'No images found'}
        elif items_with_alt_text == items_with_images:
            return {'passed': True, 'details': f'Alt text provided for all {items_with_images} images'}
        else:
            return {
                'passed': False,
                'issue': f'Missing alt text for {items_with_images - items_with_alt_text} images',
                'recommendation': 'Add descriptive alt text for all menu item images'
            }
    
    def _check_keyboard_navigation(self, menu_data: Dict[str, Any]) -> Dict[str, Any]:
        """Check keyboard navigation support"""
        accessibility_features = menu_data.get('accessibility', {}).get('features_enabled', [])
        
        if 'keyboard_navigation' in accessibility_features:
            return {'passed': True, 'details': 'Keyboard navigation enabled'}
        else:
            return {
                'passed': False,
                'issue': 'Keyboard navigation not explicitly enabled',
                'recommendation': 'Enable keyboard navigation support'
            }
    
    def _check_screen_reader_support(self, menu_data: Dict[str, Any]) -> Dict[str, Any]:
        """Check screen reader support"""
        screen_reader_items = 0
        total_items = 0
        
        if 'items' in menu_data:
            total_items = len(menu_data['items'])
            for item in menu_data['items']:
                if item.get('accessibility', {}).get('aria_label'):
                    screen_reader_items += 1
        
        if total_items == 0:
            return {'passed': True, 'details': 'No items to check'}
        elif screen_reader_items == total_items:
            return {'passed': True, 'details': f'Screen reader support for all {total_items} items'}
        else:
            return {
                'passed': False,
                'issue': f'Missing screen reader support for {total_items - screen_reader_items} items',
                'recommendation': 'Add ARIA labels and descriptions for all menu items'
            }


# Global instances
ab_testing_engine = ABTestingEngine()
multi_language_manager = MultiLanguageManager()
accessibility_enhancer = AccessibilityEnhancer()