
from rest_framework import serializers
from .models import DisplayGroup, Tag, MediaApproval

class DisplayGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = DisplayGroup
        fields = ['id', 'name', 'owner', 'displays', 'created_at', 'updated_at']

class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['id', 'name', 'created_at']

class MediaApprovalSerializer(serializers.ModelSerializer):
    class Meta:
        model = MediaApproval
        fields = ['id', 'media', 'reviewed_by', 'status', 'comments', 'reviewed_at', 'created_at']
# Organization & User Management Serializers
from rest_framework import serializers
from .models import Organization, Membership, Invitation, AuditLog

class OrganizationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organization
        fields = ['id', 'name', 'created_at', 'owner']

class MembershipSerializer(serializers.ModelSerializer):
    class Meta:
        model = Membership
        fields = ['id', 'user', 'organization', 'role', 'joined_at']

class InvitationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Invitation
        fields = ['id', 'email', 'organization', 'invited_by', 'accepted', 'created_at']

class AuditLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = AuditLog
        fields = ['id', 'user', 'action', 'timestamp', 'details']
from rest_framework import serializers
from .models import (
    User, Plan, UserProfile, Business, BusinessMember, Campaign, Media, CampaignMedia,
    Display, Schedule, Subscription, Payment, StripeCustomer, StripeSubscription, StripePayment
)
from django.db import transaction

class UserSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(source='profile.first_name', allow_blank=True, required=False)
    last_name = serializers.CharField(source='profile.last_name', allow_blank=True, required=False)
    
    class Meta:
        model = User
        fields = ['id', 'email', 'account_type', 'date_joined', 'first_name', 'last_name']
        read_only_fields = ['id', 'email', 'date_joined']
    
    def update(self, instance, validated_data):
        # Handle profile fields separately
        profile_data = {}
        if 'profile' in validated_data:
            profile_data = validated_data.pop('profile')
        
        # Update User instance
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        # Update or create profile
        if profile_data:
            profile, created = UserProfile.objects.get_or_create(user=instance)
            for attr, value in profile_data.items():
                setattr(profile, attr, value)
            profile.save()
        
        return instance

class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=6)
    first_name = serializers.CharField(max_length=30, required=True)
    last_name = serializers.CharField(max_length=30, required=True)
    business_name = serializers.CharField(max_length=100, required=False)
    
    class Meta:
        model = User
        fields = ['email', 'password', 'first_name', 'last_name', 'account_type', 'business_name']

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value

    def validate_password(self, value):
        if len(value) < 6:
            raise serializers.ValidationError("Password must be at least 6 characters long.")
        return value

    def validate(self, data):
        if data.get('account_type') == 'business' and not data.get('business_name'):
            raise serializers.ValidationError({
                'business_name': 'Business name is required for business accounts.'
            })
        return data

    def create(self, validated_data):
        try:
            with transaction.atomic():
                # Extract fields that aren't direct User model fields
                first_name = validated_data.pop('first_name')
                last_name = validated_data.pop('last_name')
                business_name = validated_data.pop('business_name', '')
                
                # Get the default Free plan
                try:
                    free_plan = Plan.objects.get(plan_name='Free')
                except Plan.DoesNotExist:
                    # Create free plan if it doesn't exist
                    free_plan = Plan.objects.create(
                        plan_name='Free',
                        price=0,
                        max_campaigns=3,
                        max_displays=5,
                        max_images=10,
                        max_videos=0,
                        max_storage_gb=0.5,
                        has_video_support=False
                    )
                
                # Create user with free plan
                user = User.objects.create_user(
                    email=validated_data['email'],
                    password=validated_data['password'],
                    account_type=validated_data.get('account_type', 'personal'),
                    plan=free_plan
                )
                
                # Create user profile
                UserProfile.objects.create(
                    user=user,
                    first_name=first_name,
                    last_name=last_name
                )
                
                # If business account, create business
                if user.account_type == 'business':
                    business = Business.objects.create(
                        owner=user, 
                        name=business_name or f"{first_name} {last_name}'s Business"
                    )
                    BusinessMember.objects.create(
                        business=business, 
                        user=user, 
                        member_role='owner'
                    )
                
                return user
                
        except Exception as e:
            raise serializers.ValidationError(f"Registration failed: {str(e)}")

class PlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = Plan
        fields = '__all__'

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = '__all__'

class BusinessSerializer(serializers.ModelSerializer):
    class Meta:
        model = Business
        fields = '__all__'

class BusinessMemberSerializer(serializers.ModelSerializer):
    class Meta:
        model = BusinessMember
        fields = '__all__'

