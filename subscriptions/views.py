from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from datetime import timedelta
from .models import SubscriptionPlan, Subscription
from .forms import SubscriptionForm

def subscription_plans(request):
    """Display all subscription plans"""
    plans = SubscriptionPlan.objects.filter(is_active=True).order_by('price_monthly')
    
    # Get user's current subscription if logged in
    current_subscription = None
    if request.user.is_authenticated and request.user.is_landlord():
        try:
            current_subscription = Subscription.objects.get(user=request.user)
        except Subscription.DoesNotExist:
            pass
    
    context = {
        'plans': plans,
        'current_subscription': current_subscription,
    }
    
    return render(request, 'subscriptions/plans.html', context)


@login_required
def subscribe(request, plan_type):
    """Subscribe to a plan or upgrade existing subscription"""
    if not request.user.is_landlord():
        messages.error(request, 'Only landlords/agents can subscribe.')
        return redirect('properties:home')
    
    plan = get_object_or_404(SubscriptionPlan, plan_type=plan_type, is_active=True)
    
    # Check if user already has an active subscription
    existing_subscription = None
    try:
        existing_subscription = Subscription.objects.get(user=request.user)
        if existing_subscription.is_active() and existing_subscription.plan_id == plan.id:
            messages.info(request, 'You are already subscribed to this plan.')
            return redirect('subscriptions:my_subscription')
    except Subscription.DoesNotExist:
        pass
    
    if request.method == 'POST':
        form = SubscriptionForm(request.POST)
        if form.is_valid():
            duration = form.cleaned_data['duration']
            auto_renew = form.cleaned_data['auto_renew']
            
            # For free plans, force monthly duration only (30 days)
            if plan.is_free:
                duration = 'monthly'
                auto_renew = False
                messages.info(request, 'Free plan is limited to 30 days. Consider upgrading for unlimited access.')
            
            # Calculate end date based on duration
            duration_days = {
                'monthly': 30,
                'quarterly': 90,
                'yearly': 365,
            }
            
            days = duration_days.get(duration, 30)
            end_date = timezone.now() + timedelta(days=days)
            
            # If upgrading, update existing subscription. Otherwise create new
            if existing_subscription:
                subscription = existing_subscription
                subscription.plan = plan
                subscription.duration = duration
                subscription.end_date = end_date
                subscription.auto_renew = auto_renew
                subscription.status = 'active' if plan.is_free else 'pending'
                messages.info(request, f'Upgrading to {plan.name} plan...')
            else:
                subscription = Subscription(
                    user=request.user,
                    plan=plan,
                    duration=duration,
                    end_date=end_date,
                    auto_renew=auto_renew,
                    status='active' if plan.is_free else 'pending',
                )
            
            subscription.save()
            
            # For free plans, activate immediately. For paid plans, redirect to payment
            if plan.is_free:
                messages.success(request, f'Welcome to {plan.name} plan! You have 30 days of free access.')
                return redirect('subscriptions:my_subscription')
            else:
                # Redirect to payment
                return redirect('payments:initialize', subscription_id=subscription.id)
    else:
        form = SubscriptionForm(initial={'plan_type': plan_type})
    
    context = {
        'plan': plan,
        'form': form,
        'existing_subscription': existing_subscription,
    }
    
    return render(request, 'subscriptions/subscribe.html', context)


@login_required
def my_subscription(request):
    """View current subscription details"""
    if not request.user.is_landlord():
        messages.error(request, 'Access denied.')
        return redirect('properties:home')
    
    try:
        subscription = Subscription.objects.get(user=request.user)
    except Subscription.DoesNotExist:
        messages.info(request, 'You do not have an active subscription.')
        return redirect('subscriptions:plans')
    
    # Check if expired
    if subscription.end_date < timezone.now():
        subscription.status = 'expired'
        subscription.save()
    
    # Check if property limit exhausted
    properties_remaining = subscription.plan.property_limit - subscription.property_count
    is_limit_exhausted = properties_remaining <= 0
    
    # Check if near limit (80% used)
    is_near_limit = (subscription.property_count / subscription.plan.property_limit) >= 0.8 if subscription.plan.property_limit > 0 else False
    
    # Calculate property usage percentage
    property_usage_percentage = 0
    if subscription.plan.property_limit > 0:
        property_usage_percentage = (subscription.property_count / subscription.plan.property_limit) * 100
        property_usage_percentage = min(100, property_usage_percentage)  # Cap at 100%
    
    context = {
        'subscription': subscription,
        'properties_remaining': properties_remaining,
        'is_limit_exhausted': is_limit_exhausted,
        'is_near_limit': is_near_limit,
        'property_usage_percentage': property_usage_percentage,
    }
    
    return render(request, 'subscriptions/my_subscription.html', context)


