"""
Management command for real-time promotional campaign monitoring.
Monitors active campaigns and updates promotional displays automatically.
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import datetime, timedelta
import time
import logging

from api.models import Campaign, Menu
from api.promotion_engine import PromotionEngine

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Monitor active promotional campaigns and trigger display updates'

    def add_arguments(self, parser):
        parser.add_argument(
            '--interval',
            type=int,
            default=30,
            help='Monitoring interval in seconds (default: 30)'
        )
        parser.add_argument(
            '--menu-id',
            type=int,
            help='Monitor specific menu ID only'
        )
        parser.add_argument(
            '--auto-refresh',
            action='store_true',
            help='Enable automatic display refresh when campaigns change'
        )

    def handle(self, *args, **options):
        interval = options.get('interval', 30)
        menu_id = options.get('menu_id')
        auto_refresh = options.get('auto_refresh', False)

        self.stdout.write(
            self.style.SUCCESS(
                f'🔄 Starting promotional campaign monitor (interval: {interval}s)...'
            )
        )

        last_campaign_check = {}
        
        try:
            while True:
                current_time = timezone.now()
                
                # Get campaigns to monitor
                campaigns_query = Campaign.objects.filter(
                    campaign_type='menu',
                    start_time__lte=current_time,
                    end_time__gte=current_time
                )
                
                if menu_id:
                    campaigns_query = campaigns_query.filter(menu_id=menu_id)

                active_campaigns = campaigns_query.select_related('menu')
                
                if active_campaigns.exists():
                    self.stdout.write(
                        f'📊 Monitoring {active_campaigns.count()} active campaigns at {current_time.strftime("%H:%M:%S")}'
                    )

                for campaign in active_campaigns:
                    menu_id = campaign.menu.id
                    
                    # Check for campaign changes
                    campaign_signature = self._get_campaign_signature(campaign)
                    
                    if menu_id not in last_campaign_check:
                        last_campaign_check[menu_id] = campaign_signature
                        self.stdout.write(
                            f'🎯 Started monitoring: {campaign.name} (Menu: {campaign.menu.name})'
                        )
                    elif last_campaign_check[menu_id] != campaign_signature:
                        self.stdout.write(
                            self.style.SUCCESS(
                                f'🔄 Campaign updated: {campaign.name}'
                            )
                        )
                        last_campaign_check[menu_id] = campaign_signature
                        
                        if auto_refresh:
                            self._trigger_display_refresh(campaign.menu)

                    # Check for campaign expiry
                    if campaign.end_time <= current_time + timedelta(minutes=5):
                        self.stdout.write(
                            self.style.WARNING(
                                f'⏰ Campaign expiring soon: {campaign.name} (ends in {(campaign.end_time - current_time).total_seconds():.0f}s)'
                            )
                        )

                # Check for campaigns that just ended
                ended_campaigns = Campaign.objects.filter(
                    campaign_type='menu',
                    end_time__lt=current_time,
                    end_time__gte=current_time - timedelta(seconds=interval * 2),
                    is_active=True
                )

                for campaign in ended_campaigns:
                    campaign.is_active = False
                    campaign.save()
                    self.stdout.write(
                        self.style.ERROR(
                            f'🏁 Campaign ended: {campaign.name}'
                        )
                    )
                    
                    if auto_refresh:
                        self._trigger_display_refresh(campaign.menu)

                # Check for campaigns that should start
                starting_campaigns = Campaign.objects.filter(
                    campaign_type='menu',
                    start_time__lte=current_time,
                    start_time__gte=current_time - timedelta(seconds=interval * 2),
                    is_active=False
                )

                for campaign in starting_campaigns:
                    if campaign.end_time > current_time:  # Only start if not already expired
                        campaign.is_active = True
                        campaign.save()
                        self.stdout.write(
                            self.style.SUCCESS(
                                f'🚀 Campaign started: {campaign.name}'
                            )
                        )
                        
                        if auto_refresh:
                            self._trigger_display_refresh(campaign.menu)

                # Performance metrics
                if datetime.now().second == 0:  # Every minute
                    self._display_performance_metrics()

                time.sleep(interval)

        except KeyboardInterrupt:
            self.stdout.write(
                self.style.SUCCESS(
                    '\n👋 Campaign monitoring stopped gracefully'
                )
            )

    def _get_campaign_signature(self, campaign):
        """Generate a signature for campaign state detection"""
        metadata = campaign.promotional_metadata or {}
        return f"{campaign.id}:{campaign.name}:{campaign.is_active}:{metadata.get('theme', 'default')}"

    def _trigger_display_refresh(self, menu):
        """Trigger display refresh for menu (placeholder for WebSocket implementation)"""
        self.stdout.write(
            f'📺 Triggering display refresh for menu: {menu.name}'
        )
        # TODO: Implement WebSocket notification to displays
        # For now, this is logged for future WebSocket integration

    def _display_performance_metrics(self):
        """Display current promotional performance metrics"""
        current_time = timezone.now()
        
        # Active campaigns
        active_count = Campaign.objects.filter(
            campaign_type='menu',
            start_time__lte=current_time,
            end_time__gte=current_time,
            is_active=True
        ).count()

        # Campaigns starting in next hour
        upcoming_count = Campaign.objects.filter(
            campaign_type='menu',
            start_time__gt=current_time,
            start_time__lte=current_time + timedelta(hours=1)
        ).count()

        # Recent performance (last 24 hours)
        recent_campaigns = Campaign.objects.filter(
            campaign_type='menu',
            created_at__gte=current_time - timedelta(days=1)
        ).count()

        self.stdout.write(
            f'📈 Metrics: {active_count} active, {upcoming_count} upcoming (1h), {recent_campaigns} created (24h)'
        )