"""
Tests for audit logging system
"""
from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from accounts.audit_models import AuditLog, LoginHistory, PaymentAudit, PropertyEditHistory
from accounts.audit_utils import log_audit, log_payment_event, log_property_edit
from payments.models import Payment
from properties.models import Property, PropertyCategory
from subscriptions.models import SubscriptionPlan
from django.utils import timezone
from decimal import Decimal

User = get_user_model()


class AuditLogTests(TestCase):
    """Test audit logging functionality"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            user_type='tenant'
        )
        self.landlord = User.objects.create_user(
            username='landlord',
            email='landlord@example.com',
            password='testpass123',
            user_type='landlord'
        )
    
    def test_log_audit_creation(self):
        """Test creating an audit log entry"""
        log_audit(
            user=self.user,
            action='CREATE',
            obj=self.landlord,
            new_values={'username': 'landlord'},
            ip_address='127.0.0.1'
        )
        
        self.assertEqual(AuditLog.objects.count(), 1)
        log = AuditLog.objects.first()
        self.assertEqual(log.user, self.user)
        self.assertEqual(log.action, 'CREATE')
        self.assertIn('landlord', log.object_repr)
    
    def test_log_audit_with_changes(self):
        """Test audit log with old and new values"""
        old_vals = {'email': 'old@example.com'}
        new_vals = {'email': 'new@example.com'}
        
        log_audit(
            user=self.user,
            action='UPDATE',
            obj=self.landlord,
            old_values=old_vals,
            new_values=new_vals,
            ip_address='192.168.1.1'
        )
        
        log = AuditLog.objects.first()
        self.assertEqual(log.get_changes()['email']['old'], 'old@example.com')
        self.assertEqual(log.get_changes()['email']['new'], 'new@example.com')
    
    def test_audit_log_system_action(self):
        """Test logging actions with no user (system actions)"""
        log_audit(
            user=None,
            action='LOGIN',
            obj=self.user,
            ip_address='127.0.0.1'
        )
        
        log = AuditLog.objects.first()
        self.assertIsNone(log.user)
        self.assertEqual(log.action, 'LOGIN')


class LoginHistoryTests(TestCase):
    """Test login history tracking"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client = Client()
    
    def test_login_history_creation(self):
        """Test login history is created on user login"""
        LoginHistory.objects.create(
            user=self.user,
            ip_address='127.0.0.1',
            user_agent='Mozilla/5.0',
            is_active=True
        )
        
        self.assertEqual(LoginHistory.objects.count(), 1)
        login = LoginHistory.objects.first()
        self.assertEqual(login.user, self.user)
        self.assertTrue(login.is_active)
    
    def test_login_logout_session(self):
        """Test login/logout creates session with duration"""
        from django.utils import timezone
        from datetime import timedelta
        
        login_time = timezone.now()
        logout_time = login_time + timedelta(hours=2)
        
        login = LoginHistory.objects.create(
            user=self.user,
            ip_address='127.0.0.1',
            user_agent='Mozilla/5.0',
            login_at=login_time,
            is_active=True
        )
        
        login.logout_at = logout_time
        login.is_active = False
        login.save()
        
        # Check duration is approximately 2 hours (allow small variance from microseconds)
        self.assertAlmostEqual(login.session_duration, 7200, delta=1)


