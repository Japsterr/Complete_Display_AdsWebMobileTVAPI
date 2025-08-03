from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from .managers import CustomUserManager

# --- Core Models ---
class Plan(models.Model):
    plan_id = models.AutoField(primary_key=True)
    plan_name = models.CharField(max_length=50, unique=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=10, default='USD')
    max_screens = models.IntegerField()
    max_storage_gb = models.FloatField()
    has_multi_user = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'Plans'

    def __str__(self):
        return self.plan_name

class User(AbstractBaseUser, PermissionsMixin):
    ACCOUNT_TYPE_CHOICES = [
        ('free', 'Free'),
        ('business', 'Business'),
        ('enterprise', 'Enterprise'),
    ]
    # Use default 'id' field (AutoField primary key) for compatibility with Django and JWT
    email = models.EmailField(unique=True)
    account_type = models.CharField(max_length=20, choices=ACCOUNT_TYPE_CHOICES, default='free')
    plan = models.ForeignKey(Plan, on_delete=models.SET_NULL, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    class Meta:
        db_table = 'Users'

    def __str__(self):
        return self.email

class UserProfile(models.Model):
    profile_id = models.AutoField(primary_key=True)
    user = models.OneToOneField('User', on_delete=models.CASCADE, related_name='profile')
    first_name = models.CharField(max_length=100, blank=True, null=True)
    last_name = models.CharField(max_length=100, blank=True, null=True)
    phone_number = models.CharField(max_length=32, blank=True, null=True)
    address_line1 = models.CharField(max_length=255, blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    state_province = models.CharField(max_length=100, blank=True, null=True)
    postal_code = models.CharField(max_length=20, blank=True, null=True)
    country = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        db_table = 'UserProfiles'

    def __str__(self):
        return f"{self.first_name} {self.last_name}".strip()

class Business(models.Model):
    business_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    owner = models.OneToOneField('User', on_delete=models.CASCADE, related_name='owned_business')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'Businesses'

    def __str__(self):
        return self.name

class BusinessMember(models.Model):
    MEMBER_ROLE_CHOICES = [
        ('owner', 'Owner'),
        ('admin', 'Admin'),
        ('editor', 'Editor'),
        ('viewer', 'Viewer'),
    ]
    member_id = models.AutoField(primary_key=True)
    business = models.ForeignKey(Business, on_delete=models.CASCADE, related_name='members')
    user = models.ForeignKey('User', on_delete=models.CASCADE, related_name='business_memberships')
    member_role = models.CharField(max_length=20, choices=MEMBER_ROLE_CHOICES, default='viewer')
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'BusinessMembers'
        unique_together = ('business', 'user')

    def __str__(self):
        return f"{self.user.email} - {self.member_role} @ {self.business.name}"

# --- Resource Models ---
class Campaign(models.Model):
    campaign_id = models.AutoField(primary_key=True)
    personal_user = models.ForeignKey('User', null=True, blank=True, on_delete=models.CASCADE, related_name='personal_campaigns')
    business = models.ForeignKey('Business', null=True, blank=True, on_delete=models.CASCADE, related_name='business_campaigns')
    created_by = models.ForeignKey('User', on_delete=models.CASCADE, related_name='created_campaigns')
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'Campaigns'
        constraints = [
            models.CheckConstraint(
                check=(
                    (models.Q(personal_user__isnull=False, business__isnull=True)) |
                    (models.Q(personal_user__isnull=True, business__isnull=False))
                ),
                name='campaign_owner_xor'
            )
        ]

    def __str__(self):
        return self.name

class Media(models.Model):
    MEDIA_TYPE_CHOICES = [
        ('image', 'Image'),
        ('video', 'Video'),
    ]
    
    media_id = models.AutoField(primary_key=True)
    personal_user = models.ForeignKey('User', null=True, blank=True, on_delete=models.CASCADE, related_name='personal_media')
    business = models.ForeignKey('Business', null=True, blank=True, on_delete=models.CASCADE, related_name='business_media')
    uploaded_by = models.ForeignKey('User', on_delete=models.CASCADE, related_name='uploaded_media')
    file = models.FileField(upload_to='uploads/')
    name = models.CharField(max_length=255)
    media_type = models.CharField(max_length=10, choices=MEDIA_TYPE_CHOICES, default='image')
    description = models.TextField(blank=True, null=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'Media'
        constraints = [
            models.CheckConstraint(
                check=(
                    (models.Q(personal_user__isnull=False, business__isnull=True)) |
                    (models.Q(personal_user__isnull=True, business__isnull=False))
                ),
                name='media_owner_xor'
            )
        ]

    def __str__(self):
        return self.name

class CampaignMedia(models.Model):
    campaign_media_id = models.AutoField(primary_key=True)
    campaign = models.ForeignKey('Campaign', on_delete=models.CASCADE, related_name='campaign_media')
    media = models.ForeignKey('Media', on_delete=models.CASCADE, related_name='media_campaigns')
    display_duration_seconds = models.PositiveIntegerField(default=10)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        db_table = 'CampaignMedia'
        unique_together = ('campaign', 'media', 'order')

    def __str__(self):
        return f"{self.campaign} - {self.media} (Order: {self.order})"

class Display(models.Model):
    ACTIVATION_STATUS_CHOICES = [
        ('pending', 'Pending Activation'),
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('blocked', 'Blocked'),
    ]
    
    display_id = models.AutoField(primary_key=True)
    personal_user = models.ForeignKey('User', null=True, blank=True, on_delete=models.CASCADE, related_name='personal_displays')
    business = models.ForeignKey('Business', null=True, blank=True, on_delete=models.CASCADE, related_name='business_displays')
    registered_by = models.ForeignKey('User', null=True, blank=True, on_delete=models.CASCADE, related_name='registered_displays')
    default_campaign = models.ForeignKey('Campaign', null=True, blank=True, on_delete=models.SET_NULL, related_name='default_for_displays')
    name = models.CharField(max_length=255)
    location = models.CharField(max_length=255, blank=True, null=True)
    
    # Device activation fields
    device_id = models.CharField(max_length=255, unique=True, null=True, blank=True)  # Unique device identifier
    activation_code = models.CharField(max_length=10, unique=True, null=True, blank=True)  # User-friendly activation code
    activation_status = models.CharField(max_length=20, choices=ACTIVATION_STATUS_CHOICES, default='pending')
    last_seen = models.DateTimeField(null=True, blank=True)  # Last time device connected
    device_info = models.JSONField(default=dict, blank=True)  # Store device details (OS, version, etc.)
    
    registered_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'Displays'
        constraints = [
            models.CheckConstraint(
                check=(
                    # Allow both NULL during pending activation
                    (models.Q(personal_user__isnull=True, business__isnull=True, activation_status='pending')) |
                    # Require one or the other when active
                    (models.Q(personal_user__isnull=False, business__isnull=True)) |
                    (models.Q(personal_user__isnull=True, business__isnull=False))
                ),
                name='display_owner_xor'
            )
        ]

    def __str__(self):
        return self.name

# --- Final Models ---
class Schedule(models.Model):
    schedule_id = models.AutoField(primary_key=True)
    display = models.ForeignKey('Display', on_delete=models.CASCADE, related_name='schedules')
    campaign = models.ForeignKey('Campaign', on_delete=models.CASCADE, related_name='schedules')
    start_datetime = models.DateTimeField()
    end_datetime = models.DateTimeField()
    priority = models.IntegerField(default=0)

    class Meta:
        db_table = 'Schedules'

    def __str__(self):
        return f"{self.display} - {self.campaign} ({self.start_datetime} to {self.end_datetime})"

class Subscription(models.Model):
    subscription_id = models.AutoField(primary_key=True)
    user = models.ForeignKey('User', on_delete=models.CASCADE, related_name='subscriptions')
    plan = models.ForeignKey('Plan', on_delete=models.CASCADE, related_name='subscriptions')
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = 'Subscriptions'

    def __str__(self):
        return f"{self.user.email} - {self.plan.plan_name}"

class Payment(models.Model):
    payment_id = models.AutoField(primary_key=True)
    subscription = models.ForeignKey('Subscription', on_delete=models.CASCADE, related_name='payments')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=10, default='USD')
    payment_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=50)

    class Meta:
        db_table = 'Payments'

    def __str__(self):
        return f"{self.subscription} - {self.amount} {self.currency}"

# --- Stripe Integration Models ---
class StripeCustomer(models.Model):
    """Links our User to Stripe Customer ID"""
    user = models.OneToOneField('User', on_delete=models.CASCADE, related_name='stripe_customer')
    stripe_customer_id = models.CharField(max_length=255, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'StripeCustomers'
    
    def __str__(self):
        return f"{self.user.email} - {self.stripe_customer_id}"

class StripeSubscription(models.Model):
    """Tracks Stripe subscription details"""
    SUBSCRIPTION_STATUS_CHOICES = [
        ('active', 'Active'),
        ('past_due', 'Past Due'),
        ('canceled', 'Canceled'),
        ('unpaid', 'Unpaid'),
        ('trialing', 'Trialing'),
        ('incomplete', 'Incomplete'),
    ]
    
    user = models.ForeignKey('User', on_delete=models.CASCADE, related_name='stripe_subscriptions')
    stripe_subscription_id = models.CharField(max_length=255, unique=True)
    stripe_customer = models.ForeignKey(StripeCustomer, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=SUBSCRIPTION_STATUS_CHOICES)
    current_period_start = models.DateTimeField()
    current_period_end = models.DateTimeField()
    plan_name = models.CharField(max_length=50)  # 'personal' or 'business'
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'StripeSubscriptions'
    
    def __str__(self):
        return f"{self.user.email} - {self.plan_name} ({self.status})"

class StripePayment(models.Model):
    """Tracks individual Stripe payments"""
    PAYMENT_STATUS_CHOICES = [
        ('succeeded', 'Succeeded'),
        ('pending', 'Pending'),
        ('failed', 'Failed'),
        ('canceled', 'Canceled'),
        ('requires_action', 'Requires Action'),
    ]
    
    stripe_payment_intent_id = models.CharField(max_length=255, unique=True)
    stripe_subscription = models.ForeignKey(StripeSubscription, on_delete=models.CASCADE, related_name='payments', null=True, blank=True)
    user = models.ForeignKey('User', on_delete=models.CASCADE, related_name='stripe_payments')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=10, default='ZAR')  # South African Rand
    status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES)
    payment_type = models.CharField(max_length=50, default='subscription')  # 'subscription', 'upgrade', 'one-time'
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'StripePayments'
    
    def __str__(self):
        return f"{self.user.email} - R{self.amount} ({self.status})"

