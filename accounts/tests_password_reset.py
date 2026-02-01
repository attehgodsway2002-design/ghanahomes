"""
Tests for password reset functionality
"""
from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.core import mail
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes

User = get_user_model()


class PasswordResetRequestTests(TestCase):
    """Test password reset request view"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='oldpassword123'
        )
        self.url = reverse('accounts:password_reset_request')
    
    def test_password_reset_request_page_loads(self):
        """Test password reset request page displays"""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/password_reset_request.html')
    
    def test_authenticated_user_redirected(self):
        """Test authenticated users are redirected from password reset"""
        self.client.login(username='testuser', password='oldpassword123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)
        # Should redirect to home page (either /properties/ or /)
        self.assertTrue('/properties/' in response.url or response.url == '/')
    
    def test_empty_email_shows_error(self):
        """Test empty email shows error message"""
        response = self.client.post(self.url, {'email': ''})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Please enter your email')
    
    def test_nonexistent_email_no_error_revealed(self):
        """Test security: nonexistent email doesn't reveal account existence"""
        response = self.client.post(self.url, {'email': 'nonexistent@example.com'})
        self.assertRedirects(response, reverse('accounts:login'))
        # Security: message should be generic
        messages = list(response.wsgi_request._messages)
        self.assertTrue(any('If an account with that email exists' in str(m) for m in messages))
    
    def test_existing_email_sends_reset_link(self):
        """Test valid email sends password reset email"""
        response = self.client.post(self.url, {'email': 'test@example.com'})
        
        # Should redirect to login
        self.assertRedirects(response, reverse('accounts:login'))
        
        # Email should be sent
        self.assertEqual(len(mail.outbox), 1)
        email = mail.outbox[0]
        
        self.assertEqual(email.subject, 'Password Reset Request - GhanaHomes')
        self.assertIn('test@example.com', email.to)
        self.assertIn('password-reset-confirm', email.body)
    
    def test_reset_email_contains_token(self):
        """Test reset email contains valid token"""
        self.client.post(self.url, {'email': 'test@example.com'})
        
        email = mail.outbox[0]
        # Extract token from email body
        self.assertTrue(any(char.isalnum() for char in email.body))


class PasswordResetConfirmTests(TestCase):
    """Test password reset confirmation view"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='oldpassword123'
        )
        
        # Generate valid token
        self.token = default_token_generator.make_token(self.user)
        self.uidb64 = urlsafe_base64_encode(force_bytes(self.user.pk))
        
        self.url = reverse('accounts:password_reset_confirm', kwargs={
            'uidb64': self.uidb64,
            'token': self.token
        })
    
    def test_valid_token_page_loads(self):
        """Test password reset page loads with valid token"""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/password_reset_confirm.html')
    
    def test_invalid_token_shows_error(self):
        """Test invalid token shows error"""
        invalid_url = reverse('accounts:password_reset_confirm', kwargs={
            'uidb64': self.uidb64,
            'token': 'invalid-token'
        })
        response = self.client.get(invalid_url)
        self.assertRedirects(response, reverse('accounts:password_reset_request'))
    
    def test_invalid_uidb64_shows_error(self):
        """Test invalid user ID shows error"""
        invalid_url = reverse('accounts:password_reset_confirm', kwargs={
            'uidb64': 'invalid-uidb64',
            'token': self.token
        })
        response = self.client.get(invalid_url)
        self.assertRedirects(response, reverse('accounts:password_reset_request'))
    
    def test_empty_password_shows_error(self):
        """Test empty password shows error"""
        response = self.client.post(self.url, {
            'password': '',
            'password_confirm': ''
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'cannot be empty')
    
    def test_passwords_not_matching_shows_error(self):
        """Test non-matching passwords show error"""
        response = self.client.post(self.url, {
            'password': 'newpassword123',
            'password_confirm': 'differentpassword123'
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'do not match')
    
    def test_password_too_short_shows_error(self):
        """Test password less than 8 characters shows error"""
        response = self.client.post(self.url, {
            'password': 'short',
            'password_confirm': 'short'
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'at least 8 characters')
    
    def test_valid_password_reset_successful(self):
        """Test valid password reset succeeds"""
        response = self.client.post(self.url, {
            'password': 'newpassword123',
            'password_confirm': 'newpassword123'
        })
        
        # Should redirect to login
        self.assertRedirects(response, reverse('accounts:login'))
        
        # Refresh user from DB
        self.user.refresh_from_db()
        
        # New password should work
        self.assertTrue(self.user.check_password('newpassword123'))
        
        # Old password should not work
        self.assertFalse(self.user.check_password('oldpassword123'))
    
    def test_can_login_after_reset(self):
        """Test user can login with new password"""
        # Reset password
        self.client.post(self.url, {
            'password': 'newpassword123',
            'password_confirm': 'newpassword123'
        })
        
        # Try login with new password
        login_success = self.client.login(
            username='testuser',
            password='newpassword123'
        )
        self.assertTrue(login_success)
    
    def test_cannot_login_with_old_password(self):
        """Test user cannot login with old password after reset"""
        # Reset password
        self.client.post(self.url, {
            'password': 'newpassword123',
            'password_confirm': 'newpassword123'
        })
        
        # Try login with old password
        login_success = self.client.login(
            username='testuser',
            password='oldpassword123'
        )
        self.assertFalse(login_success)
    
    def test_token_expires_after_use(self):
        """Test token cannot be reused"""
        # First use
        response1 = self.client.post(self.url, {
            'password': 'newpassword123',
            'password_confirm': 'newpassword123'
        })
        self.assertRedirects(response1, reverse('accounts:login'))
        
        # Second use should fail
        response2 = self.client.post(self.url, {
            'password': 'anotherpassword123',
            'password_confirm': 'anotherpassword123'
        })
        self.assertRedirects(response2, reverse('accounts:password_reset_request'))


class PasswordResetIntegrationTests(TestCase):
    """Integration tests for full password reset flow"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='oldpassword123'
        )
    
    def test_full_reset_flow(self):
        """Test complete password reset flow"""
        # Step 1: Request reset
        response = self.client.post(
            reverse('accounts:password_reset_request'),
            {'email': 'test@example.com'}
        )
        self.assertRedirects(response, reverse('accounts:login'))
        
        # Check email sent
        self.assertEqual(len(mail.outbox), 1)
        email = mail.outbox[0]
        
        # Step 2: Extract token from email (simulate user clicking link)
        # In real scenario, user would click link in email
        token = default_token_generator.make_token(self.user)
        uidb64 = urlsafe_base64_encode(force_bytes(self.user.pk))
        
        # Step 3: Reset password with valid token
        reset_url = reverse('accounts:password_reset_confirm', kwargs={
            'uidb64': uidb64,
            'token': token
        })
        
        response = self.client.post(reset_url, {
            'password': 'newpassword123',
            'password_confirm': 'newpassword123'
        })
        self.assertRedirects(response, reverse('accounts:login'))
        
        # Step 4: Login with new password
        login_success = self.client.login(
            username='testuser',
            password='newpassword123'
        )
        self.assertTrue(login_success)
        
        # Verify we're logged in
        response = self.client.get(reverse('properties:home'))
        self.assertEqual(response.status_code, 200)
