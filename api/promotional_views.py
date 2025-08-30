# Promotional Template System - Stage 3: Dynamic Content Management
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.utils import timezone
from datetime import timedelta
import logging

from .models import Menu, Campaign
from .promotion_engine import PromotionEngine, PromotionCampaignGenerator
from .serializers import CampaignSerializer

logger = logging.getLogger(__name__)

class PromotionalTemplateViewSet(viewsets.ViewSet):
    """ViewSet for managing promotional templates and auto-generation"""
    permission_classes = [permissions.IsAuthenticated]
    
    @action(detail=False, methods=['get'])
    def templates(self, request):
        """Get available promotional templates"""
        templates = [
            {
                'id': 'morning_special',
                'name': 'Morning Special',
                'description': 'Perfect for coffee and breakfast items during morning hours',
                'time_window': '6:00 AM - 11:00 AM',
                'template': {
                    'background': 'linear-gradient(135deg, #ff9a56, #ffd23f)',
                    'text_color': '#ffffff',
                    'accent_color': '#ff6b35',
                    'banner_text': '☀️ Good Morning! Start your day right with {item_name}',
                    'promotion_badge': 'MORNING SPECIAL'
                }
            },
            {
                'id': 'lunch_deal',
                'name': 'Lunch Deal',
                'description': 'Ideal for lunch items and combo meals',
                'time_window': '11:00 AM - 3:00 PM',
                'template': {
                    'background': 'linear-gradient(135deg, #667eea, #764ba2)',
                    'text_color': '#ffffff',
                    'accent_color': '#4CAF50',
                    'banner_text': '🍽️ Lunch Time! Enjoy {item_name} - Quick & Delicious',
                    'promotion_badge': 'LUNCH SPECIAL'
                }
            },
            {
                'id': 'happy_hour',
                'name': 'Happy Hour',
                'description': 'Great for beverages and afternoon treats',
                'time_window': '3:00 PM - 6:00 PM',
                'template': {
                    'background': 'linear-gradient(135deg, #f093fb, #f5576c)',
                    'text_color': '#ffffff',
                    'accent_color': '#FFC107',
                    'banner_text': '🎉 Happy Hour! Refresh with {item_name}',
                    'promotion_badge': 'HAPPY HOUR'
                }
            },
            {
                'id': 'price_drop',
                'name': 'Price Drop Alert',
                'description': 'Highlights items with reduced prices',
                'time_window': 'Anytime',
                'template': {
                    'background': 'linear-gradient(135deg, #ff6b6b, #ee5a24)',
                    'text_color': '#ffffff',
                    'accent_color': '#00d2d3',
                    'banner_text': '💸 Price Drop Alert! Save big on {item_name}',
                    'promotion_badge': 'SALE'
                }
            },
            {
                'id': 'combo_special',
                'name': 'Combo Special',
                'description': 'Perfect for meal combinations and cross-selling',
                'time_window': 'Anytime',
                'template': {
                    'background': 'linear-gradient(135deg, #4ecdc4, #44a08d)',
                    'text_color': '#ffffff',
                    'accent_color': '#FFD700',
                    'banner_text': '🍴 Perfect Combo! Try {item_name} with sides',
                    'promotion_badge': 'COMBO DEAL'
                }
            },
            {
                'id': 'chef_special',
                'name': 'Chef Special',
                'description': 'Showcase premium or signature items',
                'time_window': 'Anytime',
                'template': {
                    'background': 'linear-gradient(135deg, #2c3e50, #3498db)',
                    'text_color': '#ffffff',
                    'accent_color': '#e74c3c',
                    'banner_text': '👨‍🍳 Chef Special! Expertly crafted {item_name}',
                    'promotion_badge': 'CHEF SPECIAL'
                }
            }
        ]
        
        return Response({'templates': templates})
    
    @action(detail=False, methods=['post'])
    def detect_promotions(self, request):
        """Detect promotional opportunities for a specific menu"""
        menu_id = request.data.get('menu_id')
        
        if not menu_id:
            return Response({'error': 'menu_id is required'}, status=400)
        
        try:
            # Get user's business context
            user = request.user
            business = None
            if user.account_type == 'business' and hasattr(user, 'owned_business'):
                business = user.owned_business
            
            # Initialize promotion engine
            engine = PromotionEngine(business)
            
            # Detect promotions
            promotions = engine.detect_promotions(menu_id)
            
            # Format response
            formatted_promotions = []
            for promo in promotions:
                formatted_promotions.append({
                    'type': promo['type'],
                    'item_id': promo['item'].id,
                    'item_name': promo['item'].name,
                    'item_price': str(promo['item'].price),
                    'priority': promo['priority'],
                    'source': promo['source'],
                    'offer_text': promo['offer_text'],
                    'auto_generated': promo['auto_generated'],
                    'template_recommendation': self._get_template_recommendation(promo),
                    'estimated_impact': self._estimate_promotion_impact(promo)
                })
            
            return Response({
                'menu_id': menu_id,
                'promotions_detected': len(promotions),
                'promotions': formatted_promotions,
                'detection_timestamp': timezone.now(),
                'recommendations': self._get_promotion_recommendations(promotions)
            })
            
        except Exception as e:
            logger.error(f"Error detecting promotions: {str(e)}")
            return Response({'error': str(e)}, status=500)
    
    @action(detail=False, methods=['post'])
    def generate_campaigns(self, request):
        """Generate automated promotional campaigns"""
        menu_id = request.data.get('menu_id')
        max_campaigns = request.data.get('max_campaigns', 3)
        auto_activate = request.data.get('auto_activate', False)
        
        if not menu_id:
            return Response({'error': 'menu_id is required'}, status=400)
        
        try:
            # Get user context
            user = request.user
            business = None
            if user.account_type == 'business' and hasattr(user, 'owned_business'):
                business = user.owned_business
            
            # Initialize campaign generator
            generator = PromotionCampaignGenerator(business, user)
            
            # Create automated campaigns
            campaigns = generator.create_automated_campaigns(menu_id, max_campaigns)
            
            # Auto-activate if requested
            if auto_activate:
                for campaign in campaigns:
                    campaign.status = 'active'
                    campaign.save()
            
            # Serialize campaigns for response
            campaign_data = []
            for campaign in campaigns:
                serializer = CampaignSerializer(campaign)
                campaign_data.append(serializer.data)
            
            return Response({
                'menu_id': menu_id,
                'campaigns_created': len(campaigns),
                'campaigns': campaign_data,
                'auto_activated': auto_activate,
                'generation_timestamp': timezone.now()
            })
            
        except Exception as e:
            logger.error(f"Error generating campaigns: {str(e)}")
            return Response({'error': str(e)}, status=500)
    
    @action(detail=False, methods=['post'])
    def update_campaigns(self, request):
        """Update existing campaigns with current promotional data"""
        menu_id = request.data.get('menu_id')
        
        if not menu_id:
            return Response({'error': 'menu_id is required'}, status=400)
        
        try:
            # Get user context
            user = request.user
            business = None
            if user.account_type == 'business' and hasattr(user, 'owned_business'):
                business = user.owned_business
            
            # Initialize campaign generator
            generator = PromotionCampaignGenerator(business, user)
            
            # Update existing campaigns
            generator.update_existing_campaigns(menu_id)
            
            # Get updated campaigns
            updated_campaigns = Campaign.objects.filter(
                menu__menu_id=menu_id,
                name__startswith='Auto-Generated:'
            )
            
            campaign_data = []
            for campaign in updated_campaigns:
                serializer = CampaignSerializer(campaign)
                campaign_data.append(serializer.data)
            
            return Response({
                'menu_id': menu_id,
                'campaigns_updated': len(updated_campaigns),
                'campaigns': campaign_data,
                'update_timestamp': timezone.now()
            })
            
        except Exception as e:
            logger.error(f"Error updating campaigns: {str(e)}")
            return Response({'error': str(e)}, status=500)
    
    @action(detail=False, methods=['get'])
    def analytics(self, request):
        """Get promotional campaign analytics"""
        menu_id = request.GET.get('menu_id')
        
        if not menu_id:
            return Response({'error': 'menu_id parameter is required'}, status=400)
        
        try:
            # Get promotional campaigns for the menu
            campaigns = Campaign.objects.filter(
                menu__menu_id=menu_id,
                campaign_type='menu'
            )
            
            analytics_data = {
                'total_campaigns': campaigns.count(),
                'active_campaigns': campaigns.filter(status='active').count(),
                'auto_generated_campaigns': campaigns.filter(name__startswith='Auto-Generated:').count(),
                'campaign_performance': [],
                'promotion_types': {},
                'success_metrics': {
                    'total_impressions': 0,
                    'average_duration': 0,
                    'conversion_rate': 0
                }
            }
            
            # Analyze campaign performance
            for campaign in campaigns:
                if hasattr(campaign, 'promotional_metadata') and campaign.promotional_metadata:
                    promo_type = campaign.promotional_metadata.get('type', 'unknown')
                    analytics_data['promotion_types'][promo_type] = analytics_data['promotion_types'].get(promo_type, 0) + 1
                    
                    campaign_performance = {
                        'campaign_id': campaign.campaign_id,
                        'name': campaign.name,
                        'type': promo_type,
                        'status': campaign.status,
                        'duration_days': (timezone.now() - campaign.created_at).days,
                        'auto_generated': campaign.promotional_metadata.get('auto_generated', False)
                    }
                    analytics_data['campaign_performance'].append(campaign_performance)
            
            return Response(analytics_data)
            
        except Exception as e:
            logger.error(f"Error getting analytics: {str(e)}")
            return Response({'error': str(e)}, status=500)
    
    def _get_template_recommendation(self, promo):
        """Recommend template based on promotion type"""
        template_map = {
            'pos_promotion': 'chef_special',
            'price_drop': 'price_drop',
            'time_based': self._get_time_based_template(),
            'cross_sell': 'combo_special',
            'inventory_push': 'chef_special'
        }
        return template_map.get(promo['type'], 'chef_special')
    
    def _get_time_based_template(self):
        """Get time-appropriate template"""
        now = timezone.now()
        if 6 <= now.hour <= 11:
            return 'morning_special'
        elif 11 <= now.hour <= 15:
            return 'lunch_deal'
        elif 15 <= now.hour <= 18:
            return 'happy_hour'
        else:
            return 'chef_special'
    
    def _estimate_promotion_impact(self, promo):
        """Estimate potential impact of promotion"""
        impact_scores = {
            'pos_promotion': {'visibility': 'high', 'conversion': 'high', 'reach': 'medium'},
            'price_drop': {'visibility': 'high', 'conversion': 'very_high', 'reach': 'high'},
            'time_based': {'visibility': 'medium', 'conversion': 'medium', 'reach': 'high'},
            'cross_sell': {'visibility': 'medium', 'conversion': 'medium', 'reach': 'medium'},
            'inventory_push': {'visibility': 'low', 'conversion': 'low', 'reach': 'low'}
        }
        return impact_scores.get(promo['type'], {'visibility': 'medium', 'conversion': 'medium', 'reach': 'medium'})
    
    def _get_promotion_recommendations(self, promotions):
        """Generate recommendations based on detected promotions"""
        recommendations = []
        
        high_priority_count = sum(1 for p in promotions if p['priority'] == 'high')
        
        if high_priority_count > 0:
            recommendations.append({
                'type': 'immediate_action',
                'message': f"You have {high_priority_count} high-priority promotional opportunities. Consider creating campaigns immediately.",
                'action': 'create_campaigns'
            })
        
        pos_promotions = [p for p in promotions if p['type'] == 'pos_promotion']
        if pos_promotions:
            recommendations.append({
                'type': 'pos_integration',
                'message': f"Your POS system has {len(pos_promotions)} active promotions. These should be prioritized.",
                'action': 'prioritize_pos_promotions'
            })
        
        time_based_promotions = [p for p in promotions if p['type'] == 'time_based']
        if time_based_promotions:
            recommendations.append({
                'type': 'schedule_optimization',
                'message': f"Schedule time-based promotions for optimal customer engagement during peak hours.",
                'action': 'optimize_scheduling'
            })
        
        return recommendations