class CampaignSerializer(serializers.ModelSerializer):
    media_count = serializers.ReadOnlyField()
    total_duration = serializers.ReadOnlyField()
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    campaign_type_display = serializers.CharField(source='get_campaign_type_display', read_only=True)
    menu_name = serializers.CharField(source='menu.name', read_only=True)
    preview_url = serializers.SerializerMethodField()
    
    class Meta:
        model = Campaign
        fields = [
            'campaign_id', 'name', 'description', 'campaign_type', 'campaign_type_display',
            'menu', 'menu_name', 'menu_layout', 'auto_refresh_seconds', 'featured_rotation_seconds',
            'screen_orientation', 'normalize_to_orientation', 'status', 'status_display',
            'start_date', 'end_date', 'created_at', 'updated_at',
            'media_count', 'total_duration', 'preview_url'
        ]
        read_only_fields = ['campaign_id', 'created_at', 'updated_at', 'media_count', 'total_duration']
    
    def get_preview_url(self, obj):
        """Generate preview URL for menu campaigns"""
        if obj.campaign_type == 'menu' and obj.menu:
            preview_url = f"/tv-menu-enhanced.html?menu={obj.menu.menu_id}"
            preview_url += f"&layout={obj.menu_layout}"
            preview_url += f"&refresh={obj.auto_refresh_seconds}"
            preview_url += f"&rotate={obj.featured_rotation_seconds}"
            return preview_url
        return None
    
    def validate(self, data):
        """Validate menu campaign requirements"""
        campaign_type = data.get('campaign_type', 'media')
        menu = data.get('menu')
        
        if campaign_type == 'menu' and not menu:
            raise serializers.ValidationError("Menu campaigns must have a menu selected.")
        
        return data
        
    def update(self, instance, validated_data):
        # Update the instance
        instance = super().update(instance, validated_data) 
        # Automatically update status after any changes
        instance.update_status()
        return instance

class MediaSerializer(serializers.ModelSerializer):
    file_url = serializers.SerializerMethodField()
    media_type = serializers.CharField(read_only=True)

    class Meta:
        model = Media
        fields = ['media_id', 'name', 'description', 'file', 'file_url', 'media_type', 'uploaded_at']
        read_only_fields = ['media_id', 'uploaded_at']

    def get_file_url(self, obj):
        # Always return the public MinIO URL for the file (for frontend)
        if obj.file and hasattr(obj.file, 'url'):
            # If the url is already absolute, return as is
            if obj.file.url.startswith('http://') or obj.file.url.startswith('https://'):
                from django.conf import settings
                public_ep = getattr(settings, 'MINIO_PUBLIC_ENDPOINT', 'http://localhost:9000').rstrip('/')
                internal_ep = getattr(settings, 'AWS_S3_ENDPOINT_URL', '').rstrip('/')
                url = obj.file.url
                # If storage URL points at internal endpoint (e.g., http://minio:9000), rewrite to public endpoint
                if internal_ep and url.startswith(internal_ep):
                    return url.replace(internal_ep, public_ep, 1)
                return url
            # Otherwise, construct the public MinIO URL using settings
            from django.conf import settings
            endpoint = getattr(settings, 'MINIO_PUBLIC_ENDPOINT', 'http://localhost:9000')
            bucket = getattr(settings, 'AWS_STORAGE_BUCKET_NAME', 'media')
            file_path = obj.file.name.lstrip('/')
            return f"{endpoint}/{bucket}/{file_path}"
        return ''

    def validate_file(self, value):
        # Basic validation for allowed mime types and size
        import os
        import mimetypes
        from django.core.exceptions import ValidationError
        from django.conf import settings

        # Size limit (default 10MB)
        max_mb = float(getattr(settings, 'MAX_UPLOAD_MB', 10))
        if hasattr(value, 'size') and value.size > max_mb * 1024 * 1024:
            raise ValidationError(f"File too large. Max {int(max_mb)}MB allowed.")

        # Guess mime type from name if missing
        content_type = getattr(value, 'content_type', None) or mimetypes.guess_type(getattr(value, 'name', ''), strict=False)[0]
        if not content_type:
            raise ValidationError('Could not determine file type.')

        allowed_images = {'image/jpeg', 'image/png', 'image/webp', 'image/gif'}
        allowed_videos = {'video/mp4', 'video/webm', 'video/ogg'}
        if content_type not in allowed_images | allowed_videos:
            raise ValidationError('Unsupported file type. Allowed: images (jpg, png, webp, gif) and videos (mp4, webm, ogg).')

        # Attach detected content_type for use in create()
        value._detected_content_type = content_type
        return value

    def create(self, validated_data):
        # Auto-set media_type based on content_type/extension
        file_obj = validated_data.get('file')
        content_type = getattr(file_obj, '_detected_content_type', getattr(file_obj, 'content_type', None))
        media_type = 'image'
        if content_type and content_type.startswith('video/'):
            media_type = 'video'
        validated_data['media_type'] = media_type
        return super().create(validated_data)

    def validate(self, attrs):
        """Provide a defensive default for name if omitted and we have a file.

        This helps avoid 400 errors if the frontend forgets to send a name. The
        original filename (without path) will be used.
        """
        if not attrs.get('name'):
            file_obj = attrs.get('file')
            if file_obj and getattr(file_obj, 'name', None):
                import os
                attrs['name'] = os.path.basename(file_obj.name)
        return attrs

