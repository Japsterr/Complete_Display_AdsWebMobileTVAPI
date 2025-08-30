# Analytics Models for Stage 5
from django.db import models
from django.conf import settings
from django.utils import timezone


class MenuViewAnalytics(models.Model):
    """Track menu viewing analytics"""
    menu_id = models.CharField(max_length=255, db_index=True)
    viewer_ip = models.GenericIPAddressField()
    viewer_user_agent = models.TextField(blank=True)
    view_count = models.PositiveIntegerField(default=1)
    session_id = models.CharField(max_length=255, null=True, blank=True)
    
    # Viewing context
    is_promotional = models.BooleanField(default=False)
    campaign_id = models.CharField(max_length=255, null=True, blank=True)
    referrer = models.URLField(null=True, blank=True)
    device_type = models.CharField(max_length=50, null=True, blank=True)  # mobile, desktop, tv
    
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'menu_view_analytics'
        indexes = [
            models.Index(fields=['menu_id', '-timestamp']),
            models.Index(fields=['viewer_ip', '-timestamp']),
            models.Index(fields=['is_promotional', '-timestamp']),
        ]
    
    def __str__(self):
        return f"View: {self.menu_id} at {self.timestamp}"


class MenuItemViewAnalytics(models.Model):
    """Track individual menu item viewing analytics"""
    menu_item = models.ForeignKey('MenuItem', on_delete=models.CASCADE, related_name='view_analytics')
    viewer_ip = models.GenericIPAddressField()
    viewer_user_agent = models.TextField(blank=True)
    
    # View metrics
    view_count = models.PositiveIntegerField(default=1)
    avg_view_duration_seconds = models.FloatField(default=0)
    interaction_count = models.PositiveIntegerField(default=0)  # clicks, taps, etc.
    
    # Context
    is_promotional = models.BooleanField(default=False)
    campaign_id = models.CharField(max_length=255, null=True, blank=True)
    view_position = models.PositiveIntegerField(null=True, blank=True)  # Position in menu
    
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'menu_item_view_analytics'
        indexes = [
            models.Index(fields=['menu_item', '-timestamp']),
            models.Index(fields=['is_promotional', '-timestamp']),
        ]


class CampaignAnalytics(models.Model):
    """Track campaign performance analytics"""
    campaign = models.ForeignKey('Campaign', on_delete=models.CASCADE, related_name='analytics')
    
    # Performance metrics
    total_views = models.PositiveIntegerField(default=0)
    unique_viewers = models.PositiveIntegerField(default=0)
    total_interactions = models.PositiveIntegerField(default=0)
    avg_engagement_duration = models.FloatField(default=0)
    
    # Conversion metrics
    conversion_rate = models.FloatField(default=0)  # Percentage
    click_through_rate = models.FloatField(default=0)  # Percentage
    
    # Time-based metrics
    date = models.DateField(auto_now_add=True)
    hour = models.PositiveSmallIntegerField(default=0)  # 0-23
    
    class Meta:
        db_table = 'campaign_analytics'
        unique_together = ['campaign', 'date', 'hour']
        indexes = [
            models.Index(fields=['campaign', '-date']),
        ]


class SystemPerformanceLog(models.Model):
    """Log system performance metrics"""
    METRIC_TYPES = [
        ('database', 'Database Performance'),
        ('cache', 'Cache Performance'),
        ('api', 'API Performance'),
        ('pos_sync', 'POS Sync Performance'),
        ('overall', 'Overall System Health'),
    ]
    
    metric_type = models.CharField(max_length=20, choices=METRIC_TYPES)
    metric_data = models.JSONField(default=dict)
    
    # Performance indicators
    response_time_ms = models.FloatField(null=True, blank=True)
    success_rate = models.FloatField(null=True, blank=True)
    error_count = models.PositiveIntegerField(default=0)
    
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'system_performance_logs'
        indexes = [
            models.Index(fields=['metric_type', '-timestamp']),
        ]


class UserBehaviorAnalytics(models.Model):
    """Track user behavior patterns"""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)
    session_id = models.CharField(max_length=255)
    
    # User identification
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField()
    
    # Behavior data
    pages_visited = models.JSONField(default=list)
    time_spent_seconds = models.PositiveIntegerField(default=0)
    actions_taken = models.JSONField(default=list)
    
    # Menu interaction
    menus_viewed = models.JSONField(default=list)
    items_viewed = models.JSONField(default=list)
    items_interacted = models.JSONField(default=list)
    
    # Device and context
    device_type = models.CharField(max_length=50)
    screen_resolution = models.CharField(max_length=20, null=True, blank=True)
    referrer = models.URLField(null=True, blank=True)
    
    # Timestamps
    session_start = models.DateTimeField()
    session_end = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'user_behavior_analytics'
        indexes = [
            models.Index(fields=['session_id']),
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['ip_address', '-created_at']),
        ]


class APIUsageAnalytics(models.Model):
    """Track API endpoint usage and performance"""
    endpoint = models.CharField(max_length=255)
    method = models.CharField(max_length=10)  # GET, POST, etc.
    
    # User context
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField(blank=True)
    
    # Performance metrics
    response_time_ms = models.PositiveIntegerField()
    status_code = models.PositiveIntegerField()
    response_size_bytes = models.PositiveIntegerField(default=0)
    
    # Request details
    request_data = models.JSONField(default=dict, null=True, blank=True)
    query_params = models.JSONField(default=dict, null=True, blank=True)
    
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'api_usage_analytics'
        indexes = [
            models.Index(fields=['endpoint', '-timestamp']),
            models.Index(fields=['user', '-timestamp']),
            models.Index(fields=['status_code', '-timestamp']),
        ]


class CachePerformanceLog(models.Model):
    """Track cache performance metrics"""
    cache_key = models.CharField(max_length=255)
    operation = models.CharField(max_length=10)  # GET, SET, DELETE
    
    # Performance metrics
    execution_time_ms = models.FloatField()
    hit = models.BooleanField(default=False)  # For GET operations
    size_bytes = models.PositiveIntegerField(null=True, blank=True)
    
    # Context
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    endpoint = models.CharField(max_length=255, null=True, blank=True)
    
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'cache_performance_logs'
        indexes = [
            models.Index(fields=['operation', '-timestamp']),
            models.Index(fields=['hit', '-timestamp']),
        ]