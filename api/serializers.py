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
                
                # Create user with free plan (inactive until email verified)
                user = User.objects.create_user(
                    email=validated_data['email'],
                    password=validated_data['password'],
                    account_type=validated_data.get('account_type', 'personal'),
                    plan=free_plan,
                    is_active=False  # User starts as inactive until email verified
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
    
    class Meta:
        model = Campaign
        fields = [
            'campaign_id', 'name', 'description', 'screen_orientation', 'status', 'status_display',
            'start_date', 'end_date', 'created_at', 'updated_at',
            'media_count', 'total_duration'
        ]
        read_only_fields = ['campaign_id', 'created_at', 'updated_at', 'media_count', 'total_duration']
        
    def update(self, instance, validated_data):
        # Update the instance
        instance = super().update(instance, validated_data) 
        # Automatically update status after any changes
        instance.update_status()
        return instance

class MediaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Media
        fields = ['media_id', 'name', 'description', 'file', 'uploaded_at']
        read_only_fields = ['media_id', 'uploaded_at']

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

# --- Email Verification and Password Reset Serializers ---
class PasswordResetRequestSerializer(serializers.Serializer):
    """Serializer for requesting a password reset"""
    email = serializers.EmailField()
    
    def validate_email(self, value):
        from .models import User
        try:
            user = User.objects.get(email=value)
            if not user.is_active:
                raise serializers.ValidationError("User account is not active.")
        except User.DoesNotExist:
            # Don't reveal that the user doesn't exist for security
            pass
        return value

class PasswordResetConfirmSerializer(serializers.Serializer):
    """Serializer for confirming password reset with token"""
    token = serializers.CharField(max_length=64)
    new_password = serializers.CharField(min_length=6, write_only=True)
    
    def validate_new_password(self, value):
        if len(value) < 6:
            raise serializers.ValidationError("Password must be at least 6 characters long.")
        return value
    
    def validate_token(self, value):
        from .models import PasswordResetToken
        try:
            token_obj = PasswordResetToken.objects.get(token=value)
            if not token_obj.is_valid():
                raise serializers.ValidationError("Token is invalid or expired.")
            self.token_obj = token_obj
        except PasswordResetToken.DoesNotExist:
            raise serializers.ValidationError("Token is invalid.")
        return value
    
    def save(self):
        """Reset the user's password"""
        user = self.token_obj.user
        user.set_password(self.validated_data['new_password'])
        user.save()
        
        # Mark token as used
        self.token_obj.is_used = True
        self.token_obj.save()
        
        return user

class EmailVerificationSerializer(serializers.Serializer):
    """Serializer for email verification"""
    token = serializers.CharField(max_length=64)
    
    def validate_token(self, value):
        from .models import EmailVerificationToken
        try:
            token_obj = EmailVerificationToken.objects.get(token=value)
            if not token_obj.is_valid():
                raise serializers.ValidationError("Token is invalid or expired.")
            self.token_obj = token_obj
        except EmailVerificationToken.DoesNotExist:
            raise serializers.ValidationError("Token is invalid.")
        return value
    
    def save(self):
        """Verify the user's email and activate account"""
        user = self.token_obj.user
        user.is_active = True
        user.save()
        
        # Mark token as used
        self.token_obj.is_used = True
        self.token_obj.save()
        
        return user

class ResendVerificationSerializer(serializers.Serializer):
    """Serializer for resending email verification"""
    email = serializers.EmailField()
    
    def validate_email(self, value):
        from .models import User
        try:
            user = User.objects.get(email=value)
            if user.is_active:
                raise serializers.ValidationError("User account is already verified.")
        except User.DoesNotExist:
            raise serializers.ValidationError("User not found.")
        return value
