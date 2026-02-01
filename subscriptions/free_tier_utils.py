"""
Free Tier Management Utilities
Handles free tier setup, upgrades, and downgrades
"""

from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
from subscriptions.models import Subscription, SubscriptionPlan

User = get_user_model()


def upgrade_free_user_to_plan(user, plan_type):
    """
    Upgrade a user from free tier to a paid plan.
    
    Args:
        user: User object
        plan_type: Plan type string ('basic', 'standard', 'premium', 'enterprise')
    
    Returns:
        tuple: (success: bool, message: str, subscription: Subscription or None)
    """
    try:
        plan = SubscriptionPlan.objects.get(plan_type=plan_type, is_active=True)
        subscription = user.subscription
        
        if subscription.plan.plan_type == plan_type:
            return False, f"User is already on the {plan.name} plan", None
        
        # Update subscription
        subscription.plan = plan
        subscription.status = 'pending'  # Pending payment
        subscription.save()
        
        return True, f"Upgraded to {plan.name}. Please complete payment.", subscription
        
    except SubscriptionPlan.DoesNotExist:
        return False, f"Plan '{plan_type}' not found", None
    except Exception as e:
        return False, f"Error upgrading plan: {str(e)}", None


def downgrade_to_free_tier(user):
    """
    Downgrade a user to free tier.
    
    Args:
        user: User object
    
    Returns:
        tuple: (success: bool, message: str, subscription: Subscription or None)
    """
    try:
        free_plan = SubscriptionPlan.objects.get(plan_type='free', is_free=True)
        subscription = user.subscription
        
        if subscription.plan.plan_type == 'free':
            return False, "User is already on the free tier", None
        
        # Update subscription
        subscription.plan = free_plan
        subscription.status = 'active'
        subscription.start_date = timezone.now()
        subscription.end_date = timezone.now() + timedelta(days=365)
        subscription.auto_renew = True
        subscription.save()
        
        return True, "Downgraded to free tier", subscription
        
    except SubscriptionPlan.DoesNotExist:
        return False, "Free plan not found", None
    except Exception as e:
        return False, f"Error downgrading: {str(e)}", None


def get_free_plan_stats():
    """Get statistics about free tier usage"""
    try:
        free_plan = SubscriptionPlan.objects.get(plan_type='free', is_free=True)
        free_users = Subscription.objects.filter(
            plan=free_plan,
            status='active'
        ).count()
        
        return {
            'plan': free_plan,
            'active_users': free_users,
            'property_limit': free_plan.property_limit,
            'photo_limit': free_plan.photo_limit,
        }
    except SubscriptionPlan.DoesNotExist:
        return None


def check_free_user_capacity(user):
    """
    Check if a free tier user has reached their limits.
    
    Args:
        user: User object
    
    Returns:
        dict: Capacity information
    """
    subscription = user.subscription
    
    if not subscription.plan.is_free:
        return {'is_free': False}
    
    from properties.models import Property
    
    user_properties = Property.objects.filter(landlord=user).count()
    
    return {
        'is_free': True,
        'property_count': user_properties,
        'property_limit': subscription.plan.property_limit,
        'can_add_property': user_properties < subscription.plan.property_limit,
        'properties_remaining': max(0, subscription.plan.property_limit - user_properties),
    }
