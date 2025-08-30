"""
Management command for automated promotional campaign generation.
Runs periodically to detect promotions and generate menu campaigns.
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import datetime, timedelta
import logging

from api.models import Menu, Campaign
from api.promotion_engine import PromotionEngine, PromotionCampaignGenerator

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Automatically generate promotional campaigns based on POS data and time-based triggers'

    def add_arguments(self, parser):
        parser.add_argument(
            '--menu-id',
            type=int,
            help='Specific menu ID to process (if not provided, processes all active menus)'
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force generation even if campaigns were recently created'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be generated without creating campaigns'
        )
        parser.add_argument(
            '--template',
            type=str,
            choices=['morning_special', 'lunch_deal', 'happy_hour', 'price_drop', 'combo_special', 'chef_special'],
            help='Only use specific promotional template'
        )

    def handle(self, *args, **options):
        menu_id = options.get('menu_id')
        force = options.get('force', False)
        dry_run = options.get('dry_run', False)
        template_filter = options.get('template')

        self.stdout.write(
            self.style.SUCCESS(
                f'🎯 Starting automated promotional campaign generation...'
            )
        )

        # Get menus to process
        if menu_id:
            try:
                menus = [Menu.objects.get(id=menu_id)]
            except Menu.DoesNotExist:
                self.stdout.write(
                    self.style.ERROR(f'❌ Menu with ID {menu_id} not found')
                )
                return
        else:
            menus = Menu.objects.filter(is_active=True)

        total_generated = 0
        total_promotions = 0

        for menu in menus:
            self.stdout.write(f'\n📋 Processing menu: {menu.name}')
            
            try:
                # Check if we should skip (unless forced)
                if not force and self._should_skip_menu(menu):
                    self.stdout.write(
                        self.style.WARNING(
                            f'⏭️  Skipping {menu.name} - campaigns recently generated'
                        )
                    )
                    continue

                # Initialize promotion engine
                engine = PromotionEngine()
                generator = PromotionCampaignGenerator()

                # Detect promotions
                self.stdout.write('🔍 Detecting promotions...')
                promotions = engine.detect_promotions(menu)
                
                if template_filter:
                    promotions = [p for p in promotions if p.get('template_recommendation') == template_filter]

                total_promotions += len(promotions)
                
                self.stdout.write(
                    f'✅ Found {len(promotions)} promotion opportunities'
                )

                if not promotions:
                    self.stdout.write('📄 No promotions detected for this menu')
                    continue

                # Group promotions by priority and template
                high_priority = [p for p in promotions if p.get('priority') == 'high']
                medium_priority = [p for p in promotions if p.get('priority') == 'medium']
                
                self.stdout.write(f'🔥 High priority: {len(high_priority)}')
                self.stdout.write(f'⚡ Medium priority: {len(medium_priority)}')

                # Generate campaigns for high priority promotions
                for promotion in high_priority[:3]:  # Limit to top 3 high priority
                    campaign_data = self._generate_campaign_data(menu, promotion, 'high')
                    
                    if dry_run:
                        self.stdout.write(
                            f'🧪 DRY RUN - Would create: {campaign_data["name"]}'
                        )
                        self._display_campaign_preview(campaign_data, promotion)
                    else:
                        campaign = self._create_campaign(campaign_data)
                        if campaign:
                            total_generated += 1
                            self.stdout.write(
                                self.style.SUCCESS(
                                    f'✨ Created campaign: {campaign.name}'
                                )
                            )

                # Generate one campaign for medium priority (if no high priority)
                if not high_priority and medium_priority:
                    promotion = medium_priority[0]
                    campaign_data = self._generate_campaign_data(menu, promotion, 'medium')
                    
                    if dry_run:
                        self.stdout.write(
                            f'🧪 DRY RUN - Would create: {campaign_data["name"]}'
                        )
                        self._display_campaign_preview(campaign_data, promotion)
                    else:
                        campaign = self._create_campaign(campaign_data)
                        if campaign:
                            total_generated += 1
                            self.stdout.write(
                                self.style.SUCCESS(
                                    f'✨ Created campaign: {campaign.name}'
                                )
                            )

            except Exception as e:
                logger.error(f'Error processing menu {menu.id}: {e}')
                self.stdout.write(
                    self.style.ERROR(
                        f'❌ Error processing {menu.name}: {e}'
                    )
                )

        # Summary
        self.stdout.write(
            self.style.SUCCESS(
                f'\n🎉 Campaign generation complete!\n'
                f'📊 Promotions detected: {total_promotions}\n'
                f'🚀 Campaigns generated: {total_generated}'
            )
        )

        if dry_run:
            self.stdout.write(
                self.style.WARNING(
                    '🧪 This was a dry run - no campaigns were actually created'
                )
            )

    def _should_skip_menu(self, menu):
        """Check if menu should be skipped based on recent campaign generation"""
        recent_threshold = timezone.now() - timedelta(hours=2)
        recent_campaigns = Campaign.objects.filter(
            menu=menu,
            campaign_type='menu',
            created_at__gte=recent_threshold
        ).count()
        return recent_campaigns >= 3  # Don't generate more than 3 campaigns per 2 hours

    def _generate_campaign_data(self, menu, promotion, priority):
        """Generate campaign data from promotion detection"""
        template = promotion.get('template_recommendation', 'chef_special')
        current_time = datetime.now()
        
        # Template-specific naming and scheduling
        template_config = {
            'morning_special': {
                'name_prefix': 'Morning Special',
                'duration_hours': 5,
                'start_hour': 6
            },
            'lunch_deal': {
                'name_prefix': 'Lunch Deal',
                'duration_hours': 4,
                'start_hour': 11
            },
            'happy_hour': {
                'name_prefix': 'Happy Hour',
                'duration_hours': 3,
                'start_hour': 15
            },
            'price_drop': {
                'name_prefix': 'Flash Sale',
                'duration_hours': 6,
                'start_hour': current_time.hour
            },
            'combo_special': {
                'name_prefix': 'Combo Deal',
                'duration_hours': 8,
                'start_hour': 10
            },
            'chef_special': {
                'name_prefix': 'Chef Special',
                'duration_hours': 12,
                'start_hour': current_time.hour
            }
        }

        config = template_config.get(template, template_config['chef_special'])
        
        # Calculate start and end times
        if priority == 'high':
            start_time = timezone.now()  # Start immediately for high priority
        else:
            # Schedule for next appropriate time slot
            start_time = current_time.replace(
                hour=config['start_hour'], 
                minute=0, 
                second=0, 
                microsecond=0
            )
            if start_time <= current_time:
                start_time += timedelta(days=1)

        end_time = start_time + timedelta(hours=config['duration_hours'])

        return {
            'name': f"{config['name_prefix']} - {menu.name}",
            'description': promotion.get('offer_text', f"Automated {template.replace('_', ' ').title()}"),
            'campaign_type': 'menu',
            'menu': menu,
            'start_time': start_time,
            'end_time': end_time,
            'is_active': priority == 'high',  # Auto-activate high priority
            'promotional_metadata': {
                'template': template,
                'priority': priority,
                'auto_generated': True,
                'generation_time': timezone.now().isoformat(),
                'promotion_data': promotion,
                'layout': 'dual',  # Default layout
                'theme': template.replace('_', '-'),
                'refresh_rate': 10,
                'featured_rotation': 8
            }
        }

    def _create_campaign(self, campaign_data):
        """Create campaign from generated data"""
        try:
            campaign = Campaign.objects.create(**campaign_data)
            return campaign
        except Exception as e:
            logger.error(f'Failed to create campaign: {e}')
            return None

    def _display_campaign_preview(self, campaign_data, promotion):
        """Display preview of what would be created"""
        self.stdout.write(f'   📅 Duration: {campaign_data["start_time"]} - {campaign_data["end_time"]}')
        self.stdout.write(f'   🎯 Priority: {promotion.get("priority", "unknown")}')
        self.stdout.write(f'   🎨 Template: {promotion.get("template_recommendation", "unknown")}')
        self.stdout.write(f'   💡 Offer: {promotion.get("offer_text", "N/A")}')
        if promotion.get('items'):
            items = promotion['items'][:3]  # Show first 3 items
            self.stdout.write(f'   🍽️  Items: {", ".join([item.get("name", "Unknown") for item in items])}')