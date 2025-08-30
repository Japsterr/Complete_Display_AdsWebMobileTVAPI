# Advanced Error Handling for POS Synchronization - Stage 4
import logging
import traceback
import json
import time
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from django.core.cache import cache
from django.core.mail import send_mail
from django.conf import settings

logger = logging.getLogger(__name__)


class POSErrorHandler:
    """Comprehensive error handling and recovery for POS operations"""
    
    def __init__(self):
        self.error_counts = {}
        self.circuit_breakers = {}
    
    def handle_sync_error(self, pos_integration_id: int, error: Exception, operation: str) -> Dict[str, Any]:
        """Handle synchronization errors with intelligent recovery"""
        error_key = f"pos_error_{pos_integration_id}_{operation}"
        
        # Increment error count
        current_count = cache.get(error_key, 0) + 1
        cache.set(error_key, current_count, timeout=3600)  # Reset hourly
        
        error_info = {
            'error_type': type(error).__name__,
            'error_message': str(error),
            'error_count': current_count,
            'operation': operation,
            'pos_integration_id': pos_integration_id,
            'timestamp': datetime.now().isoformat(),
            'traceback': traceback.format_exc()
        }
        
        # Determine severity and recovery action
        if current_count >= 5:
            # Circuit breaker - disable integration temporarily
            self._activate_circuit_breaker(pos_integration_id, operation)
            error_info['action'] = 'circuit_breaker_activated'
            error_info['severity'] = 'critical'
            
            # Send alert
            self._send_error_alert(pos_integration_id, error_info)
            
        elif current_count >= 3:
            # Escalating error - switch to backup strategy
            error_info['action'] = 'backup_strategy'
            error_info['severity'] = 'high'
            
        else:
            # Retry with exponential backoff
            error_info['action'] = 'retry_with_backoff'
            error_info['severity'] = 'medium'
        
        # Log error with appropriate level
        if error_info['severity'] == 'critical':
            logger.critical(f"Critical POS error: {error_info}")
        elif error_info['severity'] == 'high':
            logger.error(f"High priority POS error: {error_info}")
        else:
            logger.warning(f"POS sync error: {error_info}")
        
        return error_info
    
    def _activate_circuit_breaker(self, pos_integration_id: int, operation: str):
        """Activate circuit breaker for problematic integration"""
        breaker_key = f"circuit_breaker_{pos_integration_id}_{operation}"
        
        # Disable for 30 minutes
        cache.set(breaker_key, {
            'activated_at': datetime.now().isoformat(),
            'reason': 'multiple_failures',
            'disabled_until': (datetime.now() + timedelta(minutes=30)).isoformat()
        }, timeout=1800)
        
        logger.critical(f"Circuit breaker activated for POS {pos_integration_id}, operation: {operation}")
    
    def is_circuit_breaker_active(self, pos_integration_id: int, operation: str) -> bool:
        """Check if circuit breaker is active for an integration"""
        breaker_key = f"circuit_breaker_{pos_integration_id}_{operation}"
        breaker_info = cache.get(breaker_key)
        
        if not breaker_info:
            return False
        
        # Check if still disabled
        disabled_until = datetime.fromisoformat(breaker_info['disabled_until'])
        if datetime.now() < disabled_until:
            return True
        
        # Circuit breaker expired
        cache.delete(breaker_key)
        return False
    
    def _send_error_alert(self, pos_integration_id: int, error_info: Dict[str, Any]):
        """Send alert email for critical errors"""
        try:
            from api.models import POSIntegration
            pos_integration = POSIntegration.objects.get(id=pos_integration_id)
            
            subject = f"Critical POS Sync Error - {pos_integration.name}"
            message = f"""
Critical error in POS synchronization:

POS Integration: {pos_integration.name} ({pos_integration.pos_system})
Operation: {error_info['operation']}
Error: {error_info['error_message']}
Error Count: {error_info['error_count']}
Time: {error_info['timestamp']}

Action Taken: {error_info['action']}

Please check the POS integration configuration and logs.
            """
            
            # Send to admin emails (configured in settings)
            admin_emails = getattr(settings, 'ADMIN_EMAILS', [])
            if admin_emails:
                send_mail(
                    subject,
                    message,
                    settings.DEFAULT_FROM_EMAIL,
                    admin_emails,
                    fail_silently=True
                )
                
        except Exception as e:
            logger.error(f"Failed to send error alert: {str(e)}")
    
    def get_error_statistics(self, pos_integration_id: int) -> Dict[str, Any]:
        """Get error statistics for a POS integration"""
        try:
            from api.models import POSUpdateLog
            
            # Get error logs from last 24 hours
            twenty_four_hours_ago = datetime.now() - timedelta(hours=24)
            error_logs = POSUpdateLog.objects.filter(
                pos_integration_id=pos_integration_id,
                success=False,
                created_at__gte=twenty_four_hours_ago
            )
            
            # Categorize errors
            error_categories = {}
            total_errors = 0
            
            for log in error_logs:
                total_errors += 1
                try:
                    details = json.loads(log.details) if log.details else {}
                    error_type = details.get('error_type', 'Unknown')
                    
                    if error_type not in error_categories:
                        error_categories[error_type] = {
                            'count': 0,
                            'latest': None,
                            'operations': set()
                        }
                    
                    error_categories[error_type]['count'] += 1
                    error_categories[error_type]['latest'] = log.created_at
                    error_categories[error_type]['operations'].add(log.operation)
                    
                except json.JSONDecodeError:
                    pass
            
            # Convert sets to lists for JSON serialization
            for category in error_categories:
                error_categories[category]['operations'] = list(error_categories[category]['operations'])
            
            # Check circuit breaker status
            circuit_breakers = []
            operations = ['sync', 'webhook', 'fetch']
            for operation in operations:
                if self.is_circuit_breaker_active(pos_integration_id, operation):
                    breaker_key = f"circuit_breaker_{pos_integration_id}_{operation}"
                    breaker_info = cache.get(breaker_key)
                    circuit_breakers.append({
                        'operation': operation,
                        'activated_at': breaker_info.get('activated_at'),
                        'disabled_until': breaker_info.get('disabled_until')
                    })
            
            return {
                'pos_integration_id': pos_integration_id,
                'period': '24_hours',
                'total_errors': total_errors,
                'error_categories': error_categories,
                'circuit_breakers': circuit_breakers,
                'health_status': self._calculate_health_status(total_errors, circuit_breakers)
            }
            
        except Exception as e:
            logger.error(f"Error getting statistics: {str(e)}")
            return {
                'error': str(e),
                'pos_integration_id': pos_integration_id
            }
    
    def _calculate_health_status(self, total_errors: int, circuit_breakers: list) -> str:
        """Calculate overall health status"""
        if circuit_breakers:
            return 'critical'
        elif total_errors > 20:
            return 'poor'
        elif total_errors > 5:
            return 'warning'
        else:
            return 'good'
    
    def reset_error_count(self, pos_integration_id: int, operation: str = None):
        """Reset error count for integration (manual recovery)"""
        if operation:
            error_key = f"pos_error_{pos_integration_id}_{operation}"
            cache.delete(error_key)
            
            # Also clear circuit breaker if active
            breaker_key = f"circuit_breaker_{pos_integration_id}_{operation}"
            cache.delete(breaker_key)
            
            logger.info(f"Reset error count for POS {pos_integration_id}, operation: {operation}")
        else:
            # Reset all operations for this integration
            operations = ['sync', 'webhook', 'fetch', 'bidirectional_sync']
            for op in operations:
                self.reset_error_count(pos_integration_id, op)
            
            logger.info(f"Reset all error counts for POS {pos_integration_id}")
    
    def get_recovery_suggestions(self, pos_integration_id: int) -> Dict[str, Any]:
        """Get automated recovery suggestions"""
        try:
            from api.models import POSIntegration
            
            pos_integration = POSIntegration.objects.get(id=pos_integration_id)
            error_stats = self.get_error_statistics(pos_integration_id)
            
            suggestions = []
            
            # Check for common error patterns
            error_categories = error_stats.get('error_categories', {})
            
            if 'ConnectionError' in error_categories:
                suggestions.append({
                    'type': 'connection',
                    'priority': 'high',
                    'suggestion': 'Check POS system connectivity and API endpoint availability',
                    'action': 'test_connection'
                })
            
            if 'AuthenticationError' in error_categories:
                suggestions.append({
                    'type': 'authentication',
                    'priority': 'high',
                    'suggestion': 'Verify API credentials and refresh tokens if necessary',
                    'action': 'refresh_credentials'
                })
            
            if 'RateLimitError' in error_categories:
                suggestions.append({
                    'type': 'rate_limit',
                    'priority': 'medium',
                    'suggestion': 'Reduce sync frequency or implement request throttling',
                    'action': 'adjust_sync_frequency'
                })
            
            if 'ValidationError' in error_categories:
                suggestions.append({
                    'type': 'data_validation',
                    'priority': 'medium',
                    'suggestion': 'Review data mapping and field validation rules',
                    'action': 'validate_data_mapping'
                })
            
            # Check for performance issues
            if error_stats.get('total_errors', 0) > 10:
                suggestions.append({
                    'type': 'performance',
                    'priority': 'medium',
                    'suggestion': 'Consider implementing caching or reducing data volume',
                    'action': 'optimize_performance'
                })
            
            # Circuit breaker suggestions
            if error_stats.get('circuit_breakers'):
                suggestions.append({
                    'type': 'circuit_breaker',
                    'priority': 'critical',
                    'suggestion': 'Circuit breaker is active. Manual intervention required.',
                    'action': 'manual_reset'
                })
            
            return {
                'pos_integration_id': pos_integration_id,
                'pos_system': pos_integration.pos_system,
                'health_status': error_stats.get('health_status', 'unknown'),
                'suggestions': suggestions,
                'auto_recovery_available': len([s for s in suggestions if s['action'] != 'manual_reset']) > 0
            }
            
        except Exception as e:
            logger.error(f"Error generating recovery suggestions: {str(e)}")
            return {
                'error': str(e),
                'pos_integration_id': pos_integration_id
            }


