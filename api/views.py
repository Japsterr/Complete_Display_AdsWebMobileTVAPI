from rest_framework import generics, viewsets, permissions, status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from django.utils import timezone
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
import random
import string
from .models import (
    Campaign, Media, Display, UserProfile, BusinessMember, 
    Schedule, RefreshToken as CustomRefreshToken, User, CampaignMedia,
    DeviceHeartbeat, MediaImpression, CampaignSession
)
from .serializers import (
    UserRegistrationSerializer, CampaignSerializer, MediaSerializer, 
    DisplaySerializer, UserProfileSerializer, ScheduleSerializer, UserSerializer,
    CampaignMediaSerializer, PasswordResetRequestSerializer, PasswordResetConfirmSerializer,
    EmailVerificationSerializer, ResendVerificationSerializer
)
from .permissions import IsOwnerOrBusinessMember

# Health check endpoint for mobile app
@api_view(['GET'])
@permission_classes([AllowAny])
def health_check(request):
    """Simple health check endpoint for mobile app connectivity testing"""
    return Response({
        'status': 'healthy',
        'message': 'DisplayAds API is running',
        'timestamp': timezone.now(),
        'version': '1.0.0'
    })

class UserRegistrationView(generics.CreateAPIView):
    serializer_class = UserRegistrationSerializer
    permission_classes = [permissions.AllowAny]
    
    def create(self, request, *args, **kwargs):
        print("=== REGISTRATION VIEW CALLED ===")
        print(f"Request data: {request.data}")
        
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            try:
                user = serializer.save()
                
                # Create email verification token
                from .models import EmailVerificationToken
                verification_token = EmailVerificationToken.objects.create(user=user)
                
                # Generate verification URL (adapt this based on your frontend)
                verification_url = f"{settings.ALLOWED_HOSTS[0] if settings.ALLOWED_HOSTS else 'localhost:3000'}/verify-email?token={verification_token.token}"
                
                # Send verification email
                context = {
                    'user': user,
                    'verification_url': verification_url,
                    'token': verification_token.token
                }
                
                html_message = render_to_string('email/email_verification.html', context)
                
                send_mail(
                    subject='Verify Your DisplayAds Email Address',
                    message=f'Click this link to verify your email: {verification_url}',
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[user.email],
                    html_message=html_message,
                    fail_silently=False,
                )
                
                return Response({
                    'message': 'Registration successful! Please check your email to verify your account before logging in.',
                    'email': user.email,
                    'verification_required': True
                }, status=status.HTTP_201_CREATED)
                
            except Exception as e:
                print(f"Registration error: {str(e)}")
                return Response({
                    'error': f'Registration failed: {str(e)}'
                }, status=status.HTTP_400_BAD_REQUEST)
        else:
            print(f"Serializer errors: {serializer.errors}")
            return Response({
                'error': 'Registration failed. Please check your input.',
                'details': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_profile(request):
    """Get current user's profile information"""
    serializer = UserSerializer(request.user)
    return Response(serializer.data)

class CustomLoginView(APIView):
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        print("=== LOGIN VIEW CALLED ===")
        print(f"Request data: {request.data}")
        
        email = request.data.get('email')
        password = request.data.get('password')
        
        print(f"Login attempt - Email: {email}, Password provided: {bool(password)}")
        
        if not email or not password:
            print("Missing email or password")
            return Response(
                {'detail': 'Email and password are required.'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check if user exists
        try:
            user_check = User.objects.get(email=email)
            print(f"User found: {user_check.email}, Active: {user_check.is_active}")
            
            # Check password manually for inactive users
            if user_check.check_password(password):
                if user_check.is_active:
                    # Generate JWT tokens
                    refresh = RefreshToken.for_user(user_check)
                    return Response({
                        'access': str(refresh.access_token),
                        'refresh': str(refresh),
                        'user': {
                            'id': user_check.id,
                            'email': user_check.email,
                            'account_type': user_check.account_type,
                        }
                    })
                else:
                    return Response(
                        {
                            'detail': 'Please verify your email address before logging in.',
                            'email_verification_required': True,
                            'email': user_check.email
                        }, 
                        status=status.HTTP_401_UNAUTHORIZED
                    )
            else:
                return Response(
                    {'detail': 'Invalid credentials.'}, 
                    status=status.HTTP_401_UNAUTHORIZED
                )
                
        except User.DoesNotExist:
            print(f"User not found: {email}")
            return Response(
                {'detail': 'Invalid credentials.'}, 
                status=status.HTTP_401_UNAUTHORIZED
            )

@api_view(['GET', 'PATCH'])
@permission_classes([IsAuthenticated])
def user_profile(request):
    """Get or update current user's profile information"""
    if request.method == 'GET':
        serializer = UserSerializer(request.user)
        return Response(serializer.data)
    
    elif request.method == 'PATCH':
        # Only allow updating certain fields
        allowed_fields = ['first_name', 'last_name']
        update_data = {k: v for k, v in request.data.items() if k in allowed_fields}
        
        serializer = UserSerializer(request.user, data=update_data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserProfileViewSet(viewsets.ModelViewSet):
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        # Users can only access their own profile
        return UserProfile.objects.filter(user=self.request.user)

class CampaignViewSet(viewsets.ModelViewSet):
    queryset = Campaign.objects.all()
    serializer_class = CampaignSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrBusinessMember]

    def get_queryset(self):
        user = self.request.user
        if user.account_type == 'personal':
            return Campaign.objects.filter(personal_user=user)
        elif user.account_type == 'business' and hasattr(user, 'owned_business'):
            return Campaign.objects.filter(business=user.owned_business)
        return Campaign.objects.none()

    def perform_create(self, serializer):
        user = self.request.user
        data = {}
        if user.account_type == 'personal':
            data['personal_user'] = user
        elif user.account_type == 'business' and hasattr(user, 'owned_business'):
            data['business'] = user.owned_business
        data['created_by'] = user
        serializer.save(**data)

class MediaViewSet(viewsets.ModelViewSet):
    queryset = Media.objects.all()
    serializer_class = MediaSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrBusinessMember]

    def get_queryset(self):
        user = self.request.user
        if user.account_type == 'personal':
            return Media.objects.filter(personal_user=user)
        elif user.account_type == 'business' and hasattr(user, 'owned_business'):
            return Media.objects.filter(business=user.owned_business)
        return Media.objects.none()

    def perform_create(self, serializer):
        user = self.request.user
        data = {}
        if user.account_type == 'personal':
            data['personal_user'] = user
        elif user.account_type == 'business' and hasattr(user, 'owned_business'):
            data['business'] = user.owned_business
        data['uploaded_by'] = user
        serializer.save(**data)

class DisplayViewSet(viewsets.ModelViewSet):
    queryset = Display.objects.all()
    serializer_class = DisplaySerializer
    permission_classes = [IsAuthenticated, IsOwnerOrBusinessMember]

    def get_queryset(self):
        user = self.request.user
        if user.account_type == 'personal':
            return Display.objects.filter(personal_user=user)
        elif user.account_type == 'business' and hasattr(user, 'owned_business'):
            return Display.objects.filter(business=user.owned_business)
        return Display.objects.none()

    def perform_create(self, serializer):
        user = self.request.user
        data = {}
        if user.account_type == 'personal':
            data['personal_user'] = user
        elif user.account_type == 'business' and hasattr(user, 'owned_business'):
            data['business'] = user.owned_business
        data['registered_by'] = user
        serializer.save(**data)

class TeamInviteView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        email = request.data.get('email')
        
        if not hasattr(user, 'owned_business'):
            return Response({'detail': 'Only business owners can invite.'}, status=403)
        
        try:
            invited_user, created = User.objects.get_or_create(
                email=email, 
                defaults={'account_type': 'business'}
            )
            member, created = BusinessMember.objects.get_or_create(
                business=user.owned_business,
                user=invited_user,
                defaults={'member_role': 'viewer'}
            )
            return Response({
                'detail': 'Invite sent.', 
                'member_id': member.member_id,
                'created': created
            })
        except Exception as e:
            return Response({'detail': str(e)}, status=400)

class AndroidTVDisplayView(APIView):
    permission_classes = [permissions.AllowAny]  # Allow Android TV devices to access

    def get(self, request):
        display_id = request.query_params.get('display_unique_identifier')
        if not display_id:
            return Response({'detail': 'Missing display_unique_identifier.'}, status=400)
        
        try:
            display_id = int(display_id)
            display = Display.objects.get(pk=display_id)
        except (ValueError, Display.DoesNotExist):
            return Response({'detail': 'Display not found.'}, status=404)
        
        now = timezone.now()
        schedule = (Schedule.objects
            .filter(display=display, start_datetime__lte=now, end_datetime__gte=now)
            .order_by('-priority')
            .first())
        
        if schedule:
            return Response({
                'campaign': schedule.campaign.campaign_id, 
                'schedule': ScheduleSerializer(schedule).data
            })
        elif display.default_campaign:
            return Response({
                'campaign': display.default_campaign.campaign_id, 
                'schedule': None
            })
        else:
            return Response({'detail': 'No campaign available.'}, status=404)

class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        token = request.data.get('refresh')
        if not token:
            return Response({'detail': 'No refresh token provided.'}, status=400)
        
        try:
            # Add token to blacklist by creating a RefreshToken record
            RefreshToken.objects.create(
                user=request.user, 
                token=token, 
                expires_at=timezone.now()
            )
            return Response({'detail': 'Logged out successfully.'}, status=200)
        except Exception as e:
            return Response({'detail': str(e)}, status=400)

# === ViewSets ===
class CampaignViewSet(viewsets.ModelViewSet):
    serializer_class = CampaignSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrBusinessMember]
    queryset = Campaign.objects.all()
    
    def get_queryset(self):
        user = self.request.user
        if user.account_type == 'business' and hasattr(user, 'owned_business'):
            campaigns = Campaign.objects.filter(business=user.owned_business)
        else:
            campaigns = Campaign.objects.filter(personal_user=user)
        
        # Update status for all campaigns before returning
        for campaign in campaigns:
            campaign.update_status()
        
        return campaigns
    
    def perform_create(self, serializer):
        user = self.request.user
        if user.account_type == 'business' and hasattr(user, 'owned_business'):
            campaign = serializer.save(business=user.owned_business, created_by=user)
        else:
            campaign = serializer.save(personal_user=user, created_by=user)
        
        # Update status after creation
        campaign.update_status()
        
    def perform_update(self, serializer):
        campaign = serializer.save()
        # Status will be updated by the serializer's update method

class MediaViewSet(viewsets.ModelViewSet):
    serializer_class = MediaSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrBusinessMember]
    queryset = Media.objects.all()
    
    def get_queryset(self):
        user = self.request.user
        if user.account_type == 'business' and hasattr(user, 'owned_business'):
            return Media.objects.filter(business=user.owned_business)
        else:
            return Media.objects.filter(personal_user=user)
    
    def perform_create(self, serializer):
        user = self.request.user
        if user.account_type == 'business' and hasattr(user, 'owned_business'):
            serializer.save(business=user.owned_business, uploaded_by=user)
        else:
            serializer.save(personal_user=user, uploaded_by=user)

class DisplayViewSet(viewsets.ModelViewSet):
    serializer_class = DisplaySerializer
    permission_classes = [IsAuthenticated, IsOwnerOrBusinessMember]
    queryset = Display.objects.all()
    
    def get_queryset(self):
        user = self.request.user
        if user.account_type == 'business' and hasattr(user, 'owned_business'):
            return Display.objects.filter(business=user.owned_business)
        else:
            return Display.objects.filter(personal_user=user)
    
    def perform_create(self, serializer):
        user = self.request.user
        if user.account_type == 'business' and hasattr(user, 'owned_business'):
            serializer.save(business=user.owned_business, registered_by=user)
        else:
            serializer.save(personal_user=user, registered_by=user)

class UserProfileViewSet(viewsets.ModelViewSet):
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]
    queryset = UserProfile.objects.all()
    
    def get_queryset(self):
        return UserProfile.objects.filter(user=self.request.user)

