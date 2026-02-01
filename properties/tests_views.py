from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from unittest.mock import patch

from properties.models import Property
from properties.forms import PropertyForm

User = get_user_model()


class PropertyModelTests(TestCase):
    """Test Property model"""
    
    def setUp(self):
        self.landlord = User.objects.create_user(
            username='landlord',
            email='landlord@example.com',
            password='testpass123',
            user_type='landlord'
        )
    
    def test_property_creation(self):
        """Test creating a property"""
        prop = Property.objects.create(
            landlord=self.landlord,
            name='Test Property',
            description='A test property',
            location='Accra',
            price=1000.00,
            bedrooms=2,
            bathrooms=1
        )
        
        self.assertEqual(prop.name, 'Test Property')
        self.assertEqual(prop.location, 'Accra')
        self.assertEqual(prop.price, 1000.00)
    
    def test_property_str_representation(self):
        """Test property string representation"""
        prop = Property.objects.create(
            landlord=self.landlord,
            name='Test Property',
            description='A test property',
            location='Accra',
            price=1000.00,
            bedrooms=2,
            bathrooms=1
        )
        
        self.assertIn('Test Property', str(prop))


class PropertyListViewTests(TestCase):
    """Test property list view"""
    
    def setUp(self):
        self.client = Client()
        self.landlord = User.objects.create_user(
            username='landlord',
            email='landlord@example.com',
            password='testpass123',
            user_type='landlord'
        )
        
        # Create test properties
        self.prop1 = Property.objects.create(
            landlord=self.landlord,
            name='Property 1',
            description='Test property 1',
            location='Accra',
            price=1000.00,
            bedrooms=2,
            bathrooms=1
        )
        
        self.prop2 = Property.objects.create(
            landlord=self.landlord,
            name='Property 2',
            description='Test property 2',
            location='Kumasi',
            price=2000.00,
            bedrooms=3,
            bathrooms=2
        )
    
    def test_property_list_view_accessible(self):
        """Test that property list view is accessible"""
        response = self.client.get(reverse('properties:property_list'))
        self.assertEqual(response.status_code, 200)
    
    def test_property_list_displays_properties(self):
        """Test that property list displays all properties"""
        response = self.client.get(reverse('properties:property_list'))
        
        self.assertContains(response, 'Property 1')
        self.assertContains(response, 'Property 2')
    
    def test_property_list_shows_correct_count(self):
        """Test that property list shows correct property count"""
        response = self.client.get(reverse('properties:property_list'))
        
        self.assertEqual(len(response.context['properties']), 2)
    
    def test_property_list_filter_by_location(self):
        """Test filtering properties by location"""
        response = self.client.get(
            reverse('properties:property_list') + '?location=Accra'
        )
        
        # Check if filtering works (implementation may vary)
        self.assertEqual(response.status_code, 200)
    
    def test_property_list_search(self):
        """Test searching for properties"""
        response = self.client.get(
            reverse('properties:property_list') + '?search=Property'
        )
        
        self.assertEqual(response.status_code, 200)


class PropertyDetailViewTests(TestCase):
    """Test property detail view"""
    
    def setUp(self):
        self.client = Client()
        self.landlord = User.objects.create_user(
            username='landlord',
            email='landlord@example.com',
            password='testpass123',
            user_type='landlord'
        )
        
        self.property = Property.objects.create(
            landlord=self.landlord,
            name='Test Property',
            description='A detailed test property',
            location='Accra',
            price=1000.00,
            bedrooms=2,
            bathrooms=1
        )
    
    def test_property_detail_view_accessible(self):
        """Test that property detail view is accessible"""
        response = self.client.get(
            reverse('properties:property_detail', kwargs={'id': self.property.id})
        )
        self.assertEqual(response.status_code, 200)
    
    def test_property_detail_shows_correct_info(self):
        """Test that property detail shows correct information"""
        response = self.client.get(
            reverse('properties:property_detail', kwargs={'id': self.property.id})
        )
        
        self.assertContains(response, 'Test Property')
        self.assertContains(response, 'A detailed test property')
        self.assertContains(response, 'Accra')
    
    def test_property_detail_404_for_non_existent(self):
        """Test that property detail returns 404 for non-existent property"""
        response = self.client.get(
            reverse('properties:property_detail', kwargs={'id': 99999})
        )
        self.assertEqual(response.status_code, 404)


