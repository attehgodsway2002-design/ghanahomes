"""
Audit logging utilities for tracking changes automatically
"""
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.contrib.contenttypes.models import ContentType
from .audit_models import AuditLog, PaymentAudit, PropertyEditHistory
import json
from django.utils import timezone


def log_audit(user, action, obj, old_values=None, new_values=None, ip_address=None, user_agent=None):
    """
    Log an audit event
    
    Args:
        user: User performing the action
        action: Action type (from AuditLog.ACTION_CHOICES)
        obj: Object being modified (or None for login/logout)
        old_values: Dict of previous values
        new_values: Dict of new values
        ip_address: IP address of request
        user_agent: User agent string
    """
    try:
        content_type = None
        object_id = None
        object_repr = str(obj) if obj else action
        
        if obj:
            content_type = ContentType.objects.get_for_model(obj)
            object_id = str(obj.pk)
        
        AuditLog.objects.create(
            user=user,
            action=action,
            content_type=content_type,
            object_id=object_id,
            object_repr=object_repr,
            old_values=old_values or {},
            new_values=new_values or {},
            ip_address=ip_address,
            user_agent=user_agent,
        )
    except Exception as e:
        # Don't let audit logging break the application
        print(f"Error logging audit: {e}")


def log_payment_event(payment, user, event, old_status=None, new_status=None, ip_address=None, details=None):
    """
    Log a payment-specific event
    
    Args:
        payment: Payment object
        user: User performing action (can be None)
        event: Event type (from PaymentAudit.EVENT_CHOICES)
        old_status: Previous payment status
        new_status: New payment status
        ip_address: IP address
        details: Additional JSON details
    """
    try:
        import datetime
        now = timezone.now()
        # Ensure monotonically increasing timestamps for audits on the same payment
        latest = PaymentAudit.objects.filter(payment=payment).order_by('-created_at').first()
        if latest and now <= latest.created_at:
            now = latest.created_at + datetime.timedelta(microseconds=1)
        audit = PaymentAudit.objects.create(
            payment=payment,
            user=user,
            event=event,
            old_status=old_status,
            new_status=new_status,
            amount=payment.amount,
            reference_code=payment.paystack_reference,
            details=details or {},
            ip_address=ip_address,
            created_at=now,
        )
    except Exception as e:
        print(f"Error logging payment event: {e}")


def log_property_edit(property_obj, user, old_values, new_values, ip_address=None):
    """
    Log a property edit event
    
    Args:
        property_obj: Property object
        user: User who edited
        old_values: Dict of previous values
        new_values: Dict of new values
        ip_address: IP address
    """
    try:
        PropertyEditHistory.objects.create(
            property=property_obj,
            user=user,
            old_values=old_values,
            new_values=new_values,
            ip_address=ip_address,
        )
    except Exception as e:
        print(f"Error logging property edit: {e}")


def get_model_changes(instance, tracked_fields):
    """
    Get changes to tracked fields for an instance
    
    Args:
        instance: Model instance
        tracked_fields: List of field names to track
    
    Returns:
        Tuple of (old_values_dict, new_values_dict, has_changes_bool)
    """
    old_values = {}
    new_values = {}
    has_changes = False
    
    try:
        # Get current DB values
        if instance.pk:
            from django.db.models import Model
            db_instance = instance.__class__.objects.get(pk=instance.pk)
            
            for field in tracked_fields:
                old_val = getattr(db_instance, field, None)
                new_val = getattr(instance, field, None)
                
                # Convert to JSON-serializable format
                if hasattr(old_val, 'isoformat'):
                    old_values[field] = old_val.isoformat()
                else:
                    old_values[field] = str(old_val) if old_val is not None else None
                
                if hasattr(new_val, 'isoformat'):
                    new_values[field] = new_val.isoformat()
                else:
                    new_values[field] = str(new_val) if new_val is not None else None
                
                if old_values[field] != new_values[field]:
                    has_changes = True
        else:
            # New instance
            for field in tracked_fields:
                new_val = getattr(instance, field, None)
                if hasattr(new_val, 'isoformat'):
                    new_values[field] = new_val.isoformat()
                else:
                    new_values[field] = str(new_val) if new_val is not None else None
                has_changes = True
    except Exception as e:
        print(f"Error tracking changes: {e}")
    
    return old_values, new_values, has_changes


# Middleware helper to get request data
def extract_request_info(request):
    """Extract IP address and user agent from request"""
    ip_address = None
    user_agent = ""
    
    if request:
        # Get client IP (handle proxies)
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip_address = x_forwarded_for.split(',')[0].strip()
        else:
            ip_address = request.META.get('REMOTE_ADDR')
        
        user_agent = request.META.get('HTTP_USER_AGENT', '')
    
    return ip_address, user_agent