class RefreshToken(models.Model):
    token_id = models.AutoField(primary_key=True)
    user = models.ForeignKey('User', on_delete=models.CASCADE, related_name='refresh_tokens')
    token = models.CharField(max_length=255, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()

    class Meta:
        db_table = 'RefreshTokens'

    def __str__(self):
        return f"{self.user.email} - {self.token[:10]}..."

# Analytics and Tracking Models
class DeviceHeartbeat(models.Model):
    """Track device online status and health"""
    display = models.ForeignKey(Display, on_delete=models.CASCADE, related_name='heartbeats')
    timestamp = models.DateTimeField(auto_now_add=True)
    device_status = models.CharField(max_length=20, default='online')
    current_campaign = models.ForeignKey(Campaign, null=True, blank=True, on_delete=models.SET_NULL)
    device_info = models.JSONField(default=dict, blank=True)  # Battery, storage, etc.
    
    class Meta:
        db_table = 'DeviceHeartbeats'
        indexes = [
            models.Index(fields=['display', '-timestamp']),
        ]

class MediaImpression(models.Model):
    """Track when and how long each media item is displayed"""
    display = models.ForeignKey(Display, on_delete=models.CASCADE, related_name='impressions')
    campaign = models.ForeignKey(Campaign, on_delete=models.CASCADE, related_name='impressions')
    media = models.ForeignKey(Media, on_delete=models.CASCADE, related_name='impressions')
    
    # Timing information
    started_at = models.DateTimeField(auto_now_add=True)
    duration_shown = models.IntegerField(help_text="Actual seconds displayed")
    scheduled_duration = models.IntegerField(help_text="Intended seconds from campaign")
    completed = models.BooleanField(default=False)
    
    # Context information
    sequence_number = models.IntegerField(help_text="Order in campaign rotation")
    total_media_in_campaign = models.IntegerField()
    
    class Meta:
        db_table = 'MediaImpressions'
        indexes = [
            models.Index(fields=['display', '-started_at']),
            models.Index(fields=['campaign', '-started_at']),
            models.Index(fields=['media', '-started_at']),
        ]

class CampaignSession(models.Model):
    """Track campaign viewing sessions on devices"""
    display = models.ForeignKey(Display, on_delete=models.CASCADE, related_name='campaign_sessions')
    campaign = models.ForeignKey(Campaign, on_delete=models.CASCADE, related_name='sessions')
    
    started_at = models.DateTimeField(auto_now_add=True)
    ended_at = models.DateTimeField(null=True, blank=True)
    total_impressions = models.IntegerField(default=0)
    total_duration = models.IntegerField(default=0, help_text="Total seconds displayed")
    
    # Session metadata
    is_active = models.BooleanField(default=True)
    ended_reason = models.CharField(max_length=50, blank=True)  # 'campaign_changed', 'device_offline', etc.
    
    class Meta:
        db_table = 'CampaignSessions'
        indexes = [
            models.Index(fields=['display', '-started_at']),
            models.Index(fields=['campaign', '-started_at']),
        ]
