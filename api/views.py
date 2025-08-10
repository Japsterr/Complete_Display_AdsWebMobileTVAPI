from rest_framework import viewsets
from .models import DisplayGroup, Tag, MediaApproval
from .serializers import DisplayGroupSerializer, TagSerializer, MediaApprovalSerializer
from rest_framework import permissions

# --- Display Grouping, Tagging, and Moderation ViewSets ---
class DisplayGroupViewSet(viewsets.ModelViewSet):
    queryset = DisplayGroup.objects.all()
    serializer_class = DisplayGroupSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [permissions.IsAuthenticated]

class MediaApprovalViewSet(viewsets.ModelViewSet):
    queryset = MediaApproval.objects.all()
    serializer_class = MediaApprovalSerializer
    permission_classes = [permissions.IsAuthenticated]
# Organization & User Management API Views
from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from .models import Organization, Membership, Invitation, AuditLog
from .serializers import OrganizationSerializer, MembershipSerializer, InvitationSerializer, AuditLogSerializer

class OrganizationViewSet(viewsets.ModelViewSet):
    queryset = Organization.objects.all()
    serializer_class = OrganizationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

class MembershipViewSet(viewsets.ModelViewSet):
    queryset = Membership.objects.all()
    serializer_class = MembershipSerializer
    permission_classes = [permissions.IsAuthenticated]

class InvitationViewSet(viewsets.ModelViewSet):
    queryset = Invitation.objects.all()
    serializer_class = InvitationSerializer
    permission_classes = [permissions.IsAuthenticated]

class AuditLogViewSet(viewsets.ModelViewSet):
    queryset = AuditLog.objects.all()
    serializer_class = AuditLogSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        # Automatically set the user to the current user if not provided
        if not serializer.validated_data.get('user'):
            serializer.save(user=self.request.user)
        else:
            serializer.save()
# Healthcheck endpoint
from rest_framework.decorators import api_view
from rest_framework.response import Response

@api_view(["GET"])
def healthcheck(request):
    return Response({"status": "ok"})
from rest_framework import generics, viewsets, permissions, status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes, throttle_classes
from django.utils import timezone
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
import random
import string
from datetime import timedelta
from .models import (
    Campaign, Media, Display, UserProfile, BusinessMember, 
    Schedule, RefreshToken as CustomRefreshToken, User, CampaignMedia,
    DeviceHeartbeat, MediaImpression, CampaignSession
)
from .serializers import (
    UserRegistrationSerializer, CampaignSerializer, MediaSerializer, 
    DisplaySerializer, UserProfileSerializer, ScheduleSerializer, UserSerializer,
    CampaignMediaSerializer
)
from .permissions import IsOwnerOrBusinessMember
from .utils import normalize_image_to_orientation, generate_activation_qr

# --- Throttling for activation endpoints ---
from rest_framework.throttling import AnonRateThrottle, UserRateThrottle

class ActivationAnonThrottle(AnonRateThrottle):
    rate = '20/min'

class ActivationUserThrottle(UserRateThrottle):
    rate = '60/min'

