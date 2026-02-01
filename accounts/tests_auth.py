from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse

User = get_user_model()


class UserRegistrationTests(TestCase):
    """Test user registration"""
    
    def setUp(self):
        self.client = Client()
    
    def test_registration_page_accessible(self):
        """Test that registration page is accessible"""
        response = self.client.get(reverse('accounts:register'))
        self.assertEqual(response.status_code, 200)
    
    def test_user_registration_successful(self):
        """Test successful user registration"""
        initial_count = User.objects.count()
        
        response = self.client.post(
            reverse('accounts:register'),
            {
                'username': 'newuser',
                'email': 'newuser@example.com',
                'password1': 'testpass123!@',
                'password2': 'testpass123!@',
                'user_type': 'tenant'
            }
        )
        
        # User should be created
        self.assertEqual(User.objects.count(), initial_count + 1)
    
    def test_registration_password_mismatch(self):
        """Test that mismatched passwords are rejected"""
        initial_count = User.objects.count()
        
        response = self.client.post(
            reverse('accounts:register'),
            {
                'username': 'newuser',
                'email': 'newuser@example.com',
                'password1': 'testpass123!@',
                'password2': 'different_password',
                'user_type': 'tenant'
            }
        )
        
        # User should not be created
        self.assertEqual(User.objects.count(), initial_count)
    
    def test_registration_duplicate_username(self):
        """Test that duplicate username is rejected"""
        User.objects.create_user(
            username='existinguser',
            email='existing@example.com',
            password='testpass123',
            user_type='tenant'
        )
        
        initial_count = User.objects.count()
        
        response = self.client.post(
            reverse('accounts:register'),
            {
                'username': 'existinguser',
                'email': 'newuser@example.com',
                'password1': 'testpass123!@',
                'password2': 'testpass123!@',
                'user_type': 'tenant'
            }
        )
        
        # No new user should be created
        self.assertEqual(User.objects.count(), initial_count)
    
    def test_registration_landlord_type(self):
        """Test registration as landlord"""
        response = self.client.post(
            reverse('accounts:register'),
            {
                'username': 'landlord_user',
                'email': 'landlord@example.com',
                'password1': 'testpass123!@',
                'password2': 'testpass123!@',
                'user_type': 'landlord'
            }
        )
        
        user = User.objects.get(username='landlord_user')
        self.assertEqual(user.user_type, 'landlord')


class UserLoginTests(TestCase):
    """Test user login"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            user_type='tenant'
        )
    
    def test_login_page_accessible(self):
        """Test that login page is accessible"""
        response = self.client.get(reverse('accounts:login'))
        self.assertEqual(response.status_code, 200)
    
    def test_user_login_successful(self):
        """Test successful user login"""
        response = self.client.post(
            reverse('accounts:login'),
            {
                'username': 'testuser',
                'password': 'testpass123'
            }
        )
        
        # User should be authenticated
        self.assertTrue(response.wsgi_request.user.is_authenticated)
    
    def test_login_invalid_credentials(self):
        """Test login with invalid credentials"""
        response = self.client.post(
            reverse('accounts:login'),
            {
                'username': 'testuser',
                'password': 'wrongpassword'
            }
        )
        
        # User should not be authenticated
        self.assertFalse(response.wsgi_request.user.is_authenticated)
    
    def test_login_non_existent_user(self):
        """Test login with non-existent user"""
        response = self.client.post(
            reverse('accounts:login'),
            {
                'username': 'nonexistent',
                'password': 'testpass123'
            }
        )
        
        self.assertFalse(response.wsgi_request.user.is_authenticated)


class UserLogoutTests(TestCase):
    """Test user logout"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            user_type='tenant'
        )
    
    def test_user_logout(self):
        """Test user logout"""
        self.client.login(username='testuser', password='testpass123')
        
        response = self.client.get(reverse('accounts:logout'))
        
        # User should be logged out
        self.assertFalse(response.wsgi_request.user.is_authenticated)


