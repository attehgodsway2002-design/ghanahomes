from django.db.models.signals import post_save
from django.dispatch import receiver
from django.urls import reverse
from django.utils import timezone
from .models import Property


@receiver(post_save, sender=Property)
def send_property_listed_email(sender, instance, created, **kwargs):
    """Send email when property is first listed."""
    if not created:  # Only on creation
        return
    
    try:
        from accounts.email_utils import send_property_listed
        
        owner = instance.owner
        property_url = reverse('properties:property_detail', kwargs={'slug': instance.slug})
        posted_date = instance.created_at
        
        send_property_listed(owner, instance, posted_date, property_url)
    except Exception as e:
        print(f"Error sending property listed email: {e}")


def check_property_expiring_soon(days_ahead=7):
    """Check for properties expiring soon and send alerts."""
    try:
        from accounts.email_utils import send_property_expired
        from django.db.models import Q
        from datetime import timedelta
        
        # Find properties expiring in the specified number of days
        target_date = timezone.now().date() + timedelta(days=days_ahead)
        
        expiring_properties = Property.objects.filter(
            expiry_date__date=target_date,
            status__in=['available', 'pending'],
        )
        
        for prop in expiring_properties:
            owner = prop.owner
            renew_url = reverse('properties:property_detail', kwargs={'slug': prop.slug})
            
            send_property_expired(
                owner,
                prop,
                prop.expiry_date,
                renew_url,
            )
    except Exception as e:
        print(f"Error checking properties expiring soon: {e}")


def check_property_expired():
    """Check for expired properties and update status."""
    try:
        from django.db.models import Q
        
        # Find properties that have expired
        expired_properties = Property.objects.filter(
            expiry_date__lt=timezone.now(),
            status__in=['available', 'pending'],
        )
        
        # Mark them as unavailable
        expired_properties.update(status='unavailable')
    except Exception as e:
        print(f"Error checking expired properties: {e}")
