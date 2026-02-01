from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.core import mail
from unittest.mock import patch, MagicMock
import json
import uuid

from payments.models import Payment
from subscriptions.models import Subscription, SubscriptionPlan
from payments.utils import verify_webhook_signature, format_amount_for_paystack

User = get_user_model()


class PaymentModelTests(TestCase):
    """Test Payment model"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            user_type='tenant'
        )
        self.plan = SubscriptionPlan.objects.create(
            name='Basic',
            description='Basic plan',
            base_price=100.00,
        )
        self.subscription = Subscription.objects.create(
            user=self.user,
            plan=self.plan,
            duration=1,
            status='inactive'
        )
    
    def test_payment_creation(self):
        """Test creating a payment"""
        payment = Payment.objects.create(
            user=self.user,
            subscription=self.subscription,
            amount=100.00,
            currency='GHS',
            status='pending',
            paystack_reference=f"GH-{uuid.uuid4().hex[:12].upper()}"
        )
        self.assertEqual(payment.status, 'pending')
        self.assertEqual(payment.amount, 100.00)
        self.assertEqual(payment.currency, 'GHS')
    
    def test_payment_str_representation(self):
        """Test payment string representation"""
        payment = Payment.objects.create(
            user=self.user,
            subscription=self.subscription,
            amount=100.00,
            currency='GHS',
            status='pending',
            paystack_reference=f"GH-{uuid.uuid4().hex[:12].upper()}"
        )
        self.assertIn('testuser', str(payment))
        self.assertIn('100.00', str(payment))


class PaymentInitializationTests(TestCase):
    """Test payment initialization flow"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            user_type='tenant'
        )
        self.plan = SubscriptionPlan.objects.create(
            name='Basic',
            description='Basic plan',
            base_price=100.00,
        )
        self.subscription = Subscription.objects.create(
            user=self.user,
            plan=self.plan,
            duration=1,
            status='inactive'
        )
    
    def test_initialize_payment_requires_login(self):
        """Test that payment initialization requires login"""
        response = self.client.get(
            reverse('payments:initialize', kwargs={'subscription_id': self.subscription.id})
        )
        self.assertEqual(response.status_code, 302)  # Redirect to login
    
    def test_initialize_payment_creates_payment_record(self):
        """Test that initialize_payment creates a Payment record"""
        self.client.login(username='testuser', password='testpass123')
        
        initial_count = Payment.objects.count()
        response = self.client.get(
            reverse('payments:initialize', kwargs={'subscription_id': self.subscription.id})
        )
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Payment.objects.count(), initial_count + 1)
        
        payment = Payment.objects.latest('created_at')
        self.assertEqual(payment.user, self.user)
        self.assertEqual(payment.subscription, self.subscription)
        self.assertEqual(payment.status, 'pending')
    
    def test_initialize_payment_404_for_non_existent_subscription(self):
        """Test that initialize_payment returns 404 for non-existent subscription"""
        self.client.login(username='testuser', password='testpass123')
        
        response = self.client.get(
            reverse('payments:initialize', kwargs={'subscription_id': 99999})
        )
        self.assertEqual(response.status_code, 404)
    
    def test_initialize_payment_404_for_other_users_subscription(self):
        """Test that user cannot initialize payment for another user's subscription"""
        other_user = User.objects.create_user(
            username='otheruser',
            email='other@example.com',
            password='testpass123',
            user_type='tenant'
        )
        other_subscription = Subscription.objects.create(
            user=other_user,
            plan=self.plan,
            duration=1,
            status='inactive'
        )
        
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(
            reverse('payments:initialize', kwargs={'subscription_id': other_subscription.id})
        )
        self.assertEqual(response.status_code, 404)


