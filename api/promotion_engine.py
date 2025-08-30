# Dynamic Promotion Engine - Stage 3: Dynamic Content Management
from django.db import models
from django.utils import timezone
from django.db.models import Q, Count, Avg
from datetime import timedelta
from typing import List, Dict, Optional
import logging
import json

logger = logging.getLogger(__name__)

class PromotionEngine:
    """Intelligent promotion detection and campaign generation engine"""
    
    def __init__(self, business=None):
        self.business = business
        
    def detect_promotions(self, menu_id: int) -> List[Dict]:
        """Detect promotional opportunities from menu and POS data"""
        from .models import Menu, MenuItem, MenuItemPOSSync
        
        try:
            menu = Menu.objects.get(menu_id=menu_id)
            promotions = []
            
            # 1. Direct POS Promotions - Items marked as promotion in POS
            pos_promotions = menu.items.filter(
                promotion_flag=True,
                available=True
            )
            
            for item in pos_promotions:
                promotions.append({
                    'type': 'pos_promotion',
                    'item': item,
                    'priority': 'high',
                    'source': 'POS System',
                    'offer_text': item.special_offer or f"Special Offer: {item.name}",
                    'auto_generated': False
                })
            
            # 2. Price Drop Detection - Items with significant price decreases
            recent_price_changes = self._detect_price_drops(menu)
            for change in recent_price_changes:
                promotions.append({
                    'type': 'price_drop',
                    'item': change['item'],
                    'priority': 'medium',
                    'source': 'Price Analysis',
                    'offer_text': f"Price Drop: {change['item'].name} - Save {change['savings']}!",
                    'auto_generated': True,
                    'savings_amount': change['savings']
                })
            
            # 3. Seasonal/Time-based Promotions
            time_promotions = self._generate_time_based_promotions(menu)
            promotions.extend(time_promotions)
            
            # 4. Cross-sell Opportunities - Popular item combinations
            cross_sell = self._detect_cross_sell_opportunities(menu)
            promotions.extend(cross_sell)
            
            # 5. Inventory Management - Promote items that need to move
            inventory_promotions = self._generate_inventory_promotions(menu)
            promotions.extend(inventory_promotions)
            
            return sorted(promotions, key=lambda x: self._get_priority_score(x['priority']), reverse=True)
            
        except Exception as e:
            logger.error(f"Error detecting promotions for menu {menu_id}: {str(e)}")
            return []
    
    def _detect_price_drops(self, menu) -> List[Dict]:
        """Detect items with recent price decreases"""
        from .models import MenuItemPOSSync
        
        price_drops = []
        recent_syncs = MenuItemPOSSync.objects.filter(
            menu_item__menu=menu,
            last_pos_update__gte=timezone.now() - timedelta(days=7)
        )
        
        for sync in recent_syncs:
            item = sync.menu_item
            if sync.pos_price and item.price:
                current_price = float(item.price)
                pos_price = float(sync.pos_price)
                
                if pos_price < current_price:
                    savings = current_price - pos_price
                    if savings >= 5.00:  # Minimum R5 savings to trigger promotion
                        price_drops.append({
                            'item': item,
                            'savings': f"R{savings:.2f}",
                            'percentage': ((savings / current_price) * 100)
                        })
        
        return price_drops
    
    def _generate_time_based_promotions(self, menu) -> List[Dict]:
        """Generate time-based promotional opportunities"""
        now = timezone.now()
        promotions = []
        
        # Morning promotions (6-11 AM)
        if 6 <= now.hour <= 11:
            coffee_items = menu.items.filter(
                Q(name__icontains='coffee') | Q(name__icontains='espresso') | 
                Q(name__icontains='cappuccino') | Q(name__icontains='latte'),
                available=True
            )
            
            for item in coffee_items[:2]:  # Limit to 2 items
                promotions.append({
                    'type': 'time_based',
                    'item': item,
                    'priority': 'medium',
                    'source': 'Time-based Engine',
                    'offer_text': f"Morning Special: {item.name} - Perfect start to your day!",
                    'auto_generated': True,
                    'time_window': 'Morning (6-11 AM)'
                })
        
        # Lunch promotions (11 AM - 3 PM)
        elif 11 <= now.hour <= 15:
            lunch_items = menu.items.filter(
                Q(name__icontains='burger') | Q(name__icontains='sandwich') | 
                Q(name__icontains='salad') | Q(name__icontains='wrap'),
                available=True
            )
            
            for item in lunch_items[:2]:
                promotions.append({
                    'type': 'time_based',
                    'item': item,
                    'priority': 'high',
                    'source': 'Time-based Engine',
                    'offer_text': f"Lunch Special: {item.name} - Quick & Delicious!",
                    'auto_generated': True,
                    'time_window': 'Lunch (11 AM - 3 PM)'
                })
        
        # Happy Hour (3-6 PM)
        elif 15 <= now.hour <= 18:
            beverage_items = menu.items.filter(
                Q(name__icontains='drink') | Q(name__icontains='juice') | 
                Q(name__icontains='smoothie') | Q(name__icontains='tea'),
                available=True
            )
            
            for item in beverage_items[:2]:
                promotions.append({
                    'type': 'time_based',
                    'item': item,
                    'priority': 'medium',
                    'source': 'Time-based Engine',
                    'offer_text': f"Happy Hour: {item.name} - Refresh your afternoon!",
                    'auto_generated': True,
                    'time_window': 'Happy Hour (3-6 PM)'
                })
        
        return promotions
    
    def _detect_cross_sell_opportunities(self, menu) -> List[Dict]:
        """Detect items that work well together for combo promotions"""
        promotions = []
        
        # Popular combinations
        combos = [
            {
                'items': ['burger', 'fries'],
                'offer': 'Perfect Combo: {item1} + Fries',
                'type': 'combo'
            },
            {
                'items': ['coffee', 'muffin'],
                'offer': 'Morning Combo: {item1} + Muffin',
                'type': 'combo'
            },
            {
                'items': ['pizza', 'drink'],
                'offer': 'Meal Deal: {item1} + Drink',
                'type': 'combo'
            }
        ]
        
        for combo in combos:
            main_items = menu.items.filter(
                name__icontains=combo['items'][0],
                available=True
            )
            
            for main_item in main_items[:1]:  # One combo per type
                promotions.append({
                    'type': 'cross_sell',
                    'item': main_item,
                    'priority': 'medium',
                    'source': 'Cross-sell Engine',
                    'offer_text': combo['offer'].format(item1=main_item.name),
                    'auto_generated': True,
                    'combo_type': combo['type']
                })
        
        return promotions
    
    def _generate_inventory_promotions(self, menu) -> List[Dict]:
        """Generate promotions for items that might need inventory movement"""
        # This would integrate with actual inventory data in a real system
        # For now, we'll simulate based on item characteristics
        
        promotions = []
        
        # Promote items that haven't been promoted recently
        non_promoted_items = menu.items.filter(
            promotion_flag=False,
            available=True,
            last_pos_sync__isnull=False  # Only items that sync with POS
        ).order_by('?')[:2]  # Random selection
        
        for item in non_promoted_items:
            promotions.append({
                'type': 'inventory_push',
                'item': item,
                'priority': 'low',
                'source': 'Inventory Engine',
                'offer_text': f"Try Our {item.name} - Fresh & Delicious!",
                'auto_generated': True,
                'reason': 'Inventory rotation'
            })
        
        return promotions
    
    def _get_priority_score(self, priority: str) -> int:
        """Convert priority to numeric score for sorting"""
        return {'high': 3, 'medium': 2, 'low': 1}.get(priority, 0)
    
    def generate_promotional_campaigns(self, promotions: List[Dict]) -> List[Dict]:
        """Generate campaign data from detected promotions"""
        campaigns = []
        
        for promo in promotions:
            if promo['priority'] in ['high', 'medium']:  # Only create campaigns for significant promotions
                campaign_data = {
                    'name': f"Auto-Generated: {promo['offer_text'][:50]}",
                    'description': self._generate_campaign_description(promo),
                    'campaign_type': 'menu',
                    'promotional_content': {
                        'type': promo['type'],
                        'offer_text': promo['offer_text'],
                        'source': promo['source'],
                        'auto_generated': promo['auto_generated'],
                        'item_id': promo['item'].id,
                        'item_name': promo['item'].name,
                        'priority': promo['priority']
                    },
                    'suggested_duration': self._get_suggested_duration(promo),
                    'target_audience': self._get_target_audience(promo),
                    'success_metrics': self._get_success_metrics(promo)
                }
                campaigns.append(campaign_data)
        
        return campaigns
    
    def _generate_campaign_description(self, promo: Dict) -> str:
        """Generate detailed campaign description"""
        base_desc = f"Automatically generated promotional campaign for {promo['item'].name}. "
        
        if promo['type'] == 'pos_promotion':
            return base_desc + f"Based on POS promotion data: {promo['offer_text']}"
        elif promo['type'] == 'price_drop':
            return base_desc + f"Highlights price reduction and savings opportunity."
        elif promo['type'] == 'time_based':
            return base_desc + f"Time-sensitive promotion for {promo.get('time_window', 'current time period')}."
        elif promo['type'] == 'cross_sell':
            return base_desc + f"Combo promotion to increase average order value."
        else:
            return base_desc + "General promotional campaign to boost item visibility."
    
    def _get_suggested_duration(self, promo: Dict) -> str:
        """Suggest campaign duration based on promotion type"""
        duration_map = {
            'pos_promotion': '7 days',  # Follow POS promotion period
            'price_drop': '3 days',     # Quick action on price changes
            'time_based': '1 day',      # Daily time-based promotions
            'cross_sell': '5 days',     # Medium-term combo promotions
            'inventory_push': '2 days'  # Short-term inventory movement
        }
        return duration_map.get(promo['type'], '3 days')
    
    def _get_target_audience(self, promo: Dict) -> str:
        """Determine target audience for promotion"""
        if promo['type'] == 'time_based':
            if 'Morning' in promo.get('time_window', ''):
                return 'Early commuters, coffee lovers'
            elif 'Lunch' in promo.get('time_window', ''):
                return 'Office workers, lunch crowd'
            else:
                return 'Afternoon visitors, casual diners'
        elif promo['type'] == 'cross_sell':
            return 'Customers looking for complete meals'
        else:
            return 'General customers, deal seekers'
    
    def _get_success_metrics(self, promo: Dict) -> Dict:
        """Define success metrics for the promotion"""
        base_metrics = {
            'target_impressions': 1000,
            'target_engagement_rate': '15%',
            'success_indicator': 'Increased item visibility and orders'
        }
        
        if promo['type'] == 'price_drop':
            base_metrics['target_conversion_rate'] = '25%'
            base_metrics['success_indicator'] = 'Capitalize on price advantage'
        elif promo['type'] == 'cross_sell':
            base_metrics['target_upsell_rate'] = '20%'
            base_metrics['success_indicator'] = 'Increase average order value'
        
        return base_metrics
    
    def _is_morning_time(self, current_time):
        """Check if current time is morning (6 AM - 11 AM)"""
        return 6 <= current_time.hour < 11
    
    def _is_lunch_time(self, current_time):
        """Check if current time is lunch (11 AM - 3 PM)"""
        return 11 <= current_time.hour < 15
    
    def _is_happy_hour_time(self, current_time):
        """Check if current time is happy hour (3 PM - 6 PM)"""
        return 15 <= current_time.hour < 18