class PropertyCreateViewTests(TestCase):
    """Test property creation view"""
    
    def setUp(self):
        self.client = Client()
        self.landlord = User.objects.create_user(
            username='landlord',
            email='landlord@example.com',
            password='testpass123',
            user_type='landlord'
        )
        self.tenant = User.objects.create_user(
            username='tenant',
            email='tenant@example.com',
            password='testpass123',
            user_type='tenant'
        )
    
    def test_create_property_requires_login(self):
        """Test that property creation requires login"""
        response = self.client.get(reverse('properties:property_create'))
        self.assertEqual(response.status_code, 302)  # Redirect to login
    
    def test_create_property_requires_landlord_role(self):
        """Test that only landlords can create properties"""
        self.client.login(username='tenant', password='testpass123')
        
        response = self.client.get(reverse('properties:property_create'))
        
        # Should either redirect or show error (depending on implementation)
        self.assertIn(response.status_code, [403, 302])
    
    def test_landlord_can_create_property(self):
        """Test that landlords can create properties"""
        self.client.login(username='landlord', password='testpass123')
        
        initial_count = Property.objects.count()
        
        response = self.client.post(
            reverse('properties:property_create'),
            {
                'name': 'New Property',
                'description': 'A new test property',
                'location': 'Accra',
                'price': 1500.00,
                'bedrooms': 3,
                'bathrooms': 2
            }
        )
        
        # Check property was created
        self.assertEqual(Property.objects.count(), initial_count + 1)
        
        new_property = Property.objects.latest('created_at')
        self.assertEqual(new_property.name, 'New Property')
        self.assertEqual(new_property.landlord, self.landlord)
    
    def test_create_property_form_validation(self):
        """Test property creation form validation"""
        self.client.login(username='landlord', password='testpass123')
        
        # Try to create property with missing required fields
        response = self.client.post(
            reverse('properties:property_create'),
            {
                'name': 'Incomplete Property',
                # Missing description, location, price, etc.
            }
        )
        
        # Form should fail validation
        self.assertEqual(response.status_code, 200)  # Re-render form with errors


class PropertyEditViewTests(TestCase):
    """Test property edit view"""
    
    def setUp(self):
        self.client = Client()
        self.landlord = User.objects.create_user(
            username='landlord',
            email='landlord@example.com',
            password='testpass123',
            user_type='landlord'
        )
        self.other_landlord = User.objects.create_user(
            username='other_landlord',
            email='other@example.com',
            password='testpass123',
            user_type='landlord'
        )
        
        self.property = Property.objects.create(
            landlord=self.landlord,
            name='Test Property',
            description='A test property',
            location='Accra',
            price=1000.00,
            bedrooms=2,
            bathrooms=1
        )
    
    def test_edit_property_requires_login(self):
        """Test that property edit requires login"""
        response = self.client.get(
            reverse('properties:property_edit', kwargs={'id': self.property.id})
        )
        self.assertEqual(response.status_code, 302)  # Redirect to login
    
    def test_owner_can_edit_property(self):
        """Test that property owner can edit the property"""
        self.client.login(username='landlord', password='testpass123')
        
        response = self.client.post(
            reverse('properties:property_edit', kwargs={'id': self.property.id}),
            {
                'name': 'Updated Property',
                'description': 'Updated description',
                'location': 'Kumasi',
                'price': 2000.00,
                'bedrooms': 3,
                'bathrooms': 2
            }
        )
        
        self.property.refresh_from_db()
        self.assertEqual(self.property.name, 'Updated Property')
        self.assertEqual(self.property.location, 'Kumasi')
    
    def test_non_owner_cannot_edit_property(self):
        """Test that non-owner cannot edit the property"""
        self.client.login(username='other_landlord', password='testpass123')
        
        response = self.client.get(
            reverse('properties:property_edit', kwargs={'id': self.property.id})
        )
        
        # Should return 404 or 403
        self.assertIn(response.status_code, [404, 403])
    
    def test_edit_property_404_for_non_existent(self):
        """Test that property edit returns 404 for non-existent property"""
        self.client.login(username='landlord', password='testpass123')
        
        response = self.client.get(
            reverse('properties:property_edit', kwargs={'id': 99999})
        )
        self.assertEqual(response.status_code, 404)


class PropertyDeleteViewTests(TestCase):
    """Test property deletion"""
    
    def setUp(self):
        self.client = Client()
        self.landlord = User.objects.create_user(
            username='landlord',
            email='landlord@example.com',
            password='testpass123',
            user_type='landlord'
        )
        
        self.property = Property.objects.create(
            landlord=self.landlord,
            name='Test Property',
            description='A test property',
            location='Accra',
            price=1000.00,
            bedrooms=2,
            bathrooms=1
        )
    
    def test_delete_property_requires_login(self):
        """Test that property deletion requires login"""
        response = self.client.post(
            reverse('properties:property_delete', kwargs={'id': self.property.id})
        )
        self.assertEqual(response.status_code, 302)  # Redirect to login
    
    def test_owner_can_delete_property(self):
        """Test that property owner can delete the property"""
        self.client.login(username='landlord', password='testpass123')
        
        property_id = self.property.id
        
        response = self.client.post(
            reverse('properties:property_delete', kwargs={'id': property_id})
        )
        
        # Check property was deleted
        with self.assertRaises(Property.DoesNotExist):
            Property.objects.get(id=property_id)