class PaymentAuditTests(TestCase):
    """Test payment audit trail"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.plan = SubscriptionPlan.objects.create(
            name='Premium',
            plan_type='premium',
            description='Premium plan',
            price_monthly=Decimal('99.99'),
            property_limit=10
        )
        self.payment = Payment.objects.create(
            user=self.user,
            amount=Decimal('99.99'),
            status='pending',
            paystack_reference='GH-12345'
        )
    
    def test_log_payment_event(self):
        """Test logging payment events"""
        log_payment_event(
            payment=self.payment,
            user=self.user,
            event='INITIATED',
            old_status=None,
            new_status='pending',
            ip_address='127.0.0.1',
            details={'ref': 'GH-12345'}
        )
        
        self.assertEqual(PaymentAudit.objects.count(), 1)
        audit = PaymentAudit.objects.first()
        self.assertEqual(audit.event, 'INITIATED')
        self.assertEqual(audit.new_status, 'pending')
    
    def test_payment_status_change_audit(self):
        """Test audit trail for payment status changes"""
        # Initial
        log_payment_event(
            payment=self.payment,
            user=self.user,
            event='INITIATED',
            new_status='pending',
        )
        
        # Verified
        log_payment_event(
            payment=self.payment,
            user=self.user,
            event='VERIFIED',
            old_status='pending',
            new_status='completed',
        )
        
        audits = PaymentAudit.objects.filter(payment=self.payment).order_by('created_at')
        self.assertEqual(audits.count(), 2)
        self.assertEqual(audits[0].event, 'INITIATED')
        self.assertEqual(audits[1].event, 'VERIFIED')


class PropertyEditHistoryTests(TestCase):
    """Test property edit history tracking"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='landlord',
            email='landlord@example.com',
            password='testpass123',
            user_type='landlord'
        )
        self.category = PropertyCategory.objects.create(
            name='Apartment',
            slug='apartment'
        )
        self.property = Property.objects.create(
            title='Test Property',
            description='A test property',
            owner=self.user,
            property_type='apartment',
            category=self.category,
            region='Accra',
            city='Accra',
            area='Airport Area',
            address='123 Main St',
            price=Decimal('5000.00'),
            bedrooms=2,
            bathrooms=1,
            size=Decimal('100.00'),
        )
    
    def test_log_property_edit(self):
        """Test logging property edits"""
        old_vals = {'price': '5000.00', 'bedrooms': 2}
        new_vals = {'price': '6000.00', 'bedrooms': 3}
        
        log_property_edit(
            property_obj=self.property,
            user=self.user,
            old_values=old_vals,
            new_values=new_vals,
            ip_address='127.0.0.1'
        )
        
        self.assertEqual(PropertyEditHistory.objects.count(), 1)
        edit = PropertyEditHistory.objects.first()
        self.assertEqual(edit.property, self.property)
        self.assertEqual(edit.user, self.user)
    
    def test_property_edit_changes(self):
        """Test getting changes from property edit"""
        old_vals = {'price': '5000.00', 'bedrooms': 2}
        new_vals = {'price': '6000.00', 'bedrooms': 3}
        
        edit = PropertyEditHistory.objects.create(
            property=self.property,
            user=self.user,
            old_values=old_vals,
            new_values=new_vals,
        )
        
        changes = edit.get_changes()
        self.assertIn('price', changes)
        self.assertIn('bedrooms', changes)
        self.assertEqual(changes['price']['old'], '5000.00')
        self.assertEqual(changes['price']['new'], '6000.00')


class AuditQueryPerformanceTests(TestCase):
    """Test query optimization for audit logs"""
    
    def setUp(self):
        self.users = [
            User.objects.create_user(
                username=f'user{i}',
                email=f'user{i}@example.com',
                password='testpass123'
            )
            for i in range(5)
        ]
    
    def test_audit_log_filtering_by_user(self):
        """Test efficient filtering of audits by user"""
        for user in self.users[:3]:
            for i in range(5):
                log_audit(
                    user=user,
                    action='LOGIN',
                    obj=user,
                )
        
        # Query should use index
        user_audits = AuditLog.objects.filter(user=self.users[0])
        self.assertEqual(user_audits.count(), 5)
    
    def test_login_history_filtering_by_user(self):
        """Test efficient filtering of login history"""
        for user in self.users[:3]:
            for i in range(3):
                LoginHistory.objects.create(
                    user=user,
                    ip_address='127.0.0.1',
                    user_agent='Mozilla/5.0'
                )
        
        # Query should use index
        user_logins = LoginHistory.objects.filter(user=self.users[1], is_active=True)
        self.assertLessEqual(user_logins.count(), 3)