class ProcessPaymentTests(TestCase):
    """Test payment processing"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            user_type='tenant'
        )
        self.plan = SubscriptionPlan.objects.create(
            name='Basic',
            description='Basic plan',
            base_price=100.00,
        )
        self.subscription = Subscription.objects.create(
            user=self.user,
            plan=self.plan,
            duration=1,
            status='inactive'
        )
        self.payment = Payment.objects.create(
            user=self.user,
            subscription=self.subscription,
            amount=100.00,
            currency='GHS',
            status='pending',
            paystack_reference=f"GH-{uuid.uuid4().hex[:12].upper()}"
        )
        self.client.login(username='testuser', password='testpass123')
    
    def test_process_payment_requires_post(self):
        """Test that process_payment requires POST method"""
        response = self.client.get(
            reverse('payments:process', kwargs={'payment_id': self.payment.id})
        )
        self.assertEqual(response.status_code, 302)  # Redirect
    
    def test_process_payment_requires_login(self):
        """Test that process_payment requires login"""
        self.client.logout()
        response = self.client.post(
            reverse('payments:process', kwargs={'payment_id': self.payment.id})
        )
        self.assertEqual(response.status_code, 302)  # Redirect to login
    
    def test_process_payment_404_for_non_existent_payment(self):
        """Test that process_payment returns 404 for non-existent payment"""
        response = self.client.post(
            reverse('payments:process', kwargs={'payment_id': 99999})
        )
        self.assertEqual(response.status_code, 404)
    
    def test_process_payment_rejects_non_pending_payment(self):
        """Test that process_payment rejects already-processed payments"""
        self.payment.status = 'completed'
        self.payment.save()
        
        response = self.client.post(
            reverse('payments:process', kwargs={'payment_id': self.payment.id})
        )
        self.assertEqual(response.status_code, 302)  # Redirect with error
    
    @patch('payments.views.get_paystack_instance')
    def test_process_payment_successful_initialization(self, mock_paystack):
        """Test successful payment initialization with Paystack"""
        # Mock Paystack response
        mock_response = MagicMock()
        mock_response.status = True
        mock_response.message = 'Authorization URL created'
        mock_response.data = {
            'authorization_url': 'https://checkout.paystack.com/test',
            'access_code': 'test_access_code_123',
            'reference': self.payment.paystack_reference
        }
        
        mock_paystack.return_value.transactions.initialize.return_value = mock_response
        
        response = self.client.post(
            reverse('payments:process', kwargs={'payment_id': self.payment.id})
        )
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['content-type'], 'application/json')
        
        data = json.loads(response.content)
        self.assertTrue(data['status'])
        self.assertIn('authorization_url', data['data'])
        self.assertIn('access_code', data['data'])


class RetryPaymentTests(TestCase):
    """Test payment retry functionality"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            user_type='tenant'
        )
        self.plan = SubscriptionPlan.objects.create(
            name='Basic',
            description='Basic plan',
            base_price=100.00,
        )
        self.subscription = Subscription.objects.create(
            user=self.user,
            plan=self.plan,
            duration=1,
            status='inactive'
        )
        self.client.login(username='testuser', password='testpass123')
    
    def test_retry_payment_creates_new_payment(self):
        """Test that retry_payment creates a new Payment record"""
        initial_count = Payment.objects.count()
        
        response = self.client.post(
            reverse('payments:retry', kwargs={'subscription_id': self.subscription.id})
        )
        
        self.assertEqual(Payment.objects.count(), initial_count + 1)
        self.assertEqual(response.status_code, 302)  # Redirect
    
    def test_retry_payment_requires_post(self):
        """Test that retry_payment requires POST"""
        response = self.client.get(
            reverse('payments:retry', kwargs={'subscription_id': self.subscription.id})
        )
        self.assertEqual(response.status_code, 302)  # Redirect
    
    def test_retry_payment_404_for_non_existent_subscription(self):
        """Test that retry_payment returns 404 for non-existent subscription"""
        response = self.client.post(
            reverse('payments:retry', kwargs={'subscription_id': 99999})
        )
        self.assertEqual(response.status_code, 404)


class PaymentCancelTests(TestCase):
    """Test payment cancellation"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            user_type='tenant'
        )
        self.plan = SubscriptionPlan.objects.create(
            name='Basic',
            description='Basic plan',
            base_price=100.00,
        )
        self.subscription = Subscription.objects.create(
            user=self.user,
            plan=self.plan,
            duration=1,
            status='inactive'
        )
        self.payment = Payment.objects.create(
            user=self.user,
            subscription=self.subscription,
            amount=100.00,
            currency='GHS',
            status='pending',
            paystack_reference=f"GH-{uuid.uuid4().hex[:12].upper()}"
        )
        self.client.login(username='testuser', password='testpass123')
    
    def test_payment_cancel_marks_pending_as_cancelled(self):
        """Test that payment_cancel marks pending payments as cancelled"""
        response = self.client.get(reverse('payments:cancel'))
        
        self.assertEqual(response.status_code, 200)
        self.payment.refresh_from_db()
        self.assertEqual(self.payment.status, 'cancelled')
    
    def test_payment_cancel_shows_retry_subscription(self):
        """Test that payment_cancel shows retry subscription in context"""
        response = self.client.get(reverse('payments:cancel'))
        
        self.assertEqual(response.status_code, 200)
        self.assertIn('retry_subscription', response.context)
        self.assertEqual(response.context['retry_subscription'], self.subscription)


class PaymentVerificationTests(TestCase):
    """Test payment verification"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            user_type='tenant'
        )
        self.plan = SubscriptionPlan.objects.create(
            name='Basic',
            description='Basic plan',
            base_price=100.00,
        )
        self.subscription = Subscription.objects.create(
            user=self.user,
            plan=self.plan,
            duration=1,
            status='inactive'
        )
        self.payment = Payment.objects.create(
            user=self.user,
            subscription=self.subscription,
            amount=100.00,
            currency='GHS',
            status='pending',
            paystack_reference=f"GH-{uuid.uuid4().hex[:12].upper()}"
        )
        self.client.login(username='testuser', password='testpass123')
    
    def test_verify_payment_requires_login(self):
        """Test that verify_payment requires login"""
        self.client.logout()
        response = self.client.get(
            reverse('payments:verify') + f"?reference={self.payment.paystack_reference}"
        )
        self.assertEqual(response.status_code, 302)  # Redirect to login
    
    def test_verify_payment_requires_reference(self):
        """Test that verify_payment requires reference parameter"""
        response = self.client.get(reverse('payments:verify'))
        self.assertEqual(response.status_code, 302)  # Redirect with error
    
    @patch('payments.views.get_paystack_instance')
    def test_verify_payment_successful(self, mock_paystack):
        """Test successful payment verification"""
        mock_response = {
            'status': True,
            'data': {
                'status': 'success',
                'channel': 'card'
            }
        }
        mock_paystack.return_value.transactions.verify.return_value = mock_response
        
        response = self.client.get(
            reverse('payments:verify') + f"?reference={self.payment.paystack_reference}"
        )
        
        self.payment.refresh_from_db()
        self.assertEqual(self.payment.status, 'completed')
        
        self.subscription.refresh_from_db()
        self.assertEqual(self.subscription.status, 'active')


