from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from django.core import mail
from django.contrib.auth import get_user_model
from api.models import EmailVerificationToken, PasswordResetToken
import json

User = get_user_model()

class EmailVerificationTests(APITestCase):
    """Test email verification functionality"""
    
    def setUp(self):
        self.registration_url = reverse('register')
        self.verification_url = reverse('verify-email')
        self.resend_url = reverse('resend-verification')
        self.login_url = reverse('login')
        
        self.user_data = {
            'email': 'test@example.com',
            'password': 'testpass123',
            'first_name': 'Test',
            'last_name': 'User',
            'account_type': 'personal'
        }
    
    def test_user_registration_creates_inactive_user(self):
        """Test that user registration creates an inactive user"""
        response = self.client.post(self.registration_url, self.user_data)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Check user is created but inactive
        user = User.objects.get(email=self.user_data['email'])
        self.assertFalse(user.is_active)
        
        # Check verification token is created
        self.assertTrue(EmailVerificationToken.objects.filter(user=user).exists())
        
        # Check email was sent
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn('Verify Your DisplayAds Email', mail.outbox[0].subject)
    
    def test_user_registration_sends_verification_email(self):
        """Test that registration sends verification email"""
        response = self.client.post(self.registration_url, self.user_data)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(len(mail.outbox), 1)
        
        email = mail.outbox[0]
        self.assertEqual(email.to, [self.user_data['email']])
        self.assertIn('verification_required', response.data)
        self.assertTrue(response.data['verification_required'])
    
    def test_inactive_user_cannot_login(self):
        """Test that inactive users cannot login"""
        # Create inactive user
        user = User.objects.create_user(
            email=self.user_data['email'],
            password=self.user_data['password'],
            is_active=False
        )
        
        login_data = {
            'email': self.user_data['email'],
            'password': self.user_data['password']
        }
        
        response = self.client.post(self.login_url, login_data)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn('email_verification_required', response.data)
        self.assertTrue(response.data['email_verification_required'])
    
    def test_email_verification_activates_user(self):
        """Test that email verification activates the user"""
        # Create inactive user and verification token
        user = User.objects.create_user(
            email=self.user_data['email'],
            password=self.user_data['password'],
            is_active=False
        )
        token = EmailVerificationToken.objects.create(user=user)
        
        verification_data = {'token': token.token}
        response = self.client.post(self.verification_url, verification_data)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Check user is now active
        user.refresh_from_db()
        self.assertTrue(user.is_active)
        
        # Check token is marked as used
        token.refresh_from_db()
        self.assertTrue(token.is_used)
    
    def test_invalid_verification_token(self):
        """Test verification with invalid token"""
        verification_data = {'token': 'invalid-token-123'}
        response = self.client.post(self.verification_url, verification_data)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('Token is invalid', str(response.data))
    
    def test_expired_verification_token(self):
        """Test verification with expired token"""
        user = User.objects.create_user(
            email=self.user_data['email'],
            password=self.user_data['password'],
            is_active=False
        )
        
        # Create expired token
        from django.utils import timezone
        from datetime import timedelta
        token = EmailVerificationToken.objects.create(user=user)
        token.expires_at = timezone.now() - timedelta(hours=1)
        token.save()
        
        verification_data = {'token': token.token}
        response = self.client.post(self.verification_url, verification_data)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('expired', str(response.data))
    
    def test_resend_verification_email(self):
        """Test resending verification email"""
        user = User.objects.create_user(
            email=self.user_data['email'],
            password=self.user_data['password'],
            is_active=False
        )
        
        resend_data = {'email': self.user_data['email']}
        response = self.client.post(self.resend_url, resend_data)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn('Verify Your DisplayAds Email', mail.outbox[0].subject)

