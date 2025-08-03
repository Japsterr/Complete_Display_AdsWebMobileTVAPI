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
    password = serializers.CharField(write_only=True)
    class Meta:
        model = User
        fields = ['email', 'password', 'account_type', 'plan']

    def create(self, validated_data):
        with transaction.atomic():
            account_type = validated_data.get('account_type', 'free')  # Default to free tier
            user = User.objects.create_user(
                email=validated_data['email'],
                password=validated_data['password'],
                account_type=account_type,
                plan=validated_data.get('plan')
            )
            if account_type == 'business':
                business = Business.objects.create(owner=user, name=f"{user.email}'s Business")
                BusinessMember.objects.create(business=business, user=user, member_role='owner')
            return user

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
    class Meta:
        model = Campaign
        fields = ['campaign_id', 'name', 'description', 'created_at']
        read_only_fields = ['campaign_id', 'created_at']

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
