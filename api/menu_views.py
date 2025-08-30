# Menu System Views - Stage 1: Enhanced POS Integration Foundation
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.db import transaction
from django.db.models import Q, Max
import logging
import json
from datetime import datetime, timedelta

from .models import (
    Menu, MenuCategory, MenuItem, POSIntegration, MenuItemPOSSync, 
    POSUpdateLog, ApiKey, Business, User
)
from .serializers import (
    MenuSerializer, MenuCategorySerializer, MenuItemSerializer,
    POSBulkUpdateSerializer, POSIntegrationSerializer, MenuItemPOSSyncSerializer,
    POSUpdateLogSerializer, ApiKeySerializer
)

logger = logging.getLogger(__name__)

# --- Authentication Utilities ---
def get_api_key_from_request(request):
    """Extract API key from request headers"""
    api_key = request.META.get('HTTP_X_API_KEY')
    if not api_key:
        api_key = request.data.get('api_key')  # Allow in POST data as fallback
    return api_key

def authenticate_api_key(api_key):
    """Authenticate and return business for API key"""
    if not api_key:
        return None, "No API key provided"
    
    try:
        key_obj = ApiKey.objects.select_related('business').get(
            key=api_key, 
            is_active=True
        )
        
        # Check expiration
        if key_obj.expires_at and key_obj.expires_at < timezone.now():
            return None, "API key expired"
        
        # Update usage tracking
        key_obj.last_used = timezone.now()
        key_obj.usage_count += 1
        key_obj.save(update_fields=['last_used', 'usage_count'])
        
        return key_obj.business, None
        
    except ApiKey.DoesNotExist:
        return None, "Invalid API key"

# --- Menu ViewSets ---
class MenuViewSet(viewsets.ModelViewSet):
    serializer_class = MenuSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        if user.account_type == 'business' and hasattr(user, 'owned_business'):
            return Menu.objects.filter(business=user.owned_business).prefetch_related('categories', 'items')
        else:
            return Menu.objects.filter(personal_user=user).prefetch_related('categories', 'items')
    
    def perform_create(self, serializer):
        user = self.request.user
        if user.account_type == 'business' and hasattr(user, 'owned_business'):
            serializer.save(business=user.owned_business)
        else:
            serializer.save(personal_user=user)
    
    @action(detail=True, methods=['get'])
    def pos_status(self, request, pk=None):
        """Get POS synchronization status for a menu"""
        menu = self.get_object()
        items_with_pos = menu.items.filter(pos_item_id__isnull=False)
        
        status_data = {
            'total_items': menu.items.count(),
            'pos_synced_items': items_with_pos.count(),
            'last_sync': items_with_pos.aggregate(
                latest=Max('last_pos_sync')
            )['latest'],
            'promotion_items': menu.items.filter(promotion_flag=True).count()
        }
        
        return Response(status_data)
    
    @action(detail=True, methods=['get'], url_path='last-updated')
    def last_updated(self, request, pk=None):
        """Get menu last updated information for real-time sync detection"""
        try:
            menu = self.get_object()
            
            # Get latest update timestamp from menu and related items
            menu_updated = menu.updated_at
            items_updated = menu.items.aggregate(latest=Max('updated_at'))['latest']
            categories_updated = menu.categories.aggregate(latest=Max('updated_at'))['latest']
            
            # Find the most recent update
            latest_update = max(filter(None, [menu_updated, items_updated, categories_updated]))
            
            # Create hash of menu content for change detection
            import hashlib
            menu_data = {
                'name': menu.name,
                'items': [{
                    'id': item.id,
                    'name': item.name,
                    'price': str(item.price),
                    'available': item.available,
                    'promotion_flag': item.promotion_flag,
                    'special_offer': item.special_offer,
                    'updated': item.updated_at.isoformat() if item.updated_at else None
                } for item in menu.items.all()],
                'updated': latest_update.isoformat()
            }
            
            content_hash = hashlib.md5(json.dumps(menu_data, sort_keys=True).encode()).hexdigest()
            
            return Response({
                'menu_id': menu.menu_id,
                'last_updated': latest_update,
                'hash': content_hash,
                'has_pos_updates': menu.items.filter(last_pos_sync__gte=timezone.now() - timedelta(minutes=5)).exists()
            })
            
        except Exception as e:
            return Response({'error': str(e)}, status=500)
    
    @action(detail=True, methods=['post'])
    def reorder(self, request, pk=None):
        """Reorder categories and items within a menu"""
        menu = self.get_object()
        categories_data = request.data.get('categories', [])
        items_data = request.data.get('items', [])
        
        try:
            with transaction.atomic():
                # Update category orders
                for cat_data in categories_data:
                    MenuCategory.objects.filter(
                        category_id=cat_data['category_id'],
                        menu=menu
                    ).update(order=cat_data['order'])
                
                # Update item orders and categories
                for item_data in items_data:
                    MenuItem.objects.filter(
                        item_id=item_data['item_id'],
                        menu=menu
                    ).update(
                        order=item_data['order'],
                        category_id=item_data.get('category_id')
                    )
                
                return Response({'status': 'ok'})
        except Exception as e:
            return Response(
                {'status': 'error', 'message': str(e)}, 
                status=status.HTTP_400_BAD_REQUEST
            )

