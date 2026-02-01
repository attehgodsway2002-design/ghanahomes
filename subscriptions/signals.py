from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
from django.urls import reverse
from .models import Subscription, SubscriptionPlan

User = get_user_model()


@receiver(post_save, sender=User)
def create_free_subscription(sender, instance, created, **kwargs):
    """
    Automatically create a free subscription when a new user registers.
    This allows users to explore the platform without paying.
    """
    if created and not hasattr(instance, '_skip_subscription'):
        try:
            free_plan = SubscriptionPlan.objects.get(plan_type='free', is_free=True)
            
            # Only create if user doesn't already have a subscription
            if not hasattr(instance, 'subscription'):
                Subscription.objects.get_or_create(
                    user=instance,
                    defaults={
                        'plan': free_plan,
                        'duration': 'monthly',
                        'start_date': timezone.now(),
                        'end_date': timezone.now() + timedelta(days=365),  # Free for 1 year
                        'status': 'active',
                        'auto_renew': True,
                    }
                )
        except SubscriptionPlan.DoesNotExist:
            # Free plan doesn't exist yet, skip
            pass
        except Exception as e:
            # Log but don't fail user creation
            print(f"Error creating free subscription: {e}")


@receiver(post_save, sender=Subscription)
def send_subscription_activated_email(sender, instance, created, **kwargs):
    """Send email when subscription is activated/renewed."""
    if not created:  # Only on changes, not creation
        return
    
    try:
        from accounts.email_utils import send_account_activated
        user = instance.user
        
        # Generate URLs
        dashboard_url = reverse('subscriptions:my_subscription')
        browse_url = reverse('properties:home')
        
        send_account_activated(user, dashboard_url, browse_url)
    except Exception as e:
        print(f"Error sending subscription activated email: {e}")


def check_subscription_expiring_soon(days_ahead=7):
    """Check for subscriptions expiring soon and send reminders."""
    try:
        from accounts.email_utils import send_subscription_renewal_reminder
        from django.conf import settings
        
        # Find subscriptions expiring in the specified number of days
        target_date = timezone.now().date() + timedelta(days=days_ahead)
        
        expiring_subscriptions = Subscription.objects.filter(
            end_date__date=target_date,
            status='active',
        )
        
        for subscription in expiring_subscriptions:
            user = subscription.user
            
            # Calculate days remaining
            days_remaining = (subscription.end_date.date() - timezone.now().date()).days
            
            # Generate renewal URL
            renewal_url = reverse('subscriptions:plans')
            
            send_subscription_renewal_reminder(
                user,
                subscription,
                days_remaining,
                renewal_url,
            )
    except Exception as e:
        print(f"Error checking subscriptions expiring soon: {e}")


def check_subscription_expired():
    """Check for expired subscriptions and send alerts."""
    try:
        from accounts.email_utils import send_subscription_expired
        
        # Find subscriptions that just expired
        expired_subscriptions = Subscription.objects.filter(
            end_date__lt=timezone.now(),
            status='active',
        )
        
        for subscription in expired_subscriptions:
            user = subscription.user
            
            # Mark as expired
            subscription.status = 'expired'
            subscription.save()
            
            # Generate renew URL
            renew_url = reverse('subscriptions:plans')
            
            send_subscription_expired(user, subscription, renew_url)
    except Exception as e:
        print(f"Error checking expired subscriptions: {e}")


@receiver(pre_delete, sender=Subscription)
def send_subscription_cancelled_email(sender, instance, **kwargs):
    """Send email when subscription is cancelled."""
    try:
        from accounts.email_utils import send_subscription_cancelled
        
        user = instance.user
        cancellation_date = timezone.now()
        plans_url = reverse('subscriptions:plans')
        
        send_subscription_cancelled(
            user,
            instance,
            cancellation_date,
            plans_url,
        )
    except Exception as e:
        print(f"Error sending subscription cancelled email: {e}")
