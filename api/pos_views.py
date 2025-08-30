# Enhanced POS Integration Views - Stage 4
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views import View
from django.core.cache import cache
import json
import logging

from .models import POSIntegration, Menu, POSUpdateLog
from .serializers import POSIntegrationSerializer
from .pos_sync_manager import POSSyncManager, WebhookManager

logger = logging.getLogger(__name__)


class POSIntegrationViewSet(viewsets.ModelViewSet):
    """Enhanced POS Integration management with advanced sync capabilities"""
    
    serializer_class = POSIntegrationSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return POSIntegration.objects.filter(
            created_by=self.request.user
        ).select_related('created_by').prefetch_related('pos_update_logs')
    
    @action(detail=True, methods=['post'])
    def test_connection(self, request, pk=None):
        """Test POS system connection and credentials"""
        pos_integration = self.get_object()
        sync_manager = POSSyncManager()
        
        try:
            # Test connection by fetching a small amount of data
            pos_items = sync_manager._fetch_pos_items(pos_integration)
            
            if pos_items:
                return Response({
                    'status': 'success',
                    'message': 'Connection successful',
                    'items_found': len(pos_items),
                    'sample_items': list(pos_items.values())[:3]  # First 3 items as sample
                })
            else:
                return Response({
                    'status': 'error',
                    'message': 'Failed to fetch data from POS system'
                }, status=status.HTTP_400_BAD_REQUEST)
                
        except Exception as e:
            logger.error(f"POS connection test failed: {str(e)}")
            return Response({
                'status': 'error',
                'message': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def sync_menu(self, request, pk=None):
        """Trigger bidirectional sync between menu and POS"""
        pos_integration = self.get_object()
        menu_id = request.data.get('menu_id')
        
        if not menu_id:
            return Response({
                'error': 'menu_id is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Verify menu exists and user has access
        try:
            menu = Menu.objects.get(menu_id=menu_id)
            # Add access control here if needed
        except Menu.DoesNotExist:
            return Response({
                'error': 'Menu not found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        sync_manager = POSSyncManager()
        
        try:
            result = sync_manager.sync_menu_bidirectional(menu_id, pos_integration.id)
            
            return Response({
                'status': 'success',
                'sync_result': result,
                'message': f'Sync completed: {result.get("menu_to_pos_updates", 0)} menu→POS, {result.get("pos_to_menu_updates", 0)} POS→menu updates'
            })
            
        except Exception as e:
            logger.error(f"Menu sync failed: {str(e)}")
            return Response({
                'status': 'error',
                'message': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=True, methods=['post'])
    def setup_webhooks(self, request, pk=None):
        """Setup webhooks for real-time POS updates"""
        pos_integration = self.get_object()
        webhook_manager = WebhookManager()
        
        try:
            success = webhook_manager.setup_pos_webhooks(pos_integration)
            
            if success:
                return Response({
                    'status': 'success',
                    'message': 'Webhooks configured successfully',
                    'webhook_id': pos_integration.webhook_id
                })
            else:
                return Response({
                    'status': 'error',
                    'message': 'Failed to setup webhooks'
                }, status=status.HTTP_400_BAD_REQUEST)
                
        except Exception as e:
            logger.error(f"Webhook setup failed: {str(e)}")
            return Response({
                'status': 'error',
                'message': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=True, methods=['get'])
    def sync_status(self, request, pk=None):
        """Get current sync status and recent activity"""
        pos_integration = self.get_object()
        
        # Get recent sync logs
        recent_logs = POSUpdateLog.objects.filter(
            pos_integration=pos_integration
        ).order_by('-created_at')[:10]
        
        # Get cached sync status
        cache_key = f"pos_sync_status_{pk}"
        cached_status = cache.get(cache_key)
        
        # Calculate sync statistics
        total_syncs = POSUpdateLog.objects.filter(
            pos_integration=pos_integration,
            operation__in=['bidirectional_sync', 'manual_sync']
        ).count()
        
        successful_syncs = POSUpdateLog.objects.filter(
            pos_integration=pos_integration,
            operation__in=['bidirectional_sync', 'manual_sync'],
            success=True
        ).count()
        
        success_rate = (successful_syncs / total_syncs * 100) if total_syncs > 0 else 0
        
        return Response({
            'pos_integration_id': pos_integration.id,
            'pos_system': pos_integration.pos_system,
            'last_sync': recent_logs[0].created_at if recent_logs else None,
            'sync_statistics': {
                'total_syncs': total_syncs,
                'successful_syncs': successful_syncs,
                'success_rate': round(success_rate, 2)
            },
            'recent_activity': [
                {
                    'operation': log.operation,
                    'success': log.success,
                    'timestamp': log.created_at,
                    'details': json.loads(log.details) if log.details else None
                }
                for log in recent_logs
            ],
            'cached_status': cached_status,
            'webhook_configured': bool(pos_integration.webhook_id)
        })
    
    @action(detail=True, methods=['get'])
    def sync_conflicts(self, request, pk=None):
        """Get recent sync conflicts and their resolutions"""
        pos_integration = self.get_object()
        
        conflict_logs = POSUpdateLog.objects.filter(
            pos_integration=pos_integration,
            operation='conflict_resolution'
        ).order_by('-created_at')[:20]
        
        conflicts = []
        for log in conflict_logs:
            try:
                conflict_data = json.loads(log.details)
                conflicts.append({
                    'timestamp': log.created_at,
                    'conflict_type': conflict_data.get('conflict', {}).get('type'),
                    'resolution': conflict_data.get('resolution'),
                    'menu_item_id': conflict_data.get('conflict', {}).get('menu_item_id'),
                    'pos_item_id': conflict_data.get('conflict', {}).get('pos_item_id'),
                    'winning_value': conflict_data.get('winning_value')
                })
            except (json.JSONDecodeError, KeyError):
                pass
        
        return Response({
            'conflicts': conflicts,
            'total_conflicts': len(conflicts),
            'resolution_strategy': pos_integration.conflict_resolution_strategy
        })
    
    @action(detail=True, methods=['post'])
    def update_conflict_strategy(self, request, pk=None):
        """Update conflict resolution strategy"""
        pos_integration = self.get_object()
        new_strategy = request.data.get('strategy')
        
        valid_strategies = ['pos_wins', 'menu_wins', 'latest_wins', 'manual']
        
        if new_strategy not in valid_strategies:
            return Response({
                'error': f'Invalid strategy. Must be one of: {", ".join(valid_strategies)}'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        pos_integration.conflict_resolution_strategy = new_strategy
        pos_integration.save()
        
        return Response({
            'status': 'success',
            'message': f'Conflict resolution strategy updated to: {new_strategy}',
            'strategy': new_strategy
        })
    
    @action(detail=False, methods=['get'])
    def supported_systems(self, request):
        """Get list of supported POS systems and their capabilities"""
        systems = {
            'square': {
                'name': 'Square',
                'features': ['bidirectional_sync', 'webhooks', 'conflict_resolution', 'auto_create'],
                'auth_method': 'oauth_bearer',
                'webhook_events': ['catalog.version.updated', 'inventory.count.updated'],
                'sync_frequency': 'real-time'
            },
            'toast': {
                'name': 'Toast POS',
                'features': ['bidirectional_sync', 'webhooks', 'conflict_resolution'],
                'auth_method': 'api_key',
                'webhook_events': ['menu.updated'],
                'sync_frequency': 'real-time'
            },
            'lightspeed': {
                'name': 'Lightspeed',
                'features': ['bidirectional_sync', 'conflict_resolution'],
                'auth_method': 'oauth_bearer',
                'webhook_events': [],
                'sync_frequency': 'polling'
            },
            'shopify': {
                'name': 'Shopify POS',
                'features': ['bidirectional_sync', 'webhooks', 'conflict_resolution', 'auto_create'],
                'auth_method': 'access_token',
                'webhook_events': ['products/update', 'products/create'],
                'sync_frequency': 'real-time'
            },
            'generic': {
                'name': 'Generic REST API',
                'features': ['bidirectional_sync', 'conflict_resolution'],
                'auth_method': 'configurable',
                'webhook_events': ['configurable'],
                'sync_frequency': 'polling'
            }
        }
        
        return Response({
            'supported_systems': systems,
            'total_systems': len(systems)
        })
    
    @action(detail=True, methods=['post'])
    def force_resync(self, request, pk=None):
        """Force a complete resynchronization, ignoring timestamps"""
        pos_integration = self.get_object()
        menu_id = request.data.get('menu_id')
        
        if not menu_id:
            return Response({
                'error': 'menu_id is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # Clear sync timestamps to force full resync
            from .models import MenuItemPOSSync
            MenuItemPOSSync.objects.filter(
                menu_item__menu_id=menu_id
            ).update(last_pos_update=None)
            
            # Perform sync
            sync_manager = POSSyncManager()
            result = sync_manager.sync_menu_bidirectional(menu_id, pos_integration.id)
            
            return Response({
                'status': 'success',
                'message': 'Force resync completed',
                'sync_result': result
            })
            
        except Exception as e:
            logger.error(f"Force resync failed: {str(e)}")
            return Response({
                'status': 'error',
                'message': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@method_decorator(csrf_exempt, name='dispatch')
class POSWebhookView(View):
    """Handle incoming webhooks from POS systems"""
    
    def post(self, request, pos_integration_id):
        """Process incoming webhook"""
        try:
            webhook_data = json.loads(request.body.decode('utf-8'))
            
            # Verify POS integration exists
            pos_integration = get_object_or_404(POSIntegration, id=pos_integration_id)
            
            # Process webhook
            webhook_manager = WebhookManager()
            result = webhook_manager.process_webhook(pos_integration_id, webhook_data)
            
            logger.info(f"Webhook processed for POS {pos_integration_id}: {result}")
            
            return HttpResponse(
                json.dumps(result),
                content_type='application/json',
                status=200
            )
            
        except json.JSONDecodeError:
            logger.error("Invalid JSON in webhook")
            return HttpResponse(
                json.dumps({'error': 'Invalid JSON'}),
                content_type='application/json',
                status=400
            )
        except Exception as e:
            logger.error(f"Webhook processing error: {str(e)}")
            return HttpResponse(
                json.dumps({'error': str(e)}),
                content_type='application/json',
                status=500
            )
    
    def get(self, request, pos_integration_id):
        """Handle webhook verification (for some POS systems)"""
        # Some POS systems send GET requests to verify webhook endpoints
        challenge = request.GET.get('challenge')
        if challenge:
            return HttpResponse(challenge, content_type='text/plain')
        
        return HttpResponse('Webhook endpoint active', content_type='text/plain')


class POSUpdateLogViewSet(viewsets.ReadOnlyModelViewSet):
    """View POS update logs and sync history"""
    
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return POSUpdateLog.objects.filter(
            pos_integration__created_by=self.request.user
        ).select_related('pos_integration').order_by('-created_at')
    
    def list(self, request):
        """List recent POS update logs with filtering"""
        queryset = self.get_queryset()
        
        # Apply filters
        pos_integration_id = request.query_params.get('pos_integration')
        operation = request.query_params.get('operation')
        success = request.query_params.get('success')
        
        if pos_integration_id:
            queryset = queryset.filter(pos_integration_id=pos_integration_id)
        
        if operation:
            queryset = queryset.filter(operation=operation)
        
        if success is not None:
            queryset = queryset.filter(success=success.lower() == 'true')
        
        # Paginate
        page = int(request.query_params.get('page', 1))
        page_size = int(request.query_params.get('page_size', 20))
        start = (page - 1) * page_size
        end = start + page_size
        
        logs = queryset[start:end]
        total = queryset.count()
        
        return Response({
            'logs': [
                {
                    'id': log.id,
                    'pos_integration': {
                        'id': log.pos_integration.id,
                        'name': log.pos_integration.name,
                        'pos_system': log.pos_integration.pos_system
                    },
                    'operation': log.operation,
                    'success': log.success,
                    'created_at': log.created_at,
                    'details': json.loads(log.details) if log.details else None
                }
                for log in logs
            ],
            'pagination': {
                'page': page,
                'page_size': page_size,
                'total': total,
                'pages': (total + page_size - 1) // page_size
            }
        })
    
    @action(detail=False, methods=['get'])
    def summary(self, request):
        """Get summary statistics for POS sync operations"""
        from django.db.models import Count, Q
        from datetime import datetime, timedelta
        
        # Get stats for last 30 days
        thirty_days_ago = datetime.now() - timedelta(days=30)
        
        queryset = self.get_queryset().filter(created_at__gte=thirty_days_ago)
        
        stats = queryset.aggregate(
            total_operations=Count('id'),
            successful_operations=Count('id', filter=Q(success=True)),
            failed_operations=Count('id', filter=Q(success=False)),
            sync_operations=Count('id', filter=Q(operation__contains='sync')),
            webhook_operations=Count('id', filter=Q(operation='webhook_received')),
            conflict_resolutions=Count('id', filter=Q(operation='conflict_resolution'))
        )
        
        # Calculate success rate
        if stats['total_operations'] > 0:
            stats['success_rate'] = round(
                (stats['successful_operations'] / stats['total_operations']) * 100, 2
            )
        else:
            stats['success_rate'] = 0
        
        # Get operation breakdown
        operation_breakdown = queryset.values('operation').annotate(
            count=Count('id')
        ).order_by('-count')
        
        # Get daily activity
        daily_activity = []
        for i in range(7):  # Last 7 days
            date = datetime.now().date() - timedelta(days=i)
            day_count = queryset.filter(
                created_at__date=date
            ).count()
            daily_activity.append({
                'date': date.isoformat(),
                'operations': day_count
            })
        
        return Response({
            'summary': stats,
            'operation_breakdown': list(operation_breakdown),
            'daily_activity': daily_activity
        })