class PromotionCampaignGenerator:
    """Generates actual campaigns from promotion data"""
    
    def __init__(self, business=None, user=None):
        self.business = business
        self.user = user
    
    def create_automated_campaigns(self, menu_id: int, max_campaigns: int = 3) -> List:
        """Create automated promotional campaigns for a menu"""
        from .models import Campaign, Menu
        
        try:
            menu = Menu.objects.get(menu_id=menu_id)
            engine = PromotionEngine(self.business)
            
            # Detect promotions
            promotions = engine.detect_promotions(menu_id)
            
            # Generate campaign data
            campaign_data_list = engine.generate_promotional_campaigns(promotions)
            
            # Create actual campaigns (limit to max_campaigns)
            created_campaigns = []
            for campaign_data in campaign_data_list[:max_campaigns]:
                try:
                    campaign = Campaign.objects.create(
                        name=campaign_data['name'],
                        description=campaign_data['description'],
                        campaign_type='menu',
                        menu=menu,
                        menu_layout='dual',  # Default layout
                        auto_refresh_seconds=10,
                        featured_rotation_seconds=8,
                        status='ready',
                        start_date=timezone.now(),
                        end_date=timezone.now() + timedelta(days=int(campaign_data['suggested_duration'].split()[0])),
                        business=self.business if self.business else None,
                        personal_user=self.user if not self.business else None,
                        created_by=self.user
                    )
                    
                    # Store promotional metadata
                    campaign.promotional_metadata = campaign_data['promotional_content']
                    campaign.save()
                    
                    created_campaigns.append(campaign)
                    
                    logger.info(f"Created automated campaign: {campaign.name}")
                    
                except Exception as e:
                    logger.error(f"Error creating campaign: {str(e)}")
                    continue
            
            return created_campaigns
            
        except Exception as e:
            logger.error(f"Error creating automated campaigns for menu {menu_id}: {str(e)}")
            return []
    
    def update_existing_campaigns(self, menu_id: int):
        """Update existing campaigns with new promotional data"""
        from .models import Campaign
        
        try:
            # Find active auto-generated campaigns for this menu
            campaigns = Campaign.objects.filter(
                menu__menu_id=menu_id,
                status__in=['ready', 'active'],
                name__startswith='Auto-Generated:'
            )
            
            engine = PromotionEngine(self.business)
            current_promotions = engine.detect_promotions(menu_id)
            
            # Update campaigns with current promotional data
            for campaign in campaigns:
                if hasattr(campaign, 'promotional_metadata'):
                    # Check if the promotion is still valid
                    item_id = campaign.promotional_metadata.get('item_id')
                    if item_id:
                        current_item_promos = [p for p in current_promotions if p['item'].id == item_id]
                        if current_item_promos:
                            # Update with current data
                            current_promo = current_item_promos[0]
                            campaign.description = engine._generate_campaign_description(current_promo)
                            campaign.save()
                        else:
                            # Promotion no longer valid, pause campaign
                            campaign.status = 'paused'
                            campaign.save()
                            logger.info(f"Paused outdated campaign: {campaign.name}")
            
        except Exception as e:
            logger.error(f"Error updating campaigns for menu {menu_id}: {str(e)}")