class ActivationAuthThrottle(UserRateThrottle):
    rate = '30/min'

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
                
                # Generate JWT tokens for immediate login
                from rest_framework_simplejwt.tokens import RefreshToken
                refresh = RefreshToken.for_user(user)
                
                return Response({
                    'access': str(refresh.access_token),
                    'refresh': str(refresh),
                    'user': {
                        'id': user.id,
                        'email': user.email,
                        'account_type': user.account_type,
                            'plan': user.plan.plan_name if user.plan else 'Free'
                    },
                    'message': 'Registration successful! Welcome to DisplayAds.'
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
        except User.DoesNotExist:
            print(f"User not found: {email}")
            return Response(
                {'detail': 'Invalid credentials.'}, 
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        # Authenticate user
        user = authenticate(username=email, password=password)
        print(f"Authentication result: {user}")
        
        if user is not None:
            if user.is_active:
                # Generate JWT tokens
                refresh = RefreshToken.for_user(user)
                return Response({
                    'access': str(refresh.access_token),
                    'refresh': str(refresh),
                    'user': {
                        'id': user.id,
                        'email': user.email,
                        'account_type': user.account_type,
                    }
                })
            else:
                return Response(
                    {'detail': 'Account is disabled.'}, 
                    status=status.HTTP_401_UNAUTHORIZED
                )
        else:
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
            # Use SimpleJWT's RefreshToken blacklist mechanism
            refresh_token = RefreshToken(token)
            refresh_token.blacklist()
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
        file = self.request.FILES.get('file')
        # Optional orientation hint from request (?target_orientation=portrait|landscape)
        target = self.request.query_params.get('target_orientation') or self.request.data.get('target_orientation') or 'portrait'

        # If it's an image, normalize to target orientation
        content_type = getattr(file, 'content_type', None)
        if file and content_type and content_type.startswith('image/'):
            try:
                processed = normalize_image_to_orientation(file.read(), 'landscape' if target == 'landscape' else 'portrait')
                from django.core.files.base import ContentFile
                # Replace uploaded content with processed PNG
                file_name = file.name.rsplit('.', 1)[0] + '.png'
                serializer.validated_data['file'] = ContentFile(processed, name=file_name)
            except Exception as e:
                # Fallback to original if processing fails
                pass

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
@throttle_classes([ActivationAnonThrottle, ActivationUserThrottle])
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
            # Device exists but not activated
            # If code expired (>15 min), generate new one
            code_expired = not display.activation_code_created_at or (timezone.now() - display.activation_code_created_at) > timedelta(minutes=15)
            if not display.activation_code or code_expired:
                activation_code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
                while Display.objects.filter(activation_code=activation_code).exists():
                    activation_code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
                display.activation_code = activation_code
                display.activation_code_created_at = timezone.now()
                display.save(update_fields=['activation_code', 'activation_code_created_at'])
            else:
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
            activation_code_created_at=timezone.now(),
            activation_status='pending',
            device_info=device_info,
            name=f"TV-{activation_code}",  # Default name
            # registered_by will be set when user activates
        )
    
    # Include QR code link for mobile app scanning (deep link or web link)
    base_url = request.build_absolute_uri('/')[:-1]
    activation_url = f"{base_url}/api/v1/devices/activate/?code={activation_code}"
    try:
        png_bytes = generate_activation_qr(activation_url)
        import base64
        qr_b64 = base64.b64encode(png_bytes).decode('ascii')
    except Exception:
        qr_b64 = None

    # TTL remaining (seconds)
    expires_in = None
    if display.activation_code_created_at:
        elapsed = (timezone.now() - display.activation_code_created_at).total_seconds()
        expires_in = max(0, int(900 - elapsed))

    return Response({
        'activation_code': activation_code,
        'status': 'pending',
        'activation_url': activation_url,
        'activation_qr_png_base64': qr_b64,
        'expires_in_seconds': expires_in,
        'message': 'Use this code (or QR) to activate your device'
    })

@api_view(['POST'])
@permission_classes([IsAuthenticated])
@throttle_classes([ActivationAuthThrottle])
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
        # Verify TTL (15 minutes)
        if not display.activation_code_created_at or (timezone.now() - display.activation_code_created_at) > timedelta(minutes=15):
            return Response({'error': 'Activation code has expired. Please generate a new code.'}, status=status.HTTP_400_BAD_REQUEST)
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
        
        # Get campaign media items (ensure public URLs)
        campaign_media = CampaignMedia.objects.filter(campaign=campaign).select_related('media')

        def to_public_url(file_field):
            if not file_field:
                return ''
            try:
                url = file_field.url
            except Exception:
                url = None
            if not url:
                return ''
            public_ep = getattr(settings, 'MINIO_PUBLIC_ENDPOINT', 'http://localhost:9000').rstrip('/')
            internal_ep = getattr(settings, 'AWS_S3_ENDPOINT_URL', '').rstrip('/')
            if url.startswith('http://') or url.startswith('https://'):
                if internal_ep and url.startswith(internal_ep):
                    return url.replace(internal_ep, public_ep, 1)
                return url
            bucket = getattr(settings, 'AWS_STORAGE_BUCKET_NAME', 'media')
            file_path = str(file_field.name).lstrip('/')
            return f"{public_ep}/{bucket}/{file_path}"

        media_items = []
        for cm in campaign_media:
            media_items.append({
                'media_id': cm.media.media_id,
                'file_path': to_public_url(cm.media.file),
                'media_type': cm.media.media_type,
                'duration': cm.display_duration_seconds,
                'name': cm.media.name,
            })
        
        return Response({
            'campaign': campaign.campaign_id,
            'campaign_name': campaign.name,
            'normalize_to_orientation': getattr(campaign, 'normalize_to_orientation', 'none'),
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
@throttle_classes([ActivationAnonThrottle, ActivationUserThrottle])
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
            expires_in = None
            if display.activation_code_created_at:
                elapsed = (timezone.now() - display.activation_code_created_at).total_seconds()
                expires_in = max(0, int(900 - elapsed))
            return Response({
                'status': display.activation_status,
                'activated': False,
                'activation_code': display.activation_code,
                'expires_in_seconds': expires_in,
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
import csv
from django.db import models

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

# --- Advanced Analytics: Summary and Exports ---
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def analytics_summary(request):
    """Summary analytics including device uptime approximation and time series.

    Optional query params:
    - start: ISO datetime or YYYY-MM-DD (defaults to now-24h for granularity=hour, now-7d for day)
    - end: ISO datetime or YYYY-MM-DD (defaults to now)
    - granularity: 'hour' | 'day' (default 'hour')
    """
    user = request.user

    # Select displays for user
    if user.account_type == 'personal':
        displays = Display.objects.filter(personal_user=user)
    elif user.account_type == 'business' and hasattr(user, 'owned_business'):
        displays = Display.objects.filter(business=user.owned_business)
    else:
        displays = Display.objects.none()

    now = timezone.now()

    # Parse time window
    from django.utils.dateparse import parse_datetime, parse_date
    from django.utils.timezone import make_aware, get_current_timezone
    granularity = request.query_params.get('granularity', 'hour')
    end_str = request.query_params.get('end')
    start_str = request.query_params.get('start')

    def _to_aware(dt_str):
        if not dt_str:
            return None
        dt = parse_datetime(dt_str)
        if dt is None:
            d = parse_date(dt_str)
            if d is not None:
                # Interpret as start of day local time
                from datetime import datetime as _dt
                dt = _dt(d.year, d.month, d.day)
        if dt is None:
            return None
        if timezone.is_naive(dt):
            dt = make_aware(dt, get_current_timezone())
        return dt

    end = _to_aware(end_str) or now
    if granularity == 'day':
        default_span = timedelta(days=7)
    else:
        default_span = timedelta(hours=24)
    start = _to_aware(start_str) or (end - default_span)

    # Clamp if inverted
    if end < start:
        start, end = end, start

    # Uptime approximation: heartbeats per device in window vs expected (1/min)
    uptime = []
    total_minutes = max(1, int((end - start).total_seconds() / 60))
    expected = total_minutes
    hb = DeviceHeartbeat.objects.filter(display__in=displays, timestamp__gte=start, timestamp__lte=end)
    hb_counts = {}
    for d_id, cnt in hb.values_list('display_id').annotate(models.Count('id')):
        hb_counts[d_id] = cnt
    for d in displays:
        count = hb_counts.get(d.display_id, 0)
        percent = min(100.0, round((count / expected) * 100.0, 1)) if expected else 0.0
        uptime.append({
            'display_id': d.display_id,
            'name': d.name,
            'online_now': bool(d.last_seen and (now - d.last_seen).total_seconds() < 120),
            'last_seen': d.last_seen.isoformat() if d.last_seen else None,
            'uptime_24h_percent': percent,
            'heartbeats_24h': count,
        })

    # Time series of impressions across window
    ts = []
    impressions = MediaImpression.objects.filter(display__in=displays, started_at__gte=start, started_at__lte=end)
    # Build buckets
    from collections import defaultdict
    buckets = defaultdict(int)
    if granularity == 'day':
        def bucket_key(dt):
            return dt.replace(hour=0, minute=0, second=0, microsecond=0)
        step = timedelta(days=1)
    else:
        def bucket_key(dt):
            return dt.replace(minute=0, second=0, microsecond=0)
        step = timedelta(hours=1)
    for imp in impressions.values_list('started_at', flat=True):
        key = bucket_key(imp)
        buckets[key] += 1
    # Produce ordered series
    cur = bucket_key(start)
    end_bucket = bucket_key(end)
    while cur <= end_bucket:
        ts.append({'timestamp': cur.isoformat(), 'count': buckets.get(cur, 0)})
        cur += step

    # Top media within window
    top_media = []
    media_counts = impressions.model.objects.filter(display__in=displays, started_at__gte=start, started_at__lte=end) \
        .values('media__name', 'campaign__name') \
        .annotate(total=models.Count('id'), total_duration=models.Sum('duration_shown')) \
        .order_by('-total')[:20]
    for row in media_counts:
        top_media.append({
            'media': row['media__name'],
            'campaign': row['campaign__name'],
            'total_impressions': row['total'],
            'total_duration': row['total_duration'] or 0,
        })

    return Response({
        'uptime': uptime,
        'impressions_timeseries_24h': ts,
        'top_media_7d': top_media,
    })

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def analytics_campaign_breakdown(request):
    """Per-campaign breakdown in a time window.

    Query params: start, end (ISO/Date), optional business/personal via auth.
    """
    user = request.user
    if user.account_type == 'personal':
        displays = Display.objects.filter(personal_user=user)
    elif user.account_type == 'business' and hasattr(user, 'owned_business'):
        displays = Display.objects.filter(business=user.owned_business)
    else:
        displays = Display.objects.none()

    from django.utils.dateparse import parse_datetime, parse_date
    from django.utils.timezone import make_aware, get_current_timezone

    def _to_aware(dt_str, *, end_inclusive: bool = False):
        """Parse a datetime/date string to an aware datetime.

        - If dt_str is YYYY-MM-DD and end_inclusive=True, returns end of day (23:59:59.999999).
        - If dt_str is YYYY-MM-DD and end_inclusive=False, returns start of day (00:00:00).
        """
        if not dt_str:
            return None
        dt = parse_datetime(dt_str)
        if dt is None:
            d = parse_date(dt_str)
            if d is not None:
                from datetime import datetime as _dt
                if end_inclusive:
                    dt = _dt(d.year, d.month, d.day, 23, 59, 59, 999999)
                else:
                    dt = _dt(d.year, d.month, d.day)
        else:
            # parse_datetime parsed a date string as midnight; detect plain date inputs
            if end_inclusive and dt.time() == getattr(dt, 'min').time():
                # Heuristic: if input looks like YYYY-MM-DD (no time separator), bump to end of day
                if ('T' not in dt_str) and (' ' not in dt_str):
                    dt = dt.replace(hour=23, minute=59, second=59, microsecond=999999)
        if dt is None:
            return None
        if timezone.is_naive(dt):
            dt = make_aware(dt, get_current_timezone())
        return dt

    now = timezone.now()
    end = _to_aware(request.query_params.get('end'), end_inclusive=True) or now
    start = _to_aware(request.query_params.get('start')) or (end - timedelta(days=7))
    if end < start:
        start, end = end, start

    qs = MediaImpression.objects.filter(display__in=displays, started_at__gte=start, started_at__lte=end)
    agg = qs.values('campaign__campaign_id', 'campaign__name').annotate(
        total_impressions=models.Count('id'),
        total_duration=models.Sum('duration_shown'),
        unique_displays=models.Count('display', distinct=True),
    ).order_by('-total_impressions')

    campaigns = []
    for row in agg:
        # Top media for campaign
        top_media = list(
            qs.filter(campaign__campaign_id=row['campaign__campaign_id']).values('media__name').annotate(
                total=models.Count('id'),
                total_duration=models.Sum('duration_shown'),
            ).order_by('-total')[:10]
        )
        campaigns.append({
            'campaign_id': row['campaign__campaign_id'],
            'campaign_name': row['campaign__name'],
            'total_impressions': row['total_impressions'],
            'total_duration': row['total_duration'] or 0,
            'unique_displays': row['unique_displays'],
            'top_media': [
                {
                    'media': tm['media__name'],
                    'total_impressions': tm['total'],
                    'total_duration': tm['total_duration'] or 0,
                } for tm in top_media
            ]
        })

    return Response({
        'start': start.isoformat(),
        'end': end.isoformat(),
        'campaigns': campaigns,
    })

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def export_impressions_csv(request):
    """Export impressions as CSV within optional start/end window (defaults last 7 days)"""
    user = request.user
    if user.account_type == 'personal':
        displays = Display.objects.filter(personal_user=user)
    elif user.account_type == 'business' and hasattr(user, 'owned_business'):
        displays = Display.objects.filter(business=user.owned_business)
    else:
        displays = Display.objects.none()

    from django.utils.dateparse import parse_datetime, parse_date
    from django.utils.timezone import make_aware, get_current_timezone
    now = timezone.now()
    def _to_aware(dt_str):
        if not dt_str:
            return None
        dt = parse_datetime(dt_str)
        if dt is None:
            d = parse_date(dt_str)
            if d is not None:
                from datetime import datetime as _dt
                dt = _dt(d.year, d.month, d.day)
        if dt is None:
            return None
        if timezone.is_naive(dt):
            dt = make_aware(dt, get_current_timezone())
        return dt
    end = _to_aware(request.query_params.get('end')) or now
    start = _to_aware(request.query_params.get('start')) or (end - timedelta(days=7))
    if end < start:
        start, end = end, start

    qs = MediaImpression.objects.filter(display__in=displays, started_at__gte=start, started_at__lte=end) \
        .select_related('display', 'campaign', 'media') \
        .order_by('-started_at')

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="impressions.csv"'
    writer = csv.writer(response)
    writer.writerow(['timestamp', 'display', 'campaign', 'media', 'duration_shown', 'scheduled_duration', 'completed', 'sequence_number', 'total_media_in_campaign'])
    for imp in qs:
        writer.writerow([
            imp.started_at.isoformat(),
            imp.display.name,
            imp.campaign.name,
            imp.media.name,
            imp.duration_shown,
            imp.scheduled_duration,
            int(imp.completed),
            imp.sequence_number,
            imp.total_media_in_campaign,
        ])
    return response

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def export_devices_csv(request):
    """Export devices with last_seen and uptime approximation within optional window (default 24h)"""
    user = request.user
    if user.account_type == 'personal':
        displays = Display.objects.filter(personal_user=user)
    elif user.account_type == 'business' and hasattr(user, 'owned_business'):
        displays = Display.objects.filter(business=user.owned_business)
    else:
        displays = Display.objects.none()

    from django.utils.dateparse import parse_datetime, parse_date
    from django.utils.timezone import make_aware, get_current_timezone
    now = timezone.now()
    def _to_aware(dt_str):
        if not dt_str:
            return None
        dt = parse_datetime(dt_str)
        if dt is None:
            d = parse_date(dt_str)
            if d is not None:
                from datetime import datetime as _dt
                dt = _dt(d.year, d.month, d.day)
        if dt is None:
            return None
        if timezone.is_naive(dt):
            dt = make_aware(dt, get_current_timezone())
        return dt
    end = _to_aware(request.query_params.get('end')) or now
    start = _to_aware(request.query_params.get('start')) or (end - timedelta(hours=24))
    if end < start:
        start, end = end, start

    total_minutes = max(1, int((end - start).total_seconds() / 60))
    expected = total_minutes
    hb = DeviceHeartbeat.objects.filter(display__in=displays, timestamp__gte=start, timestamp__lte=end)
    hb_counts = {}
    for d_id, cnt in hb.values_list('display_id').annotate(models.Count('id')):
        hb_counts[d_id] = cnt

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="devices_status.csv"'
    writer = csv.writer(response)
    writer.writerow(['display_id', 'name', 'location', 'status', 'last_seen', 'uptime_percent', 'heartbeats_window'])
    for d in displays:
        count = hb_counts.get(d.display_id, 0)
        percent = min(100.0, round((count / expected) * 100.0, 1)) if expected else 0.0
        writer.writerow([
            d.display_id,
            d.name,
            d.location or '',
            d.activation_status,
            d.last_seen.isoformat() if d.last_seen else '',
            percent,
            count,
        ])
    return response
