from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from api.models import Campaign, Display, Media, Plan, Business
import json

User = get_user_model()

class DigitalSignageAPITests(APITestCase):
    """Comprehensive test suite for Digital Signage API"""
    
    def setUp(self):
        """Set up test data"""
        # Create a test plan
        self.plan = Plan.objects.create(
            plan_name="Basic Plan",
            price=29.99,
            max_screens=5,
            max_storage_gb=10.0,
            has_multi_user=False
        )
        
        # Create test users
        self.personal_user = User.objects.create_user(
            email="personal@test.com",
            password="testpass123",
            account_type="personal",
            plan=self.plan
        )
        
        self.business_user = User.objects.create_user(
            email="business@test.com", 
            password="testpass123",
            account_type="business",
            plan=self.plan
        )
        
        # Create business for business user
        self.business = Business.objects.create(
            name="Test Business",
            owner=self.business_user
        )
    
    def get_jwt_token(self, user):
        """Get JWT token for user"""
        response = self.client.post('/api/v1/login/', {
            'email': user.email,
            'password': 'testpass123'
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        return response.data['access']
    
    def test_user_registration_personal(self):
        """Test personal user registration"""
        print("🧪 Testing personal user registration...")
        
        data = {
            'email': 'newuser@test.com',
            'password': 'securepass123',
            'account_type': 'personal'
        }
        
        response = self.client.post('/api/v1/register/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Verify user was created
        user = User.objects.get(email='newuser@test.com')
        self.assertEqual(user.account_type, 'personal')
        self.assertTrue(user.check_password('securepass123'))  # Password should be hashed
        print("✅ Personal user registration successful")
    
    def test_user_registration_business(self):
        """Test business user registration"""
        print("🧪 Testing business user registration...")
        
        data = {
            'email': 'newbusiness@test.com',
            'password': 'securepass123',
            'account_type': 'business'
        }
        
        response = self.client.post('/api/v1/register/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Verify user and business were created
        user = User.objects.get(email='newbusiness@test.com')
        self.assertEqual(user.account_type, 'business')
        self.assertTrue(hasattr(user, 'owned_business'))
        print("✅ Business user registration successful")
    
    def test_user_login(self):
        """Test user login and JWT token generation"""
        print("🧪 Testing user login...")
        
        data = {
            'email': 'personal@test.com',
            'password': 'testpass123'
        }
        
        response = self.client.post('/api/v1/login/', data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
        print("✅ User login successful")
    
    def test_token_refresh(self):
        """Test JWT token refresh"""
        print("🧪 Testing token refresh...")
        
        # Get initial tokens
        login_response = self.client.post('/api/v1/login/', {
            'email': 'personal@test.com',
            'password': 'testpass123'
        })
        refresh_token = login_response.data['refresh']
        
        # Test token refresh
        response = self.client.post('/api/v1/token/refresh/', {
            'refresh': refresh_token
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        print("✅ Token refresh successful")
    
    def test_campaign_crud_operations(self):
        """Test Campaign CRUD operations"""
        print("🧪 Testing Campaign CRUD operations...")
        
        # Get authentication token
        token = self.get_jwt_token(self.personal_user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        
        # Create campaign
        campaign_data = {
            'name': 'Test Campaign',
            'description': 'Test campaign description'
        }
        
        response = self.client.post('/api/v1/campaigns/', campaign_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        campaign_id = response.data['campaign_id']
        
        # Verify campaign ownership
        campaign = Campaign.objects.get(campaign_id=campaign_id)
        self.assertEqual(campaign.personal_user, self.personal_user)
        self.assertEqual(campaign.created_by, self.personal_user)
        
        # List campaigns
        response = self.client.get('/api/v1/campaigns/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(len(response.data) >= 1)
        
        # Get specific campaign
        response = self.client.get(f'/api/v1/campaigns/{campaign_id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Test Campaign')
        
        # Update campaign
        update_data = {'name': 'Updated Campaign Name'}
        response = self.client.patch(f'/api/v1/campaigns/{campaign_id}/', update_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Delete campaign
        response = self.client.delete(f'/api/v1/campaigns/{campaign_id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        
        print("✅ Campaign CRUD operations successful")
    
    def test_display_crud_operations(self):
        """Test Display CRUD operations"""
        print("🧪 Testing Display CRUD operations...")
        
        token = self.get_jwt_token(self.personal_user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        
        # Create display
        display_data = {
            'name': 'Test Display',
            'location': 'Office Lobby'
        }
        
        response = self.client.post('/api/v1/displays/', display_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        display_id = response.data['display_id']
        
        # Verify display ownership
        display = Display.objects.get(display_id=display_id)
        self.assertEqual(display.personal_user, self.personal_user)
        self.assertEqual(display.registered_by, self.personal_user)
        
        # List displays
        response = self.client.get('/api/v1/displays/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        print("✅ Display CRUD operations successful")
    
    def test_android_tv_endpoint(self):
        """Test Android TV endpoint"""
        print("🧪 Testing Android TV endpoint...")
        
        # Create a display first
        token = self.get_jwt_token(self.personal_user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        
        display_data = {
            'name': 'Android TV Display',
            'location': 'Conference Room'
        }
        
        response = self.client.post('/api/v1/displays/', display_data)
        display_id = response.data['display_id']
        
        # Test Android TV endpoint without authentication (as it should be)
        self.client.credentials()  # Remove authentication
        response = self.client.get(f'/api/v1/android-tv/?display_unique_identifier={display_id}')
        
        # Should return 404 because no campaign is assigned
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn('No campaign available', response.data['detail'])
        
        print("✅ Android TV endpoint working correctly")
    
    def test_business_team_invite(self):
        """Test business team invite functionality"""
        print("🧪 Testing business team invite...")
        
        token = self.get_jwt_token(self.business_user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        
        invite_data = {
            'email': 'newteammember@test.com'
        }
        
        response = self.client.post('/api/v1/team/invite/', invite_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('member_id', response.data)
        
        print("✅ Business team invite successful")
    
    def test_user_permissions(self):
        """Test that users can only access their own resources"""
        print("🧪 Testing user permissions...")
        
        # Create campaign as personal user
        token1 = self.get_jwt_token(self.personal_user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token1}')
        
        response = self.client.post('/api/v1/campaigns/', {
            'name': 'Personal Campaign',
            'description': 'Personal user campaign'
        })
        campaign_id = response.data['campaign_id']
        
        # Try to access as business user (should fail)
        token2 = self.get_jwt_token(self.business_user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token2}')
        
        response = self.client.get(f'/api/v1/campaigns/{campaign_id}/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        
        print("✅ User permissions working correctly")
    
    def test_password_security(self):
        """Test password security (hashing)"""
        print("🧪 Testing password security...")
        
        # Test that passwords are hashed
        user = User.objects.get(email='personal@test.com')
        self.assertNotEqual(user.password, 'testpass123')  # Should be hashed
        self.assertTrue(user.check_password('testpass123'))  # But should validate correctly
        
        # Test that registration response doesn't include password
        response = self.client.post('/api/v1/register/', {
            'email': 'securitytest@test.com',
            'password': 'plaintextpassword',
            'account_type': 'personal'
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertNotIn('password', response.data)
        
        print("✅ Password security verified")
    
    def test_logout_functionality(self):
        """Test logout functionality"""
        print("🧪 Testing logout functionality...")
        
        # Get tokens
        login_response = self.client.post('/api/v1/login/', {
            'email': 'personal@test.com',
            'password': 'testpass123'
        })
        refresh_token = login_response.data['refresh']
        access_token = login_response.data['access']
        
        # Test logout
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
        response = self.client.post('/api/v1/logout/', {
            'refresh': refresh_token
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        print("✅ Logout functionality working")

    def tearDown(self):
        """Clean up after tests"""
        pass  # Django handles test database cleanup automatically
