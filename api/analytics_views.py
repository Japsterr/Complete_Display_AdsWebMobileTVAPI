# Analytics API Views - Stage 5
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from django.core.cache import cache
from django.utils import timezone
from django.db import models
from datetime import datetime, timedelta
import json
import csv
import logging

from .analytics_engine import menu_analytics_engine, performance_monitor
from .analytics_models import (
    MenuViewAnalytics, MenuItemViewAnalytics, CampaignAnalytics, 
    SystemPerformanceLog, UserBehaviorAnalytics, APIUsageAnalytics
)
from .models import Menu, MenuItem, Campaign

logger = logging.getLogger(__name__)


class AnalyticsViewSet(viewsets.ViewSet):
    """Comprehensive analytics API endpoints"""
    
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['get'])
    def menu_performance(self, request):
        """Get menu performance analytics"""
        menu_id = request.query_params.get('menu_id')
        days = int(request.query_params.get('days', 7))
        
        if not menu_id:
            return Response({
                'error': 'menu_id parameter is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # Verify user has access to this menu
            menu = get_object_or_404(Menu, menu_id=menu_id)
            # Add permission check here if needed
            
            performance_data = menu_analytics_engine.get_menu_performance_summary(menu_id, days)
            
            return Response({
                'status': 'success',
                'data': performance_data
            })
            
        except Exception as e:
            logger.error(f"Menu performance analytics error: {str(e)}")
            return Response({
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['get'])
    def system_performance(self, request):
        """Get system performance metrics"""
        try:
            performance_data = performance_monitor.get_system_performance_metrics()
            
            return Response({
                'status': 'success',
                'data': performance_data
            })
            
        except Exception as e:
            logger.error(f"System performance analytics error: {str(e)}")
            return Response({
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['get'])
    def dashboard_summary(self, request):
        """Get dashboard summary with key metrics"""
        try:
            # Get user's menus
            user_menus = Menu.objects.filter(business__owner=request.user)
            
            if not user_menus.exists():
                return Response({
                    'status': 'success',
                    'data': {
                        'message': 'No menus found for user',
                        'total_menus': 0
                    }
                })
            
            # Aggregate metrics across all user menus
            days = int(request.query_params.get('days', 7))
            end_date = timezone.now()
            start_date = end_date - timedelta(days=days)
            
            summary_data = {
                'period': f'{days} days',
                'total_menus': user_menus.count(),
                'generated_at': timezone.now().isoformat(),
                'metrics': {
                    'total_views': 0,
                    'unique_viewers': 0,
                    'total_items': 0,
                    'active_campaigns': 0,
                    'avg_engagement': 0
                },
                'top_performing_menus': [],
                'recent_activity': [],
                'alerts': []
            }
            
            # Aggregate data for each menu
            menu_performance_list = []
            
            for menu in user_menus:
                try:
                    menu_perf = menu_analytics_engine.get_menu_performance_summary(menu.menu_id, days)
                    
                    if 'error' not in menu_perf:
                        summary_data['metrics']['total_views'] += menu_perf['summary']['total_views']
                        summary_data['metrics']['unique_viewers'] += menu_perf['summary']['unique_viewers']
                        summary_data['metrics']['total_items'] += menu_perf['summary']['total_items']
                        
                        menu_performance_list.append({
                            'menu_id': menu.menu_id,
                            'menu_name': menu.name,
                            'performance': menu_perf
                        })
                        
                except Exception as menu_error:
                    logger.warning(f"Error getting performance for menu {menu.menu_id}: {str(menu_error)}")
            
            # Get top performing menus
            menu_performance_list.sort(
                key=lambda x: x['performance']['summary']['total_views'], 
                reverse=True
            )
            summary_data['top_performing_menus'] = menu_performance_list[:5]
            
            # Get active campaigns
            active_campaigns = Campaign.objects.filter(
                menu_id__in=user_menus.values_list('menu_id', flat=True),
                start_date__lte=end_date,
                end_date__gte=start_date
            ).count()
            summary_data['metrics']['active_campaigns'] = active_campaigns
            
            # Calculate average engagement
            if summary_data['metrics']['total_views'] > 0:
                summary_data['metrics']['avg_engagement'] = round(
                    summary_data['metrics']['unique_viewers'] / summary_data['metrics']['total_views'] * 100, 2
                )
            
            # Get recent activity
            recent_views = MenuViewAnalytics.objects.filter(
                menu_id__in=user_menus.values_list('menu_id', flat=True),
                timestamp__gte=start_date
            ).order_by('-timestamp')[:10]
            
            summary_data['recent_activity'] = [
                {
                    'menu_id': view.menu_id,
                    'timestamp': view.timestamp.isoformat(),
                    'view_count': view.view_count,
                    'is_promotional': view.is_promotional
                }
                for view in recent_views
            ]
            
            # Generate alerts based on performance
            alerts = self._generate_performance_alerts(menu_performance_list)
            summary_data['alerts'] = alerts
            
            return Response({
                'status': 'success',
                'data': summary_data
            })
            
        except Exception as e:
            logger.error(f"Dashboard summary error: {str(e)}")
            return Response({
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def _generate_performance_alerts(self, menu_performance_list):
        """Generate performance alerts based on analytics"""
        alerts = []
        
        for menu_data in menu_performance_list:
            performance = menu_data['performance']
            menu_name = menu_data['menu_name']
            
            # Low engagement alert
            if performance['summary']['total_views'] < 10:
                alerts.append({
                    'type': 'low_engagement',
                    'severity': 'warning',
                    'menu_id': menu_data['menu_id'],
                    'message': f'Menu "{menu_name}" has low viewership ({performance["summary"]["total_views"]} views)'
                })
            
            # POS sync issues
            pos_stats = performance.get('pos_sync_stats', {})
            if pos_stats.get('sync_enabled') and pos_stats.get('success_rate', 100) < 80:
                alerts.append({
                    'type': 'pos_sync_issue',
                    'severity': 'error',
                    'menu_id': menu_data['menu_id'],
                    'message': f'Menu "{menu_name}" has POS sync issues (Success rate: {pos_stats.get("success_rate", 0)}%)'
                })
            
            # Campaign performance
            campaign_impact = performance.get('campaign_impact', {})
            if campaign_impact.get('campaigns_active', 0) > 0:
                avg_effectiveness = campaign_impact.get('avg_campaign_effectiveness', 0)
                if avg_effectiveness < 30:
                    alerts.append({
                        'type': 'poor_campaign_performance',
                        'severity': 'warning',
                        'menu_id': menu_data['menu_id'],
                        'message': f'Menu "{menu_name}" campaigns are underperforming (Effectiveness: {avg_effectiveness}%)'
                    })
        
        return alerts
    
    @action(detail=False, methods=['get'])
    def export_analytics(self, request):
        """Export analytics data as CSV"""
        export_type = request.query_params.get('type', 'menu_views')
        menu_id = request.query_params.get('menu_id')
        days = int(request.query_params.get('days', 30))
        
        try:
            if export_type == 'menu_views':
                return self._export_menu_views(menu_id, days)
            elif export_type == 'item_performance':
                return self._export_item_performance(menu_id, days)
            elif export_type == 'campaign_analytics':
                return self._export_campaign_analytics(menu_id, days)
            else:
                return Response({
                    'error': 'Invalid export type. Options: menu_views, item_performance, campaign_analytics'
                }, status=status.HTTP_400_BAD_REQUEST)
                
        except Exception as e:
            logger.error(f"Export analytics error: {str(e)}")
            return Response({
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def _export_menu_views(self, menu_id, days):
        """Export menu view analytics as CSV"""
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="menu_views_{menu_id}_{days}days.csv"'
        
        writer = csv.writer(response)
        writer.writerow([
            'Timestamp', 'Menu ID', 'Viewer IP', 'View Count', 
            'Is Promotional', 'Campaign ID', 'Device Type', 'Referrer'
        ])
        
        end_date = timezone.now()
        start_date = end_date - timedelta(days=days)
        
        views = MenuViewAnalytics.objects.filter(
            menu_id=menu_id,
            timestamp__gte=start_date
        ).order_by('-timestamp')
        
        for view in views:
            writer.writerow([
                view.timestamp.isoformat(),
                view.menu_id,
                view.viewer_ip,
                view.view_count,
                view.is_promotional,
                view.campaign_id or '',
                view.device_type or '',
                view.referrer or ''
            ])
        
        return response
    
    def _export_item_performance(self, menu_id, days):
        """Export item performance analytics as CSV"""
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="item_performance_{menu_id}_{days}days.csv"'
        
        writer = csv.writer(response)
        writer.writerow([
            'Item ID', 'Item Name', 'Category', 'Price', 'Total Views', 
            'Unique Viewers', 'Avg View Duration', 'Promotional Views', 'Popularity Score'
        ])
        
        # Get performance data
        performance_data = menu_analytics_engine.get_menu_performance_summary(menu_id, days)
        
        if 'error' not in performance_data:
            for item in performance_data.get('item_performance', []):
                writer.writerow([
                    item['item_id'],
                    item['name'],
                    item['category'] or '',
                    item['price'],
                    item['total_views'],
                    item['unique_viewers'],
                    item['avg_view_duration'],
                    item['promotional_views'],
                    item['popularity_score']
                ])
        
        return response
    
    def _export_campaign_analytics(self, menu_id, days):
        """Export campaign analytics as CSV"""
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="campaign_analytics_{menu_id}_{days}days.csv"'
        
        writer = csv.writer(response)
        writer.writerow([
            'Campaign ID', 'Campaign Name', 'Type', 'Views', 
            'Duration Days', 'Effectiveness Score'
        ])
        
        # Get campaign data
        performance_data = menu_analytics_engine.get_menu_performance_summary(menu_id, days)
        
        if 'error' not in performance_data:
            campaign_impact = performance_data.get('campaign_impact', {})
            for campaign in campaign_impact.get('campaign_performance', []):
                writer.writerow([
                    campaign['campaign_id'],
                    campaign['name'],
                    campaign['type'],
                    campaign['views'],
                    campaign['duration_days'],
                    campaign['effectiveness_score']
                ])
        
        return response
    
    @action(detail=False, methods=['post'])
    def track_view(self, request):
        """Track a menu view event"""
        menu_id = request.data.get('menu_id')
        
        if not menu_id:
            return Response({
                'error': 'menu_id is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # Get client information
            ip_address = self._get_client_ip(request)
            user_agent = request.META.get('HTTP_USER_AGENT', '')
            referrer = request.META.get('HTTP_REFERER')
            
            # Create or update view record
            view_record, created = MenuViewAnalytics.objects.get_or_create(
                menu_id=menu_id,
                viewer_ip=ip_address,
                defaults={
                    'viewer_user_agent': user_agent,
                    'view_count': 1,
                    'is_promotional': request.data.get('is_promotional', False),
                    'campaign_id': request.data.get('campaign_id'),
                    'referrer': referrer,
                    'device_type': request.data.get('device_type')
                }
            )
            
            if not created:
                # Update existing record
                view_record.view_count += 1
                view_record.save()
            
            return Response({
                'status': 'success',
                'message': 'View tracked successfully',
                'view_count': view_record.view_count
            })
            
        except Exception as e:
            logger.error(f"Track view error: {str(e)}")
            return Response({
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['post'])
    def track_item_view(self, request):
        """Track a menu item view event"""
        item_id = request.data.get('item_id')
        view_duration = request.data.get('view_duration', 0)
        
        if not item_id:
            return Response({
                'error': 'item_id is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # Get menu item
            menu_item = get_object_or_404(MenuItem, item_id=item_id)
            
            # Get client information
            ip_address = self._get_client_ip(request)
            user_agent = request.META.get('HTTP_USER_AGENT', '')
            
            # Create or update item view record
            item_view, created = MenuItemViewAnalytics.objects.get_or_create(
                menu_item=menu_item,
                viewer_ip=ip_address,
                defaults={
                    'viewer_user_agent': user_agent,
                    'view_count': 1,
                    'avg_view_duration_seconds': view_duration,
                    'is_promotional': request.data.get('is_promotional', False),
                    'campaign_id': request.data.get('campaign_id'),
                    'view_position': request.data.get('view_position')
                }
            )
            
            if not created:
                # Update existing record with average
                total_duration = (item_view.avg_view_duration_seconds * item_view.view_count) + view_duration
                item_view.view_count += 1
                item_view.avg_view_duration_seconds = total_duration / item_view.view_count
                item_view.save()
            
            return Response({
                'status': 'success',
                'message': 'Item view tracked successfully',
                'view_count': item_view.view_count
            })
            
        except Exception as e:
            logger.error(f"Track item view error: {str(e)}")
            return Response({
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def _get_client_ip(self, request):
        """Get client IP address from request"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
    
    @action(detail=False, methods=['get'])
    def real_time_metrics(self, request):
        """Get real-time metrics for dashboard"""
        try:
            # Get metrics for the last hour
            one_hour_ago = timezone.now() - timedelta(hours=1)
            
            # Real-time view counts
            recent_views = MenuViewAnalytics.objects.filter(
                timestamp__gte=one_hour_ago
            ).aggregate(
                total_views=models.Sum('view_count'),
                unique_ips=models.Count('viewer_ip', distinct=True)
            )
            
            # Active campaigns
            active_campaigns = Campaign.objects.filter(
                start_date__lte=timezone.now(),
                end_date__gte=timezone.now()
            ).count()
            
            # System health
            system_performance = performance_monitor.get_system_performance_metrics()
            
            return Response({
                'status': 'success',
                'data': {
                    'timestamp': timezone.now().isoformat(),
                    'recent_views': recent_views['total_views'] or 0,
                    'unique_viewers_hour': recent_views['unique_ips'] or 0,
                    'active_campaigns': active_campaigns,
                    'system_health': system_performance.get('overall_health', 'unknown')
                }
            })
            
        except Exception as e:
            logger.error(f"Real-time metrics error: {str(e)}")
            return Response({
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)