class POSRetryHandler:
    """Handle retry logic with exponential backoff"""
    
    def __init__(self):
        self.max_retries = 3
        self.base_delay = 1  # seconds
        self.max_delay = 60  # seconds
    
    def execute_with_retry(self, func, *args, **kwargs):
        """Execute function with retry logic"""
        last_exception = None
        
        for attempt in range(self.max_retries + 1):
            try:
                return func(*args, **kwargs)
                
            except Exception as e:
                last_exception = e
                
                if attempt < self.max_retries:
                    delay = min(self.base_delay * (2 ** attempt), self.max_delay)
                    logger.warning(f"Retry attempt {attempt + 1} failed: {str(e)}. Retrying in {delay}s")
                    time.sleep(delay)
                else:
                    logger.error(f"All retry attempts failed: {str(e)}")
                    raise
        
        # This shouldn't be reached, but just in case
        raise last_exception


class POSDataValidator:
    """Validate POS data integrity and consistency"""
    
    @staticmethod
    def validate_menu_item(menu_item_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate menu item data"""
        errors = []
        warnings = []
        
        # Required fields
        required_fields = ['name', 'price']
        for field in required_fields:
            if not menu_item_data.get(field):
                errors.append(f"Missing required field: {field}")
        
        # Price validation
        price = menu_item_data.get('price')
        if price is not None:
            try:
                price_value = float(price)
                if price_value < 0:
                    errors.append("Price cannot be negative")
                elif price_value > 1000:
                    warnings.append("Price seems unusually high")
            except (ValueError, TypeError):
                errors.append("Invalid price format")
        
        # Name validation
        name = menu_item_data.get('name')
        if name and len(name) > 200:
            errors.append("Name too long (max 200 characters)")
        
        # Description validation
        description = menu_item_data.get('description')
        if description and len(description) > 1000:
            warnings.append("Description is very long")
        
        return {
            'valid': len(errors) == 0,
            'errors': errors,
            'warnings': warnings
        }
    
    @staticmethod
    def validate_pos_response(response_data: Dict[str, Any], expected_structure: Dict[str, Any]) -> Dict[str, Any]:
        """Validate POS API response structure"""
        errors = []
        
        def check_structure(data, structure, path=""):
            for key, expected_type in structure.items():
                current_path = f"{path}.{key}" if path else key
                
                if key not in data:
                    errors.append(f"Missing field: {current_path}")
                    continue
                
                value = data[key]
                
                if isinstance(expected_type, dict):
                    if not isinstance(value, dict):
                        errors.append(f"Field {current_path} should be an object")
                    else:
                        check_structure(value, expected_type, current_path)
                elif isinstance(expected_type, list):
                    if not isinstance(value, list):
                        errors.append(f"Field {current_path} should be an array")
                elif not isinstance(value, expected_type):
                    errors.append(f"Field {current_path} should be {expected_type.__name__}")
        
        check_structure(response_data, expected_structure)
        
        return {
            'valid': len(errors) == 0,
            'errors': errors
        }


# Global error handler instance
pos_error_handler = POSErrorHandler()
pos_retry_handler = POSRetryHandler()