class PaymentUtilsTests(TestCase):
    """Test payment utility functions"""
    
    def test_format_amount_for_paystack(self):
        """Test formatting amount for Paystack (in pesewas)"""
        # 100 GHS = 10000 pesewas
        result = format_amount_for_paystack(100.00)
        self.assertEqual(result, 10000)
        
        # 50.50 GHS = 5050 pesewas
        result = format_amount_for_paystack(50.50)
        self.assertEqual(result, 5050)
    
    def test_verify_webhook_signature_valid(self):
        """Test webhook signature verification with valid signature"""
        # This would require mocking the actual HMAC verification
        # Placeholder for signature verification test
        pass
    
    def test_verify_webhook_signature_invalid(self):
        """Test webhook signature verification with invalid signature"""
        # This would require mocking the actual HMAC verification
        # Placeholder for signature verification test
        pass


class PaymentWebhookTests(TestCase):
    """Test Paystack webhook handling"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            user_type='tenant'
        )
        self.plan = SubscriptionPlan.objects.create(
            name='Basic',
            description='Basic plan',
            base_price=100.00,
        )
        self.subscription = Subscription.objects.create(
            user=self.user,
            plan=self.plan,
            duration=1,
            status='inactive'
        )
        self.payment = Payment.objects.create(
            user=self.user,
            subscription=self.subscription,
            amount=100.00,
            currency='GHS',
            status='pending',
            paystack_reference=f"GH-{uuid.uuid4().hex[:12].upper()}"
        )
    
    def test_webhook_rejects_get_request(self):
        """Test that webhook rejects GET requests"""
        response = self.client.get(reverse('payments:webhook'))
        self.assertEqual(response.status_code, 405)  # Method Not Allowed
    
    @patch('payments.views.verify_webhook_signature')
    def test_webhook_rejects_invalid_signature(self, mock_verify):
        """Test that webhook rejects invalid signatures"""
        mock_verify.return_value = False
        
        payload = json.dumps({'event': 'charge.success'})
        response = self.client.post(
            reverse('payments:webhook'),
            data=payload,
            content_type='application/json',
            HTTP_X_PAYSTACK_SIGNATURE='invalid_signature'
        )
        
        self.assertEqual(response.status_code, 401)  # Unauthorized
    
    @patch('payments.views.verify_webhook_signature')
    def test_webhook_charge_success_event(self, mock_verify):
        """Test webhook handling charge.success event"""
        mock_verify.return_value = True
        
        payload = json.dumps({
            'event': 'charge.success',
            'data': {
                'reference': self.payment.paystack_reference,
                'amount': 10000,  # in pesewas
                'channel': 'card'
            }
        })
        
        response = self.client.post(
            reverse('payments:webhook'),
            data=payload,
            content_type='application/json',
            HTTP_X_PAYSTACK_SIGNATURE='valid_signature'
        )
        
        self.assertEqual(response.status_code, 200)
        
        self.payment.refresh_from_db()
        self.assertEqual(self.payment.status, 'completed')
        
        self.subscription.refresh_from_db()
        self.assertEqual(self.subscription.status, 'active')