class PasswordResetTests(APITestCase):
    """Test password reset functionality"""
    
    def setUp(self):
        self.reset_request_url = reverse('password-reset-request')
        self.reset_confirm_url = reverse('password-reset-confirm')
        self.login_url = reverse('login')
        
        self.user = User.objects.create_user(
            email='test@example.com',
            password='oldpassword123',
            is_active=True
        )
    
    def test_password_reset_request_sends_email(self):
        """Test that password reset request sends email"""
        request_data = {'email': self.user.email}
        response = self.client.post(self.reset_request_url, request_data)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn('Reset Your DisplayAds Password', mail.outbox[0].subject)
        
        # Check password reset token is created
        self.assertTrue(PasswordResetToken.objects.filter(user=self.user).exists())
    
    def test_password_reset_request_nonexistent_email(self):
        """Test password reset request with non-existent email"""
        request_data = {'email': 'nonexistent@example.com'}
        response = self.client.post(self.reset_request_url, request_data)
        
        # Should still return success for security (don't reveal user existence)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(mail.outbox), 0)
    
    def test_password_reset_confirm(self):
        """Test password reset confirmation"""
        # Create password reset token
        token = PasswordResetToken.objects.create(user=self.user)
        
        confirm_data = {
            'token': token.token,
            'new_password': 'newpassword123'
        }
        response = self.client.post(self.reset_confirm_url, confirm_data)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Check token is marked as used
        token.refresh_from_db()
        self.assertTrue(token.is_used)
        
        # Check user can login with new password
        login_data = {'email': self.user.email, 'password': 'newpassword123'}
        login_response = self.client.post(self.login_url, login_data)
        self.assertEqual(login_response.status_code, status.HTTP_200_OK)
    
    def test_password_reset_invalid_token(self):
        """Test password reset with invalid token"""
        confirm_data = {
            'token': 'invalid-token-123',
            'new_password': 'newpassword123'
        }
        response = self.client.post(self.reset_confirm_url, confirm_data)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('Token is invalid', str(response.data))
    
    def test_password_reset_expired_token(self):
        """Test password reset with expired token"""
        from django.utils import timezone
        from datetime import timedelta
        
        # Create expired token
        token = PasswordResetToken.objects.create(user=self.user)
        token.expires_at = timezone.now() - timedelta(hours=1)
        token.save()
        
        confirm_data = {
            'token': token.token,
            'new_password': 'newpassword123'
        }
        response = self.client.post(self.reset_confirm_url, confirm_data)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('expired', str(response.data))
    
    def test_password_reset_weak_password(self):
        """Test password reset with weak password"""
        token = PasswordResetToken.objects.create(user=self.user)
        
        confirm_data = {
            'token': token.token,
            'new_password': '123'  # Too short
        }
        response = self.client.post(self.reset_confirm_url, confirm_data)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('6 characters', str(response.data))

class IntegrationTests(APITestCase):
    """Test complete user flows"""
    
    def test_complete_registration_and_verification_flow(self):
        """Test complete user registration and email verification flow"""
        registration_url = reverse('register')
        verification_url = reverse('verify-email')
        login_url = reverse('login')
        
        user_data = {
            'email': 'integration@example.com',
            'password': 'testpass123',
            'first_name': 'Integration',
            'last_name': 'Test',
            'account_type': 'personal'
        }
        
        # 1. Register user
        response = self.client.post(registration_url, user_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # 2. Verify user cannot login yet
        login_data = {'email': user_data['email'], 'password': user_data['password']}
        response = self.client.post(login_url, login_data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        
        # 3. Get verification token from database
        user = User.objects.get(email=user_data['email'])
        token = EmailVerificationToken.objects.get(user=user)
        
        # 4. Verify email
        verification_data = {'token': token.token}
        response = self.client.post(verification_url, verification_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # 5. User can now login
        response = self.client.post(login_url, login_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
    
    def test_complete_password_reset_flow(self):
        """Test complete password reset flow"""
        reset_request_url = reverse('password-reset-request')
        reset_confirm_url = reverse('password-reset-confirm')
        login_url = reverse('login')
        
        # Create active user
        user = User.objects.create_user(
            email='resettest@example.com',
            password='oldpassword123',
            is_active=True
        )
        
        # 1. Request password reset
        request_data = {'email': user.email}
        response = self.client.post(reset_request_url, request_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # 2. Get reset token from database
        token = PasswordResetToken.objects.get(user=user)
        
        # 3. Confirm password reset
        confirm_data = {
            'token': token.token,
            'new_password': 'newpassword456'
        }
        response = self.client.post(reset_confirm_url, confirm_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # 4. Login with new password
        login_data = {'email': user.email, 'password': 'newpassword456'}
        response = self.client.post(login_url, login_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        
        # 5. Old password no longer works
        old_login_data = {'email': user.email, 'password': 'oldpassword123'}
        response = self.client.post(login_url, old_login_data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)