class UserProfileTests(TestCase):
    """Test user profile"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            user_type='tenant'
        )
    
    def test_profile_page_requires_login(self):
        """Test that profile page requires login"""
        response = self.client.get(reverse('accounts:profile'))
        self.assertEqual(response.status_code, 302)  # Redirect to login
    
    def test_profile_page_accessible_when_logged_in(self):
        """Test that profile page is accessible when logged in"""
        self.client.login(username='testuser', password='testpass123')
        
        response = self.client.get(reverse('accounts:profile'))
        self.assertEqual(response.status_code, 200)
    
    def test_profile_shows_user_info(self):
        """Test that profile shows user information"""
        self.client.login(username='testuser', password='testpass123')
        
        response = self.client.get(reverse('accounts:profile'))
        
        self.assertContains(response, 'testuser')
        self.assertContains(response, 'test@example.com')


class UserEditProfileTests(TestCase):
    """Test user profile editing"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            user_type='tenant'
        )
    
    def test_edit_profile_requires_login(self):
        """Test that profile editing requires login"""
        response = self.client.get(reverse('accounts:edit_profile'))
        self.assertEqual(response.status_code, 302)  # Redirect to login
    
    def test_edit_profile_email(self):
        """Test editing user email"""
        self.client.login(username='testuser', password='testpass123')
        
        response = self.client.post(
            reverse('accounts:edit_profile'),
            {
                'email': 'newemail@example.com',
                'first_name': 'Test',
                'last_name': 'User'
            }
        )
        
        self.user.refresh_from_db()
        self.assertEqual(self.user.email, 'newemail@example.com')
    
    def test_edit_profile_duplicate_email(self):
        """Test that duplicate email is rejected"""
        other_user = User.objects.create_user(
            username='otheruser',
            email='other@example.com',
            password='testpass123',
            user_type='tenant'
        )
        
        self.client.login(username='testuser', password='testpass123')
        
        response = self.client.post(
            reverse('accounts:edit_profile'),
            {
                'email': 'other@example.com',
                'first_name': 'Test',
                'last_name': 'User'
            }
        )
        
        # Email should not be changed
        self.user.refresh_from_db()
        self.assertEqual(self.user.email, 'test@example.com')


class UserPasswordChangeTests(TestCase):
    """Test user password change"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='oldpassword123',
            user_type='tenant'
        )
    
    def test_change_password_requires_login(self):
        """Test that password change requires login"""
        response = self.client.get(reverse('accounts:change_password'))
        self.assertEqual(response.status_code, 302)  # Redirect to login
    
    def test_change_password_successful(self):
        """Test successful password change"""
        self.client.login(username='testuser', password='oldpassword123')
        
        # First verify we can login with old password
        self.client.logout()
        login_result = self.client.login(username='testuser', password='oldpassword123')
        self.assertTrue(login_result, "Should be able to login with original password")
        
        # Now change the password
        response = self.client.post(
            reverse('accounts:change_password'),
            {
                'oldpassword': 'oldpassword123',
                'new_password1': 'newpassword123!@',
                'new_password2': 'newpassword123!@'
            }
        )
        
        # Should redirect after successful change
        if response.status_code != 302:
            # If not a redirect, check what the form errors are
            if hasattr(response, 'context') and 'form' in response.context:
                self.fail(f"Form errors: {response.context['form'].errors}")
            else:
                self.fail(f"Expected redirect (302), got {response.status_code}")
        
        # Should be able to login with new password
        self.client.logout()
        login_result = self.client.login(username='testuser', password='newpassword123!@')
        self.assertTrue(login_result, "Should be able to login with new password")
    
    def test_change_password_incorrect_old_password(self):
        """Test password change with incorrect old password"""
        self.client.login(username='testuser', password='oldpassword123')
        
        response = self.client.post(
            reverse('accounts:change_password'),
            {
                'oldpassword': 'wrongoldpassword',
                'new_password1': 'newpassword123!@',
                'new_password2': 'newpassword123!@'
            }
        )
        
        # Should not be able to login with new password
        self.client.logout()
        login_result = self.client.login(username='testuser', password='newpassword123!@')
        self.assertFalse(login_result)
    
    def test_change_password_mismatch(self):
        """Test password change with mismatched passwords"""
        self.client.login(username='testuser', password='oldpassword123')
        
        response = self.client.post(
            reverse('accounts:change_password'),
            {
                'oldpassword': 'oldpassword123',
                'new_password1': 'newpassword123!@',
                'new_password2': 'differentpassword!@'
            }
        )
        
        # Should still be able to login with old password
        self.client.logout()
        login_result = self.client.login(username='testuser', password='oldpassword123')
        self.assertTrue(login_result)