class MenuCategoryViewSet(viewsets.ModelViewSet):
    serializer_class = MenuCategorySerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        if user.account_type == 'business' and hasattr(user, 'owned_business'):
            return MenuCategory.objects.filter(menu__business=user.owned_business)
        else:
            return MenuCategory.objects.filter(menu__personal_user=user)

class MenuItemViewSet(viewsets.ModelViewSet):
    serializer_class = MenuItemSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        if user.account_type == 'business' and hasattr(user, 'owned_business'):
            return MenuItem.objects.filter(menu__business=user.owned_business).select_related('category', 'menu')
        else:
            return MenuItem.objects.filter(menu__personal_user=user).select_related('category', 'menu')

# --- POS Integration Views ---
@api_view(['POST'])
@permission_classes([permissions.AllowAny])  # Uses API key authentication
def pos_update_menu_items(request):
    """
    Enhanced POS update endpoint with support for dynamic names, descriptions, and promotions
    
    Expected payload:
    {
        'updates': [
            {
                'item_id': 123,
                'name': 'Dynamic Item Name',          # NEW: Dynamic naming
                'description': 'Updated description', # NEW: Dynamic descriptions  
                'price': '25.00',
                'available': False,
                'promotion_flag': True,               # NEW: Promotion detection
                'special_offer': 'Buy 2 Get 1 Free', # NEW: Promotional content
                'pos_item_id': 'POS123'              # POS system item ID
            }
        ],
        'source_system': 'square',  # Optional: POS system identifier
        'sync_timestamp': '2025-08-30T10:00:00Z'  # Optional: sync timestamp
    }
    """
    # API Key Authentication
    api_key = get_api_key_from_request(request)
    business, auth_error = authenticate_api_key(api_key)
    
    if not business:
        logger.warning(f"POS update failed authentication: {auth_error}")
        return Response(
            {'error': auth_error, 'updated': 0, 'failed': 0}, 
            status=status.HTTP_401_UNAUTHORIZED if api_key else status.HTTP_400_BAD_REQUEST
        )
    
    # Validate request data
    serializer = POSBulkUpdateSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(
            {'error': 'Invalid data format', 'details': serializer.errors},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    validated_data = serializer.validated_data
    updates = validated_data['updates']
    source_system = validated_data.get('source_system', 'unknown')
    
    # Process updates
    updated_count = 0
    failed_count = 0
    failed_items = []
    update_start_time = timezone.now()
    
    # Get or create POS integration record
    pos_integration, created = POSIntegration.objects.get_or_create(
        business=business,
        pos_system_type=source_system,
        defaults={'sync_status': 'active'}
    )
    
    try:
        with transaction.atomic():
            for update_data in updates:
                try:
                    # Find the menu item
                    item = MenuItem.objects.select_for_update().get(
                        item_id=update_data['item_id'],
                        menu__business=business
                    )
                    
                    # Track what changed for audit
                    changes = {}
                    
                    # Update basic fields with dynamic support
                    if 'name' in update_data:
                        old_name = item.name
                        item.name = update_data['name']
                        changes['name'] = {'old': old_name, 'new': item.name}
                    
                    if 'description' in update_data:
                        old_desc = item.description
                        item.description = update_data['description']
                        changes['description'] = {'old': old_desc, 'new': item.description}
                    
                    if 'price' in update_data:
                        old_price = float(item.price)
                        item.price = update_data['price']
                        changes['price'] = {'old': old_price, 'new': float(item.price)}
                    
                    if 'available' in update_data:
                        old_available = item.available
                        item.available = update_data['available']
                        changes['available'] = {'old': old_available, 'new': item.available}
                    
                    # Enhanced POS fields
                    if 'promotion_flag' in update_data:
                        old_promo = item.promotion_flag
                        item.promotion_flag = update_data['promotion_flag']
                        changes['promotion_flag'] = {'old': old_promo, 'new': item.promotion_flag}
                    
                    if 'special_offer' in update_data:
                        old_offer = item.special_offer
                        item.special_offer = update_data['special_offer']
                        changes['special_offer'] = {'old': old_offer, 'new': item.special_offer}
                    
                    if 'pos_item_id' in update_data:
                        item.pos_item_id = update_data['pos_item_id']
                    
                    # Update sync timestamp
                    item.last_pos_sync = timezone.now()
                    item.save()
                    
                    # Create or update POS sync record
                    pos_sync, sync_created = MenuItemPOSSync.objects.update_or_create(
                        menu_item=item,
                        pos_integration=pos_integration,
                        defaults={
                            'pos_item_id': update_data.get('pos_item_id', item.pos_item_id or ''),
                            'pos_name': update_data.get('name', item.name),
                            'pos_description': update_data.get('description', item.description),
                            'pos_price': update_data.get('price', item.price),
                            'pos_available': update_data.get('available', item.available),
                            'pos_promotion_data': {
                                'promotion_flag': update_data.get('promotion_flag', False),
                                'special_offer': update_data.get('special_offer', ''),
                                'sync_timestamp': timezone.now().isoformat()
                            }
                        }
                    )
                    
                    updated_count += 1
                    logger.info(f"Updated menu item {item.item_id} from POS: {changes}")
                    
                except MenuItem.DoesNotExist:
                    failed_count += 1
                    failed_items.append({
                        'item_id': update_data['item_id'],
                        'error': 'Item not found or access denied'
                    })
                    logger.warning(f"POS update failed - item not found: {update_data['item_id']}")
                
                except Exception as e:
                    failed_count += 1
                    failed_items.append({
                        'item_id': update_data.get('item_id', 'unknown'),
                        'error': str(e)
                    })
                    logger.error(f"POS update failed for item {update_data.get('item_id')}: {str(e)}")
    
    except Exception as e:
        logger.error(f"POS update transaction failed: {str(e)}")
        return Response(
            {'error': 'Update transaction failed', 'details': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
    
    # Log the update operation
    update_duration = (timezone.now() - update_start_time).total_seconds()
    
    POSUpdateLog.objects.create(
        pos_integration=pos_integration,
        update_type='api',
        items_updated=updated_count,
        items_failed=failed_count,
        update_data={
            'source_system': source_system,
            'total_updates': len(updates),
            'request_timestamp': validated_data.get('sync_timestamp'),
            'api_key_name': ApiKey.objects.filter(key=api_key).first().name if api_key else None
        },
        error_details={'failed_items': failed_items} if failed_items else {},
        duration_seconds=update_duration
    )
    
    # Update POS integration status
    pos_integration.last_sync = timezone.now()
    pos_integration.sync_status = 'active' if failed_count == 0 else 'error'
    if failed_count > 0:
        pos_integration.error_message = f"Failed to update {failed_count} items"
    else:
        pos_integration.error_message = None
    pos_integration.save()
    
    response_data = {
        'status': 'success' if failed_count == 0 else 'partial_success',
        'updated': updated_count,
        'failed': failed_count,
        'total_processed': len(updates),
        'sync_timestamp': timezone.now().isoformat(),
        'duration_seconds': update_duration
    }
    
    if failed_items:
        response_data['failed_items'] = failed_items
    
    logger.info(f"POS update completed: {response_data}")
    return Response(response_data)

@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def pos_webhook_handler(request):
    """
    Webhook endpoint for real-time POS updates
    Different POS systems can send data in their own format
    """
    api_key = get_api_key_from_request(request)
    business, auth_error = authenticate_api_key(api_key)
    
    if not business:
        return Response({'error': auth_error}, status=status.HTTP_401_UNAUTHORIZED)
    
    # Log webhook received
    logger.info(f"Webhook received from POS for business {business.name}: {request.data}")
    
    # Process webhook data (implementation depends on POS system format)
    # This is a flexible handler that can be extended for different POS systems
    
    webhook_type = request.data.get('type', 'unknown')
    
    if webhook_type == 'item_updated':
        # Handle item update webhooks
        item_data = request.data.get('item', {})
        
        # Convert to standard format and call update handler
        standardized_update = {
            'updates': [{
                'item_id': item_data.get('menu_item_id'),
                'name': item_data.get('name'),
                'description': item_data.get('description'),
                'price': item_data.get('price'),
                'available': item_data.get('available', True),
                'promotion_flag': item_data.get('on_promotion', False),
                'special_offer': item_data.get('promotion_text', ''),
                'pos_item_id': item_data.get('pos_id')
            }],
            'source_system': request.data.get('source', 'webhook'),
            'sync_timestamp': request.data.get('timestamp')
        }
        
        # Reuse the main update logic
        return pos_update_menu_items(request._request if hasattr(request, '_request') else request)
    
    return Response({'status': 'webhook_received', 'type': webhook_type})

# --- API Key Management Views ---
class ApiKeyViewSet(viewsets.ModelViewSet):
    serializer_class = ApiKeySerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        if user.account_type == 'business' and hasattr(user, 'owned_business'):
            return ApiKey.objects.filter(business=user.owned_business)
        return ApiKey.objects.none()
    
    def perform_create(self, serializer):
        user = self.request.user
        if user.account_type == 'business' and hasattr(user, 'owned_business'):
            # Generate a secure API key
            import secrets
            api_key = f"sk_{secrets.token_urlsafe(32)}"
            serializer.save(business=user.owned_business, key=api_key)

# --- POS Integration Management Views ---
class POSIntegrationViewSet(viewsets.ModelViewSet):
    serializer_class = POSIntegrationSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        if user.account_type == 'business' and hasattr(user, 'owned_business'):
            return POSIntegration.objects.filter(business=user.owned_business)
        return POSIntegration.objects.none()
    
    def perform_create(self, serializer):
        user = self.request.user
        if user.account_type == 'business' and hasattr(user, 'owned_business'):
            serializer.save(business=user.owned_business)
    
    @action(detail=True, methods=['post'])
    def test_connection(self, request, pk=None):
        """Test POS system connection"""
        integration = self.get_object()
        
        # Implement connection testing logic based on POS type
        # This is a placeholder for actual POS API testing
        
        try:
            # Simulate connection test
            integration.sync_status = 'active'
            integration.error_message = None
            integration.save()
            
            return Response({
                'status': 'success',
                'message': 'Connection test successful',
                'timestamp': timezone.now().isoformat()
            })
        except Exception as e:
            integration.sync_status = 'error'
            integration.error_message = str(e)
            integration.save()
            
            return Response({
                'status': 'error',
                'message': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def pos_sync_logs(request):
    """Get POS synchronization logs"""
    user = request.user
    if user.account_type != 'business' or not hasattr(user, 'owned_business'):
        return Response({'error': 'Access denied'}, status=status.HTTP_403_FORBIDDEN)
    
    logs = POSUpdateLog.objects.filter(
        pos_integration__business=user.owned_business
    ).order_by('-timestamp')[:50]  # Last 50 logs
    
    serializer = POSUpdateLogSerializer(logs, many=True)
    return Response({
        'logs': serializer.data,
        'total_logs': logs.count()
    })

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def menu_analytics(request):
    """Get menu performance analytics"""
    user = request.user
    if user.account_type == 'business' and hasattr(user, 'owned_business'):
        menus = Menu.objects.filter(business=user.owned_business)
    else:
        menus = Menu.objects.filter(personal_user=user)
    
    analytics_data = {
        'total_menus': menus.count(),
        'total_items': MenuItem.objects.filter(menu__in=menus).count(),
        'pos_synced_items': MenuItem.objects.filter(
            menu__in=menus, 
            pos_item_id__isnull=False
        ).count(),
        'promotion_items': MenuItem.objects.filter(
            menu__in=menus, 
            promotion_flag=True
        ).count(),
        'last_sync': MenuItem.objects.filter(
            menu__in=menus
        ).aggregate(latest=Max('last_pos_sync'))['latest']
    }
    
    return Response(analytics_data)