@login_required
def cancel_subscription(request):
    """Cancel subscription"""
    try:
        subscription = Subscription.objects.get(user=request.user)
        
        # Require POST for security, but allow GET with confirmation
        if request.method == 'POST' or request.GET.get('confirm') == 'yes':
            subscription.status = 'cancelled'
            subscription.auto_renew = False
            subscription.save()
            
            messages.success(request, 'Subscription cancelled successfully. You can still view your properties and consider upgrading or using our free plan.')
            return redirect('subscriptions:plans')
        
        # Show confirmation page on GET
        return render(request, 'subscriptions/cancel_confirmation.html', {'subscription': subscription})
    
    except Subscription.DoesNotExist:
        messages.error(request, 'No active subscription found.')
        return redirect('subscriptions:plans')


@login_required
def renew_subscription(request):
    """Renew or upgrade subscription"""
    if not request.user.is_landlord():
        messages.error(request, 'Only landlords can renew subscriptions.')
        return redirect('properties:home')
    
    try:
        subscription = Subscription.objects.get(user=request.user)
        
        # Check if renewal is allowed
        now = timezone.now()
        days_until_expiry = (subscription.end_date - now).days
        
        # Allow renewal if: expired, exhausted, or within 7 days of expiration
        can_renew = (
            subscription.status == 'expired' or
            days_until_expiry <= 7 or
            (subscription.property_count >= subscription.plan.property_limit and subscription.status == 'active')
        )
        
        if not can_renew and subscription.status == 'active':
            messages.info(request, 'Your subscription is still active. You can renew it 7 days before expiration or if you reach your property limit.')
            return redirect('subscriptions:my_subscription')
        
        # Get available plans for renewal/upgrade (same tier or better)
        available_plans = SubscriptionPlan.objects.filter(is_active=True)
        
        # For free plans, only allow upgrade to paid plans
        if subscription.plan.is_free:
            available_plans = available_plans.exclude(is_free=True)
            messages.info(request, 'Your free trial has ended. Choose a paid plan to continue posting.')
        else:
            # For paid plans, allow renewal of same plan or upgrade
            available_plans = available_plans.filter(price_monthly__gte=subscription.plan.price_monthly)
        
        if request.method == 'POST':
            form = SubscriptionForm(request.POST)
            if form.is_valid():
                new_plan_type = request.POST.get('plan_type')
                new_plan = get_object_or_404(SubscriptionPlan, plan_type=new_plan_type, is_active=True)
                duration = form.cleaned_data['duration']
                auto_renew = form.cleaned_data['auto_renew']
                
                # Update subscription
                subscription.plan = new_plan
                subscription.duration = duration
                subscription.auto_renew = auto_renew
                subscription.status = 'pending' if not new_plan.is_free else 'active'
                
                # Calculate new end date (extend from now, not from old end date)
                duration_days = {'monthly': 30, 'quarterly': 90, 'yearly': 365}
                days = duration_days.get(duration, 30)
                subscription.end_date = now + timedelta(days=days)
                
                subscription.save()
                
                if new_plan.is_free:
                    messages.success(request, f'Renewed on {new_plan.name} plan for 30 days!')
                    return redirect('subscriptions:my_subscription')
                else:
                    messages.info(request, f'Proceeding to payment for {new_plan.name} renewal...')
                    return redirect('payments:initialize', subscription_id=subscription.id)
        else:
            form = SubscriptionForm()
        
        context = {
            'subscription': subscription,
            'available_plans': available_plans,
            'form': form,
            'days_until_expiry': max(0, days_until_expiry),
        }
        
        return render(request, 'subscriptions/renew.html', context)
        
    except Subscription.DoesNotExist:
        messages.error(request, 'No subscription found.')
        return redirect('subscriptions:plans')
