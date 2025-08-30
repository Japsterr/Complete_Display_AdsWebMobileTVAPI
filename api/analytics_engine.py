# Stage 5: Analytics & Performance Optimization System
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from django.core.cache import cache
from django.db import models
from django.db.models import Count, Avg, Sum, F, Q
from django.utils import timezone
from decimal import Decimal

logger = logging.getLogger(__name__)


class MenuAnalyticsEngine:
    """Advanced analytics engine for menu performance and user behavior"""
    
    def __init__(self):
        self.cache_timeout = 300  # 5 minutes
    
    def get_menu_performance_summary(self, menu_id: str, days: int = 7) -> Dict[str, Any]:
        """Get comprehensive menu performance summary"""
        cache_key = f"menu_performance_{menu_id}_{days}"
        cached_result = cache.get(cache_key)
        
        if cached_result:
            logger.debug(f"Cache hit for menu performance: {menu_id}")
            return cached_result
        
        end_date = timezone.now()
        start_date = end_date - timedelta(days=days)
        
        # Import here to avoid circular imports
        from api.models import Menu, MenuItem, MenuViewAnalytics, POSUpdateLog
        
        try:
            menu = Menu.objects.get(menu_id=menu_id)
            
            # Basic menu stats
            total_items = MenuItem.objects.filter(menu=menu).count()
            active_items = MenuItem.objects.filter(menu=menu, is_available=True).count()
            
            # View analytics
            total_views = MenuViewAnalytics.objects.filter(
                menu_id=menu_id,
                timestamp__gte=start_date
            ).aggregate(total=Sum('view_count'))['total'] or 0
            
            unique_viewers = MenuViewAnalytics.objects.filter(
                menu_id=menu_id,
                timestamp__gte=start_date
            ).values('viewer_ip').distinct().count()
            
            # Item performance
            item_performance = self._get_item_performance(menu_id, start_date, end_date)
            
            # POS sync performance
            pos_sync_stats = self._get_pos_sync_stats(menu_id, start_date, end_date)
            
            # Promotional campaign impact
            campaign_impact = self._get_campaign_impact(menu_id, start_date, end_date)
            
            # Peak viewing times
            peak_times = self._get_peak_viewing_times(menu_id, start_date, end_date)
            
            result = {
                'menu_id': menu_id,
                'period': f'{days} days',
                'generated_at': timezone.now().isoformat(),
                'summary': {
                    'total_items': total_items,
                    'active_items': active_items,
                    'total_views': total_views,
                    'unique_viewers': unique_viewers,
                    'avg_views_per_day': round(total_views / days, 2) if days > 0 else 0,
                    'items_availability_rate': round((active_items / total_items * 100), 2) if total_items > 0 else 0
                },
                'item_performance': item_performance,
                'pos_sync_stats': pos_sync_stats,
                'campaign_impact': campaign_impact,
                'peak_times': peak_times,
                'recommendations': self._generate_recommendations(menu_id, item_performance, campaign_impact)
            }
            
            # Cache result
            cache.set(cache_key, result, self.cache_timeout)
            logger.info(f"Generated menu performance summary for {menu_id}")
            
            return result
            
        except Menu.DoesNotExist:
            logger.error(f"Menu not found: {menu_id}")
            return {'error': 'Menu not found'}
        except Exception as e:
            logger.error(f"Error generating menu performance: {str(e)}")
            return {'error': str(e)}
    
    def _get_item_performance(self, menu_id: str, start_date: datetime, end_date: datetime) -> List[Dict[str, Any]]:
        """Get individual item performance metrics"""
        from api.models import MenuItem, MenuItemViewAnalytics
        
        items = MenuItem.objects.filter(menu__menu_id=menu_id)
        performance = []
        
        for item in items:
            # Get view analytics for this item
            item_views = MenuItemViewAnalytics.objects.filter(
                menu_item=item,
                timestamp__gte=start_date,
                timestamp__lte=end_date
            ).aggregate(
                total_views=Sum('view_count'),
                unique_viewers=Count('viewer_ip', distinct=True),
                avg_view_duration=Avg('avg_view_duration_seconds')
            )
            
            # Price change impact
            price_changes = self._get_price_change_impact(item, start_date, end_date)
            
            # Promotional impact
            promotional_views = MenuItemViewAnalytics.objects.filter(
                menu_item=item,
                timestamp__gte=start_date,
                timestamp__lte=end_date,
                is_promotional=True
            ).aggregate(promo_views=Sum('view_count'))['promo_views'] or 0
            
            performance.append({
                'item_id': item.item_id,
                'name': item.name,
                'price': float(item.price),
                'category': item.category.name if item.category else None,
                'is_available': item.is_available,
                'total_views': item_views['total_views'] or 0,
                'unique_viewers': item_views['unique_viewers'] or 0,
                'avg_view_duration': float(item_views['avg_view_duration'] or 0),
                'promotional_views': promotional_views,
                'promotional_conversion_rate': round(
                    (promotional_views / (item_views['total_views'] or 1)) * 100, 2
                ),
                'price_change_impact': price_changes,
                'popularity_score': self._calculate_popularity_score(item_views, promotional_views)
            })
        
        # Sort by popularity score
        performance.sort(key=lambda x: x['popularity_score'], reverse=True)
        
        return performance
    
    def _get_price_change_impact(self, item, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Analyze impact of price changes on item performance"""
        from api.models import POSUpdateLog, MenuItemPOSSync
        
        try:
            # Get price change events from POS sync logs
            pos_sync = MenuItemPOSSync.objects.filter(menu_item=item).first()
            if not pos_sync:
                return {'changes': 0, 'impact': 'no_data'}
            
            price_changes = POSUpdateLog.objects.filter(
                pos_integration=pos_sync.pos_integration,
                operation__in=['bidirectional_sync', 'manual_sync'],
                success=True,
                created_at__gte=start_date,
                created_at__lte=end_date,
                details__icontains=item.item_id
            ).count()
            
            # Calculate impact (simplified)
            if price_changes > 0:
                # Get views before and after price changes
                mid_date = start_date + (end_date - start_date) / 2
                
                from api.models import MenuItemViewAnalytics
                views_before = MenuItemViewAnalytics.objects.filter(
                    menu_item=item,
                    timestamp__gte=start_date,
                    timestamp__lt=mid_date
                ).aggregate(total=Sum('view_count'))['total'] or 0
                
                views_after = MenuItemViewAnalytics.objects.filter(
                    menu_item=item,
                    timestamp__gte=mid_date,
                    timestamp__lte=end_date
                ).aggregate(total=Sum('view_count'))['total'] or 0
                
                if views_before > 0:
                    change_percentage = ((views_after - views_before) / views_before) * 100
                    impact = 'positive' if change_percentage > 5 else 'negative' if change_percentage < -5 else 'neutral'
                else:
                    impact = 'no_baseline'
                    change_percentage = 0
                
                return {
                    'changes': price_changes,
                    'impact': impact,
                    'view_change_percentage': round(change_percentage, 2)
                }
            
            return {'changes': 0, 'impact': 'no_changes'}
            
        except Exception as e:
            logger.error(f"Error analyzing price change impact: {str(e)}")
            return {'changes': 0, 'impact': 'error'}
    
    def _get_pos_sync_stats(self, menu_id: str, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Get POS synchronization statistics"""
        from api.models import POSUpdateLog, MenuItemPOSSync, MenuItem
        
        try:
            # Get menu items
            menu_items = MenuItem.objects.filter(menu__menu_id=menu_id)
            
            # Get POS sync records for these items
            pos_syncs = MenuItemPOSSync.objects.filter(menu_item__in=menu_items)
            
            if not pos_syncs.exists():
                return {
                    'sync_enabled': False,
                    'message': 'No POS integration configured'
                }
            
            # Get sync logs in date range
            pos_integrations = pos_syncs.values_list('pos_integration', flat=True).distinct()
            
            sync_logs = POSUpdateLog.objects.filter(
                pos_integration__in=pos_integrations,
                created_at__gte=start_date,
                created_at__lte=end_date
            )
            
            total_syncs = sync_logs.count()
            successful_syncs = sync_logs.filter(success=True).count()
            failed_syncs = sync_logs.filter(success=False).count()
            
            # Sync frequency analysis
            sync_frequency = self._calculate_sync_frequency(sync_logs, start_date, end_date)
            
            # Recent sync status
            recent_sync = sync_logs.order_by('-created_at').first()
            
            return {
                'sync_enabled': True,
                'total_syncs': total_syncs,
                'successful_syncs': successful_syncs,
                'failed_syncs': failed_syncs,
                'success_rate': round((successful_syncs / total_syncs * 100), 2) if total_syncs > 0 else 0,
                'sync_frequency': sync_frequency,
                'last_sync': recent_sync.created_at.isoformat() if recent_sync else None,
                'last_sync_success': recent_sync.success if recent_sync else None
            }
            
        except Exception as e:
            logger.error(f"Error getting POS sync stats: {str(e)}")
            return {'error': str(e)}
    
    def _calculate_sync_frequency(self, sync_logs, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Calculate sync frequency patterns"""
        if not sync_logs.exists():
            return {'avg_interval_hours': 0, 'pattern': 'no_data'}
        
        # Group syncs by day
        daily_syncs = {}
        for log in sync_logs.order_by('created_at'):
            day = log.created_at.date()
            if day not in daily_syncs:
                daily_syncs[day] = []
            daily_syncs[day].append(log.created_at)
        
        # Calculate average interval between syncs
        intervals = []
        for day, syncs in daily_syncs.items():
            if len(syncs) > 1:
                for i in range(1, len(syncs)):
                    interval = (syncs[i] - syncs[i-1]).total_seconds() / 3600  # hours
                    intervals.append(interval)
        
        if intervals:
            avg_interval = sum(intervals) / len(intervals)
            
            # Determine pattern
            if avg_interval < 0.25:  # Less than 15 minutes
                pattern = 'very_frequent'
            elif avg_interval < 1:  # Less than 1 hour
                pattern = 'frequent'
            elif avg_interval < 6:  # Less than 6 hours
                pattern = 'regular'
            else:
                pattern = 'infrequent'
            
            return {
                'avg_interval_hours': round(avg_interval, 2),
                'pattern': pattern,
                'total_intervals': len(intervals)
            }
        
        return {'avg_interval_hours': 0, 'pattern': 'insufficient_data'}
    
    def _get_campaign_impact(self, menu_id: str, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Analyze promotional campaign impact"""
        from api.models import Campaign, MenuViewAnalytics
        
        try:
            # Get campaigns for this menu
            campaigns = Campaign.objects.filter(
                menu_id=menu_id,
                start_date__lte=end_date,
                end_date__gte=start_date
            )
            
            if not campaigns.exists():
                return {
                    'campaigns_active': 0,
                    'message': 'No campaigns in date range'
                }
            
            total_campaigns = campaigns.count()
            
            # Calculate campaign performance
            campaign_performance = []
            total_campaign_views = 0
            
            for campaign in campaigns:
                # Get views during campaign period
                campaign_views = MenuViewAnalytics.objects.filter(
                    menu_id=menu_id,
                    timestamp__gte=max(campaign.start_date, start_date),
                    timestamp__lte=min(campaign.end_date, end_date),
                    is_promotional=True
                ).aggregate(total=Sum('view_count'))['total'] or 0
                
                total_campaign_views += campaign_views
                
                campaign_performance.append({
                    'campaign_id': campaign.id,
                    'name': campaign.name,
                    'type': campaign.campaign_type,
                    'views': campaign_views,
                    'duration_days': (campaign.end_date - campaign.start_date).days,
                    'effectiveness_score': self._calculate_campaign_effectiveness(campaign, campaign_views)
                })
            
            # Overall campaign impact
            total_views = MenuViewAnalytics.objects.filter(
                menu_id=menu_id,
                timestamp__gte=start_date,
                timestamp__lte=end_date
            ).aggregate(total=Sum('view_count'))['total'] or 0
            
            campaign_conversion_rate = round(
                (total_campaign_views / total_views * 100), 2
            ) if total_views > 0 else 0
            
            return {
                'campaigns_active': total_campaigns,
                'total_campaign_views': total_campaign_views,
                'campaign_conversion_rate': campaign_conversion_rate,
                'campaign_performance': campaign_performance,
                'avg_campaign_effectiveness': round(
                    sum(c['effectiveness_score'] for c in campaign_performance) / len(campaign_performance), 2
                ) if campaign_performance else 0
            }
            
        except Exception as e:
            logger.error(f"Error analyzing campaign impact: {str(e)}")
            return {'error': str(e)}
    
    def _calculate_campaign_effectiveness(self, campaign, campaign_views: int) -> float:
        """Calculate campaign effectiveness score (0-100)"""
        try:
            # Base score from views
            view_score = min(campaign_views / 100, 50)  # Max 50 points for views
            
            # Duration score (longer campaigns get penalty)
            duration_days = (campaign.end_date - campaign.start_date).days
            duration_score = max(50 - duration_days, 0)  # Penalty for long campaigns
            
            # Campaign type bonus
            type_bonus = {
                'promotional': 10,
                'seasonal': 8,
                'limited_time': 15,
                'general': 5
            }.get(campaign.campaign_type, 0)
            
            total_score = min(view_score + duration_score + type_bonus, 100)
            return round(total_score, 2)
            
        except Exception:
            return 0.0
    
    def _get_peak_viewing_times(self, menu_id: str, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Analyze peak viewing times and patterns"""
        from api.models import MenuViewAnalytics
        
        try:
            views = MenuViewAnalytics.objects.filter(
                menu_id=menu_id,
                timestamp__gte=start_date,
                timestamp__lte=end_date
            )
            
            if not views.exists():
                return {'pattern': 'no_data'}
            
            # Group by hour of day
            hourly_views = {}
            daily_views = {}
            
            for view in views:
                hour = view.timestamp.hour
                day = view.timestamp.strftime('%A')
                
                if hour not in hourly_views:
                    hourly_views[hour] = 0
                hourly_views[hour] += view.view_count
                
                if day not in daily_views:
                    daily_views[day] = 0
                daily_views[day] += view.view_count
            
            # Find peak hours (top 3)
            peak_hours = sorted(hourly_views.items(), key=lambda x: x[1], reverse=True)[:3]
            peak_days = sorted(daily_views.items(), key=lambda x: x[1], reverse=True)[:3]
            
            # Determine pattern
            total_views = sum(hourly_views.values())
            peak_hour_percentage = (peak_hours[0][1] / total_views * 100) if peak_hours else 0
            
            if peak_hour_percentage > 40:
                pattern = 'highly_concentrated'
            elif peak_hour_percentage > 25:
                pattern = 'concentrated'
            else:
                pattern = 'distributed'
            
            return {
                'pattern': pattern,
                'peak_hours': [{'hour': h, 'views': v, 'percentage': round(v/total_views*100, 2)} for h, v in peak_hours],
                'peak_days': [{'day': d, 'views': v, 'percentage': round(v/total_views*100, 2)} for d, v in peak_days],
                'total_views_analyzed': total_views
            }
            
        except Exception as e:
            logger.error(f"Error analyzing peak viewing times: {str(e)}")
            return {'error': str(e)}
    
    def _calculate_popularity_score(self, item_views: Dict, promotional_views: int) -> float:
        """Calculate item popularity score"""
        total_views = item_views['total_views'] or 0
        unique_viewers = item_views['unique_viewers'] or 0
        avg_duration = item_views['avg_view_duration'] or 0
        
        # Weighted score calculation
        view_score = min(total_views / 10, 40)  # Max 40 points
        unique_score = min(unique_viewers * 2, 25)  # Max 25 points
        duration_score = min(avg_duration / 10, 20)  # Max 20 points
        promo_score = min(promotional_views / 5, 15)  # Max 15 points
        
        return round(view_score + unique_score + duration_score + promo_score, 2)
    
    def _generate_recommendations(self, menu_id: str, item_performance: List[Dict], campaign_impact: Dict) -> List[Dict[str, str]]:
        """Generate actionable recommendations based on analytics"""
        recommendations = []
        
        if not item_performance:
            recommendations.append({
                'type': 'data',
                'priority': 'high',
                'message': 'No item performance data available. Ensure analytics tracking is enabled.',
                'action': 'enable_analytics'
            })
            return recommendations
        
        # Low performing items
        low_performers = [item for item in item_performance if item['popularity_score'] < 20]
        if len(low_performers) > 0:
            recommendations.append({
                'type': 'item_optimization',
                'priority': 'medium',
                'message': f'{len(low_performers)} items have low engagement. Consider updating descriptions, images, or pricing.',
                'action': 'optimize_items',
                'affected_items': [item['item_id'] for item in low_performers[:5]]
            })
        
        # High performers to promote
        top_performers = item_performance[:3]
        if top_performers:
            recommendations.append({
                'type': 'promotion',
                'priority': 'low',
                'message': f'Top performing items could benefit from promotional campaigns.',
                'action': 'create_promotions',
                'suggested_items': [item['item_id'] for item in top_performers]
            })
        
        # Campaign effectiveness
        if campaign_impact.get('campaigns_active', 0) > 0:
            avg_effectiveness = campaign_impact.get('avg_campaign_effectiveness', 0)
            if avg_effectiveness < 30:
                recommendations.append({
                    'type': 'campaign_optimization',
                    'priority': 'high',
                    'message': 'Current campaigns have low effectiveness. Review targeting and content.',
                    'action': 'optimize_campaigns'
                })
            elif avg_effectiveness > 70:
                recommendations.append({
                    'type': 'campaign_expansion',
                    'priority': 'low',
                    'message': 'Campaigns are performing well. Consider expanding successful strategies.',
                    'action': 'expand_campaigns'
                })
        else:
            recommendations.append({
                'type': 'campaign_creation',
                'priority': 'medium',
                'message': 'No active promotional campaigns. Consider creating campaigns for top items.',
                'action': 'create_campaigns'
            })
        
        # Price optimization suggestions
        price_sensitive_items = [
            item for item in item_performance 
            if item.get('price_change_impact', {}).get('impact') == 'negative'
        ]
        if price_sensitive_items:
            recommendations.append({
                'type': 'pricing',
                'priority': 'medium',
                'message': f'{len(price_sensitive_items)} items showed negative response to price changes.',
                'action': 'review_pricing',
                'affected_items': [item['item_id'] for item in price_sensitive_items]
            })
        
        return recommendations


class PerformanceMonitor:
    """Monitor system performance and optimize caching"""
    
    def __init__(self):
        self.metrics_cache_timeout = 180  # 3 minutes
    
    def get_system_performance_metrics(self) -> Dict[str, Any]:
        """Get comprehensive system performance metrics"""
        cache_key = "system_performance_metrics"
        cached_result = cache.get(cache_key)
        
        if cached_result:
            return cached_result
        
        try:
            # Database performance
            db_metrics = self._get_database_metrics()
            
            # Cache performance
            cache_metrics = self._get_cache_metrics()
            
            # API performance
            api_metrics = self._get_api_performance_metrics()
            
            # POS sync performance
            pos_sync_metrics = self._get_pos_sync_performance()
            
            result = {
                'timestamp': timezone.now().isoformat(),
                'database': db_metrics,
                'cache': cache_metrics,
                'api': api_metrics,
                'pos_sync': pos_sync_metrics,
                'overall_health': self._calculate_overall_health(db_metrics, cache_metrics, api_metrics)
            }
            
            cache.set(cache_key, result, self.metrics_cache_timeout)
            return result
            
        except Exception as e:
            logger.error(f"Error getting performance metrics: {str(e)}")
            return {'error': str(e)}
    
    def _get_database_metrics(self) -> Dict[str, Any]:
        """Get database performance metrics"""
        from django.db import connection
        from api.models import Menu, MenuItem, Campaign, POSUpdateLog
        
        try:
            # Query performance
            with connection.cursor() as cursor:
                cursor.execute("SELECT COUNT(*) FROM api_menu")
                menu_count = cursor.fetchone()[0]
                
                cursor.execute("SELECT COUNT(*) FROM api_menuitem")
                item_count = cursor.fetchone()[0]
                
                cursor.execute("SELECT COUNT(*) FROM api_campaign")
                campaign_count = cursor.fetchone()[0]
            
            # Recent activity
            recent_pos_logs = POSUpdateLog.objects.filter(
                created_at__gte=timezone.now() - timedelta(hours=1)
            ).count()
            
            return {
                'total_menus': menu_count,
                'total_items': item_count,
                'total_campaigns': campaign_count,
                'recent_pos_activity': recent_pos_logs,
                'status': 'healthy'
            }
            
        except Exception as e:
            logger.error(f"Database metrics error: {str(e)}")
            return {'error': str(e), 'status': 'error'}
    
    def _get_cache_metrics(self) -> Dict[str, Any]:
        """Get cache performance metrics"""
        try:
            # Test cache performance
            test_key = "cache_performance_test"
            test_value = {"timestamp": timezone.now().isoformat()}
            
            # Write test
            start_time = timezone.now()
            cache.set(test_key, test_value, 60)
            write_time = (timezone.now() - start_time).total_seconds() * 1000
            
            # Read test
            start_time = timezone.now()
            cached_value = cache.get(test_key)
            read_time = (timezone.now() - start_time).total_seconds() * 1000
            
            # Clean up
            cache.delete(test_key)
            
            return {
                'write_time_ms': round(write_time, 2),
                'read_time_ms': round(read_time, 2),
                'read_success': cached_value is not None,
                'status': 'healthy' if write_time < 100 and read_time < 50 else 'slow'
            }
            
        except Exception as e:
            logger.error(f"Cache metrics error: {str(e)}")
            return {'error': str(e), 'status': 'error'}
    
    def _get_api_performance_metrics(self) -> Dict[str, Any]:
        """Get API performance metrics"""
        try:
            # This would typically involve API call logging
            # For now, we'll simulate some metrics
            
            # In a real implementation, you'd track:
            # - Average response times
            # - Request rates
            # - Error rates
            # - Endpoint performance
            
            return {
                'avg_response_time_ms': 150,  # Simulated
                'requests_per_minute': 45,   # Simulated
                'error_rate_percent': 2.3,   # Simulated
                'status': 'healthy'
            }
            
        except Exception as e:
            logger.error(f"API metrics error: {str(e)}")
            return {'error': str(e), 'status': 'error'}
    
    def _get_pos_sync_performance(self) -> Dict[str, Any]:
        """Get POS synchronization performance metrics"""
        from api.models import POSUpdateLog
        
        try:
            # Recent sync performance
            one_hour_ago = timezone.now() - timedelta(hours=1)
            recent_syncs = POSUpdateLog.objects.filter(created_at__gte=one_hour_ago)
            
            if not recent_syncs.exists():
                return {
                    'recent_syncs': 0,
                    'status': 'no_activity'
                }
            
            total_syncs = recent_syncs.count()
            successful_syncs = recent_syncs.filter(success=True).count()
            avg_duration = recent_syncs.filter(
                duration_ms__isnull=False
            ).aggregate(avg=Avg('duration_ms'))['avg'] or 0
            
            success_rate = (successful_syncs / total_syncs * 100) if total_syncs > 0 else 0
            
            status = 'healthy' if success_rate >= 95 else 'warning' if success_rate >= 80 else 'unhealthy'
            
            return {
                'recent_syncs': total_syncs,
                'success_rate': round(success_rate, 2),
                'avg_duration_ms': round(avg_duration, 2),
                'status': status
            }
            
        except Exception as e:
            logger.error(f"POS sync metrics error: {str(e)}")
            return {'error': str(e), 'status': 'error'}
    
    def _calculate_overall_health(self, db_metrics: Dict, cache_metrics: Dict, api_metrics: Dict) -> str:
        """Calculate overall system health"""
        statuses = [
            db_metrics.get('status', 'unknown'),
            cache_metrics.get('status', 'unknown'),
            api_metrics.get('status', 'unknown')
        ]
        
        if 'error' in statuses:
            return 'error'
        elif 'unhealthy' in statuses:
            return 'unhealthy'
        elif 'warning' in statuses or 'slow' in statuses:
            return 'warning'
        elif all(s == 'healthy' for s in statuses):
            return 'healthy'
        else:
            return 'unknown'


# Global analytics engine instance
menu_analytics_engine = MenuAnalyticsEngine()
performance_monitor = PerformanceMonitor()