class CampaignMediaViewSet(viewsets.ModelViewSet):
    serializer_class = CampaignMediaSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrBusinessMember]
    queryset = CampaignMedia.objects.all()


    def get_queryset(self):
        # For individual operations (GET/PATCH/DELETE on specific items), return all
        # For list operations with campaign filter, filter by campaign
        campaign_id = self.request.query_params.get('campaign')
        if campaign_id and self.action == 'list':
            return CampaignMedia.objects.filter(campaign_id=campaign_id)
        elif self.action in ['retrieve', 'update', 'partial_update', 'destroy']:
            # For individual operations, return all to allow access by primary key
            return CampaignMedia.objects.all()
        return CampaignMedia.objects.none()
    
    def perform_create(self, serializer):
        serializer.save()


# === Device Activation Views ===

@api_view(['POST'])
@permission_classes([AllowAny])  # TV devices need to call this before authentication
def request_activation_code(request):
    """
    TV device calls this to get an activation code
    POST /api/v1/devices/request-activation/
    Body: { "device_id": "unique_device_identifier", "device_info": {...} }
    """
    device_id = request.data.get('device_id')
    device_info = request.data.get('device_info', {})
    
    if not device_id:
        return Response(
            {'error': 'device_id is required'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Check if device already exists
    try:
        display = Display.objects.get(device_id=device_id)
        if display.activation_status == 'active':
            return Response({
                'status': 'already_activated',
                'message': 'Device is already activated',
                'display_name': display.name
            })
        else:
            # Device exists but not activated, return existing code
            activation_code = display.activation_code
    except Display.DoesNotExist:
        # Generate new activation code
        activation_code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
        
        # Ensure code is unique
        while Display.objects.filter(activation_code=activation_code).exists():
            activation_code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
        
        # Create new display record
        display = Display.objects.create(
            device_id=device_id,
            activation_code=activation_code,
            activation_status='pending',
            device_info=device_info,
            name=f"TV-{activation_code}",  # Default name
            # registered_by will be set when user activates
        )
    
    return Response({
        'activation_code': activation_code,
        'status': 'pending',
        'message': 'Use this code in the web dashboard to activate your device'
    })

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def activate_device(request):
    """
    Web user calls this to activate a device using the activation code
    POST /api/v1/devices/activate/
    Body: { "activation_code": "ABC123", "display_name": "Living Room TV", "location": "Main Office" }
    """
    activation_code = request.data.get('activation_code')
    display_name = request.data.get('display_name', '')
    location = request.data.get('location', '')
    
    if not activation_code:
        return Response(
            {'error': 'activation_code is required'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        display = Display.objects.get(activation_code=activation_code, activation_status='pending')
    except Display.DoesNotExist:
        return Response(
            {'error': 'Invalid or already used activation code'}, 
            status=status.HTTP_404_NOT_FOUND
        )
    
    # Activate the device
    user = request.user
    display.activation_status = 'active'
    display.registered_by = user
    display.last_seen = timezone.now()
    
    # Update display info if provided
    if display_name:
        display.name = display_name
    if location:
        display.location = location
    
    # Assign to user (personal vs business logic)
    if hasattr(user, 'owned_business') and user.owned_business:
        display.business = user.owned_business
        display.personal_user = None
    else:
        display.personal_user = user
        display.business = None
    
    display.save()
    
    return Response({
        'status': 'activated',
        'message': f'Device "{display.name}" has been successfully activated',
        'display': {
            'id': display.display_id,
            'name': display.name,
            'location': display.location,
            'device_id': display.device_id,
            'activated_at': display.registered_at
        }
    })

@api_view(['GET'])
@permission_classes([AllowAny])
def get_device_campaign(request):
    """
    TV device calls this to get current campaign content
    GET /api/v1/devices/current-campaign/?device_id=unique_device_identifier
    """
    device_id = request.query_params.get('device_id')
    
    if not device_id:
        return Response(
            {'error': 'device_id is required'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        display = Display.objects.get(device_id=device_id, activation_status='active')
        
        # Update last seen
        display.last_seen = timezone.now()
        display.save()
        
        # Check for scheduled campaigns first
        now = timezone.now()
        schedule = (Schedule.objects
            .filter(display=display, start_datetime__lte=now, end_datetime__gte=now)
            .order_by('-priority')
            .first())
        
        campaign = None
        if schedule:
            campaign = schedule.campaign
        elif display.default_campaign:
            campaign = display.default_campaign
        
        if not campaign:
            return Response(
                {'error': 'No campaign assigned to this display'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Get campaign media items
        campaign_media = CampaignMedia.objects.filter(campaign=campaign).select_related('media')
        
        media_items = []
        for cm in campaign_media:
            media_items.append({
                'media_id': cm.media.media_id,
                'file_path': cm.media.file.url if cm.media.file else '',
                'media_type': cm.media.media_type,
                'duration': cm.display_duration_seconds,
                'name': cm.media.name,
            })
        
        return Response({
            'campaign': campaign.campaign_id,
            'campaign_name': campaign.name,
            'media_items': media_items,
            'schedule': ScheduleSerializer(schedule).data if schedule else None
        })
        
    except Display.DoesNotExist:
        return Response(
            {'error': 'Device not found or not activated'}, 
            status=status.HTTP_404_NOT_FOUND
        )

@api_view(['POST'])
@permission_classes([AllowAny])
def check_activation_status(request):
    """
    TV device calls this to check if it has been activated
    POST /api/v1/devices/check-activation/
    Body: { "device_id": "unique_device_identifier" }
    """
    device_id = request.data.get('device_id')
    
    if not device_id:
        return Response(
            {'error': 'device_id is required'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        display = Display.objects.get(device_id=device_id)
        
        if display.activation_status == 'active':
            # Update last seen
            display.last_seen = timezone.now()
            display.save()
            
            return Response({
                'status': 'active',
                'activated': True,
                'display_name': display.name,
                'location': display.location,
                'message': 'Device is activated and ready to use'
            })
        else:
            return Response({
                'status': display.activation_status,
                'activated': False,
                'activation_code': display.activation_code,
                'message': 'Device is not yet activated'
            })
            
    except Display.DoesNotExist:
        return Response(
            {'error': 'Device not found'}, 
            status=status.HTTP_404_NOT_FOUND
        )

# TV Simulator view
from django.http import HttpResponse
from django.conf import settings
import os

def tv_simulator_view(request):
    """Serve the TV simulator HTML file"""
    file_path = os.path.join(settings.BASE_DIR, 'tv-simulator.html')
    
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
        return HttpResponse(content, content_type='text/html')
    except FileNotFoundError:
        return HttpResponse('TV Simulator not found', status=404)

# Analytics and Tracking Endpoints

@api_view(['POST'])
@permission_classes([AllowAny])
def device_heartbeat(request):
    """Record device heartbeat and status"""
    device_id = request.data.get('device_id')
    
    if not device_id:
        return Response({'error': 'device_id required'}, status=400)
    
    try:
        display = Display.objects.get(device_id=device_id)
        
        # Update last_seen
        display.last_seen = timezone.now()
        display.save()
        
        # Record heartbeat
        heartbeat = DeviceHeartbeat.objects.create(
            display=display,
            device_status=request.data.get('status', 'online'),
            current_campaign=display.default_campaign,
            device_info=request.data.get('device_info', {})
        )
        
        return Response({
            'status': 'recorded',
            'timestamp': heartbeat.timestamp.isoformat()
        })
        
    except Display.DoesNotExist:
        return Response({'error': 'Device not found'}, status=404)

@api_view(['POST'])
@permission_classes([AllowAny])
def record_media_impression(request):
    """Record when a media item starts/completes displaying"""
    device_id = request.data.get('device_id')
    media_id = request.data.get('media_id')
    campaign_id = request.data.get('campaign_id')
    
    if not all([device_id, media_id, campaign_id]):
        return Response({'error': 'device_id, media_id, and campaign_id required'}, status=400)
    
    try:
        display = Display.objects.get(device_id=device_id)
        media = Media.objects.get(media_id=media_id)
        campaign = Campaign.objects.get(campaign_id=campaign_id)
        
        impression = MediaImpression.objects.create(
            display=display,
            campaign=campaign,
            media=media,
            duration_shown=request.data.get('duration_shown', 0),
            scheduled_duration=request.data.get('scheduled_duration', 10),  # Default 10 seconds
            completed=request.data.get('completed', False),
            sequence_number=request.data.get('sequence_number', 0),
            total_media_in_campaign=request.data.get('total_media_in_campaign', 1)
        )
        
        return Response({
            'status': 'recorded',
            'impression_id': impression.id
        })
        
    except (Display.DoesNotExist, Media.DoesNotExist, Campaign.DoesNotExist) as e:
        return Response({'error': str(e)}, status=404)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def analytics_dashboard(request):
    """Get analytics data for dashboard"""
    user = request.user
    
    # Get user's displays
    if user.account_type == 'personal':
        displays = Display.objects.filter(personal_user=user)
    elif user.account_type == 'business' and hasattr(user, 'owned_business'):
        displays = Display.objects.filter(business=user.owned_business)
    else:
        displays = Display.objects.none()
    
    # Get recent impressions
    recent_impressions = MediaImpression.objects.filter(
        display__in=displays
    ).select_related('display', 'campaign', 'media').order_by('-started_at')[:50]
    
    # Get device status
    device_status = []
    for display in displays:
        last_heartbeat = display.heartbeats.first()
        status = {
            'display_id': display.display_id,
            'name': display.name,
            'last_seen': display.last_seen.isoformat() if display.last_seen else None,
            'status': 'online' if last_heartbeat and 
                     (timezone.now() - last_heartbeat.timestamp).seconds < 120 else 'offline',
            'current_campaign': display.default_campaign.name if display.default_campaign else None
        }
        device_status.append(status)
    
    # Get campaign performance
    campaign_stats = {}
    for impression in recent_impressions:
        campaign_name = impression.campaign.name
        if campaign_name not in campaign_stats:
            campaign_stats[campaign_name] = {
                'total_impressions': 0,
                'total_duration': 0,
                'unique_displays': set()
            }
        
        campaign_stats[campaign_name]['total_impressions'] += 1
        campaign_stats[campaign_name]['total_duration'] += impression.duration_shown
        campaign_stats[campaign_name]['unique_displays'].add(impression.display.display_id)
    
    # Convert sets to counts
    for stats in campaign_stats.values():
        stats['unique_displays'] = len(stats['unique_displays'])
    
    return Response({
        'device_status': device_status,
        'campaign_performance': campaign_stats,
        'recent_impressions': [
            {
                'timestamp': imp.started_at.isoformat(),
                'display': imp.display.name,
                'campaign': imp.campaign.name,
                'media': imp.media.name,
                'duration': imp.duration_shown,
                'completed': imp.completed
            }
            for imp in recent_impressions
        ]
    })

# --- Email Verification and Password Reset Views ---

class PasswordResetRequestView(APIView):
    """Request a password reset token"""
    permission_classes = [AllowAny]
    
    def post(self, request):
        serializer = PasswordResetRequestSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            
            try:
                user = User.objects.get(email=email)
                
                # Create or update password reset token
                from .models import PasswordResetToken
                # Invalidate any existing tokens
                PasswordResetToken.objects.filter(user=user, is_used=False).update(is_used=True)
                
                # Create new token
                reset_token = PasswordResetToken.objects.create(user=user)
                
                # Generate reset URL (adapt this based on your frontend)
                reset_url = f"{settings.ALLOWED_HOSTS[0] if settings.ALLOWED_HOSTS else 'localhost:3000'}/reset-password?token={reset_token.token}"
                
                # Send password reset email
                context = {
                    'user': user,
                    'reset_url': reset_url,
                    'token': reset_token.token
                }
                
                html_message = render_to_string('email/password_reset.html', context)
                
                send_mail(
                    subject='Reset Your DisplayAds Password',
                    message=f'Click this link to reset your password: {reset_url}',
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[email],
                    html_message=html_message,
                    fail_silently=False,
                )
                
            except User.DoesNotExist:
                # Don't reveal that user doesn't exist for security
                pass
            
            return Response({
                'message': 'If an account with that email exists, we have sent a password reset link.'
            }, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class PasswordResetConfirmView(APIView):
    """Confirm password reset with token"""
    permission_classes = [AllowAny]
    
    def post(self, request):
        serializer = PasswordResetConfirmSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            
            return Response({
                'message': 'Password has been reset successfully. You can now log in with your new password.'
            }, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class EmailVerificationView(APIView):
    """Verify email address with token"""
    permission_classes = [AllowAny]
    
    def post(self, request):
        serializer = EmailVerificationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            
            return Response({
                'message': 'Email verified successfully. Your account is now active.',
                'user': {
                    'id': user.id,
                    'email': user.email,
                    'is_active': user.is_active
                }
            }, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ResendVerificationEmailView(APIView):
    """Resend email verification"""
    permission_classes = [AllowAny]
    
    def post(self, request):
        serializer = ResendVerificationSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            
            try:
                user = User.objects.get(email=email)
                
                # Create or update email verification token
                from .models import EmailVerificationToken
                verification_token, created = EmailVerificationToken.objects.get_or_create(
                    user=user,
                    defaults={'is_used': False}
                )
                
                if not created:
                    # Reset existing token
                    verification_token.is_used = False
                    verification_token.save()
                
                # Generate verification URL (adapt this based on your frontend)
                verification_url = f"{settings.ALLOWED_HOSTS[0] if settings.ALLOWED_HOSTS else 'localhost:3000'}/verify-email?token={verification_token.token}"
                
                # Send verification email
                context = {
                    'user': user,
                    'verification_url': verification_url,
                    'token': verification_token.token
                }
                
                html_message = render_to_string('email/email_verification.html', context)
                
                send_mail(
                    subject='Verify Your DisplayAds Email Address',
                    message=f'Click this link to verify your email: {verification_url}',
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[email],
                    html_message=html_message,
                    fail_silently=False,
                )
                
                return Response({
                    'message': 'Verification email sent successfully.'
                }, status=status.HTTP_200_OK)
                
            except User.DoesNotExist:
                return Response({
                    'error': 'User not found.'
                }, status=status.HTTP_404_NOT_FOUND)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
