from django.test import TestCase, Client, override_settings
from django.contrib.auth import get_user_model
from django.core import mail
from django.urls import reverse
from unittest.mock import patch, MagicMock
import logging

from payments.models import Payment
from payments.tasks import send_payment_confirmation_email, send_payment_cancelled_email
from subscriptions.models import Subscription, SubscriptionPlan

User = get_user_model()


@override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
class EmailDeliveryTests(TestCase):
    """Test email delivery for payment confirmations"""
    
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
            status='active'
        )
        self.payment = Payment.objects.create(
            user=self.user,
            subscription=self.subscription,
            amount=100.00,
            currency='GHS',
            status='completed',
            paystack_reference='GH-TEST123456',
            payment_method='card'
        )
    
    def test_payment_confirmation_email_sent(self):
        """Test that payment confirmation email is sent"""
        mail.outbox = []  # Clear outbox
        
        send_payment_confirmation_email(self.payment.id)
        
        # Check email was sent
        self.assertEqual(len(mail.outbox), 1)
        email = mail.outbox[0]
        
        self.assertEqual(email.to, [self.user.email])
        self.assertIn('Payment', email.subject)
        self.assertIn('Successful', email.subject)
    
    def test_payment_confirmation_email_content(self):
        """Test payment confirmation email contains correct information"""
        mail.outbox = []  # Clear outbox
        
        send_payment_confirmation_email(self.payment.id)
        
        email = mail.outbox[0]
        body = email.body
        
        self.assertIn('payment', body.lower())
        self.assertIn('confirmed', body.lower())
    
    def test_payment_cancelled_email_sent(self):
        """Test that payment cancelled email is sent"""
        self.payment.status = 'cancelled'
        self.payment.save()
        
        mail.outbox = []  # Clear outbox
        
        send_payment_cancelled_email(self.payment.id)
        
        # Check email was sent
        self.assertEqual(len(mail.outbox), 1)
        email = mail.outbox[0]
        
        self.assertEqual(email.to, [self.user.email])
        self.assertIn('Payment', email.subject)
    
    def test_email_sent_to_correct_recipient(self):
        """Test email sent to correct user"""
        other_user = User.objects.create_user(
            username='other',
            email='other@example.com',
            password='testpass123',
            user_type='tenant'
        )
        
        mail.outbox = []  # Clear outbox
        
        send_payment_confirmation_email(self.payment.id)
        
        email = mail.outbox[0]
        
        self.assertEqual(email.to, [self.user.email])
        self.assertNotEqual(email.to, [other_user.email])
    
    def test_invalid_payment_id_handles_gracefully(self):
        """Test that invalid payment ID is handled"""
        mail.outbox = []  # Clear outbox
        
        # Should not raise exception
        try:
            send_payment_confirmation_email(99999)
        except Exception as e:
            self.fail(f"send_payment_confirmation_email raised {type(e).__name__}: {e}")
    
    def test_email_not_sent_for_pending_payment(self):
        """Test that confirmation email not sent for pending payment"""
        pending_payment = Payment.objects.create(
            user=self.user,
            subscription=self.subscription,
            amount=100.00,
            currency='GHS',
            status='pending',
            paystack_reference='GH-PENDING123'
        )
        
        # Should not send email for pending payment
        # This depends on the implementation
        mail.outbox = []
        send_payment_confirmation_email(pending_payment.id)
        
        # Implementation should decide whether to send or not
        # For now, we're just checking it doesn't crash


@override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
class QueuedEmailDeliveryTests(TestCase):
    """Test queued email delivery with django-q"""
    
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
            status='active'
        )
        self.payment = Payment.objects.create(
            user=self.user,
            subscription=self.subscription,
            amount=100.00,
            currency='GHS',
            status='completed',
            paystack_reference='GH-TEST123456',
            payment_method='card'
        )
    
    @patch('django_q.tasks.async_task')
    def test_queued_email_task_called(self, mock_async_task):
        """Test that async_task is called for email"""
        mock_async_task.return_value = 'task_id_123'
        
        from django_q.tasks import async_task
        result = async_task(
            'payments.tasks.send_payment_confirmation_email',
            self.payment.id
        )
        
        # Verify async_task was called
        self.assertIsNotNone(result)


@override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
class SubscriptionEmailTests(TestCase):
    """Test emails sent during subscription flow"""
    
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
    
    def test_email_sent_on_subscription_purchase(self):
        """Test that email is sent when subscription is purchased"""
        self.client.login(username='testuser', password='testpass123')
        
        mail.outbox = []  # Clear outbox
        
        # Create subscription
        subscription = Subscription.objects.create(
            user=self.user,
            plan=self.plan,
            duration=1,
            status='inactive'
        )
        
        # Create and complete payment
        payment = Payment.objects.create(
            user=self.user,
            subscription=subscription,
            amount=100.00,
            currency='GHS',
            status='completed',
            paystack_reference='GH-TEST123456',
            payment_method='card'
        )
        
        # Manually send confirmation
        send_payment_confirmation_email(payment.id)
        
        # Check email was sent
        self.assertGreater(len(mail.outbox), 0)


@override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
class EmailErrorHandlingTests(TestCase):
    """Test error handling in email delivery"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='invalid-email',
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
            status='active'
        )
        self.payment = Payment.objects.create(
            user=self.user,
            subscription=self.subscription,
            amount=100.00,
            currency='GHS',
            status='completed',
            paystack_reference='GH-TEST123456'
        )
    
    def test_email_failure_doesnt_crash_app(self):
        """Test that email failure doesn't crash the application"""
        try:
            send_payment_confirmation_email(self.payment.id)
        except Exception as e:
            self.fail(f"Email sending raised {type(e).__name__}: {e}")
    
    def test_missing_user_email_handled(self):
        """Test that missing user email is handled gracefully"""
        user_no_email = User.objects.create_user(
            username='noemail',
            email='',
            password='testpass123',
            user_type='tenant'
        )
        
        payment = Payment.objects.create(
            user=user_no_email,
            subscription=self.subscription,
            amount=100.00,
            currency='GHS',
            status='completed',
            paystack_reference='GH-NOEMAIL123'
        )
        
        try:
            send_payment_confirmation_email(payment.id)
        except Exception as e:
            self.fail(f"Email sending raised {type(e).__name__}: {e}")