class CampaignMediaSerializer(serializers.ModelSerializer):
    class Meta:
        model = CampaignMedia
        fields = '__all__'

class DisplaySerializer(serializers.ModelSerializer):
    activated_at = serializers.DateTimeField(source='registered_at', read_only=True)
    default_campaign_name = serializers.CharField(source='default_campaign.name', read_only=True)
    
    class Meta:
        model = Display
        fields = ['display_id', 'name', 'location', 'device_id', 'activation_status', 'registered_at', 'activated_at', 'last_seen', 'default_campaign', 'default_campaign_name']
        read_only_fields = ['display_id', 'registered_at', 'activated_at', 'device_id', 'activation_status']

class ScheduleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Schedule
        fields = '__all__'

class SubscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subscription
        fields = '__all__'

class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = '__all__'

# --- Stripe Serializers ---
class StripeCustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = StripeCustomer
        fields = '__all__'

class StripeSubscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = StripeSubscription
        fields = '__all__'

class StripePaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = StripePayment
        fields = '__all__'

# --- Menu System Serializers ---
from .models import Menu, MenuCategory, MenuItem, POSIntegration, MenuItemPOSSync, POSUpdateLog, ApiKey

class MenuCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = MenuCategory
        fields = ['category_id', 'name', 'order']

class MenuItemSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    pos_sync_status = serializers.SerializerMethodField()
    
    class Meta:
        model = MenuItem
        fields = [
            'item_id', 'name', 'description', 'price', 'currency', 'available',
            'image', 'order', 'category', 'category_name', 'pos_item_id', 
            'last_pos_sync', 'promotion_flag', 'special_offer', 'pos_sync_status'
        ]
    
    def get_pos_sync_status(self, obj):
        try:
            sync = obj.pos_sync
            return {
                'synced': True,
                'last_sync': sync.last_pos_update,
                'conflicts': bool(sync.sync_conflicts)
            }
        except:
            return {'synced': False, 'last_sync': None, 'conflicts': False}

class MenuSerializer(serializers.ModelSerializer):
    categories = MenuCategorySerializer(many=True, read_only=True)
    items = MenuItemSerializer(many=True, read_only=True)
    items_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Menu
        fields = ['menu_id', 'name', 'active', 'created_at', 'updated_at', 'categories', 'items', 'items_count']
    
    def get_items_count(self, obj):
        return obj.items.count()

class POSUpdateRequestSerializer(serializers.Serializer):
    """Serializer for POS update requests"""
    item_id = serializers.IntegerField()
    name = serializers.CharField(max_length=255, required=False)
    description = serializers.CharField(required=False, allow_blank=True)
    price = serializers.DecimalField(max_digits=10, decimal_places=2, required=False)
    available = serializers.BooleanField(required=False)
    promotion_flag = serializers.BooleanField(required=False)
    special_offer = serializers.CharField(max_length=500, required=False, allow_blank=True)
    pos_item_id = serializers.CharField(max_length=100, required=False)

class POSBulkUpdateSerializer(serializers.Serializer):
    """Serializer for bulk POS updates"""
    updates = POSUpdateRequestSerializer(many=True)
    source_system = serializers.CharField(max_length=50, required=False, default='unknown')
    sync_timestamp = serializers.DateTimeField(required=False)

class POSIntegrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = POSIntegration
        fields = [
            'id', 'pos_system_type', 'api_endpoint', 'last_sync', 'sync_status',
            'error_message', 'sync_interval_minutes', 'auto_sync_enabled',
            'webhook_url', 'created_at', 'updated_at'
        ]

class MenuItemPOSSyncSerializer(serializers.ModelSerializer):
    menu_item_name = serializers.CharField(source='menu_item.name', read_only=True)
    
    class Meta:
        model = MenuItemPOSSync
        fields = [
            'id', 'menu_item', 'menu_item_name', 'pos_item_id', 'last_pos_update',
            'sync_conflicts', 'pos_name', 'pos_description', 'pos_price',
            'pos_available', 'pos_promotion_data'
        ]

class POSUpdateLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = POSUpdateLog
        fields = [
            'id', 'update_type', 'items_updated', 'items_failed',
            'update_data', 'error_details', 'timestamp', 'duration_seconds'
        ]

class ApiKeySerializer(serializers.ModelSerializer):
    key = serializers.CharField(write_only=True)  # Don't expose keys in responses
    
    class Meta:
        model = ApiKey
        fields = [
            'id', 'name', 'key', 'can_update_menus', 'can_read_analytics',
            'allowed_ips', 'last_used', 'usage_count', 'is_active',
            'created_at', 'expires_at'
        ]
        extra_kwargs = {
            'usage_count': {'read_only': True},
            'last_used': {'read_only': True},
        }
