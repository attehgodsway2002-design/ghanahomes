"""
Admin dashboard views for GhanaHomes
"""
from django.shortcuts import render
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Count, Sum, Q, F, DecimalField, Avg
from django.db.models.functions import TruncDate
from django.utils import timezone
from django.core.paginator import Paginator
from django.http import HttpResponse
from datetime import timedelta
import json
import csv

from accounts.models import User
from properties.models import Property
from subscriptions.models import Subscription, SubscriptionPlan
from payments.models import Payment
from chat.models import ChatRoom, Message


@staff_member_required
def admin_dashboard(request):
    """Main admin dashboard with key metrics and statistics."""
    
    # Date range
    today = timezone.now()
    week_ago = today - timedelta(days=7)
    month_ago = today - timedelta(days=30)
    
    # User Statistics
    total_users = User.objects.count()
    total_landlords = User.objects.filter(user_type='landlord').count()
    total_tenants = User.objects.filter(user_type='tenant').count()
    verified_users = User.objects.filter(is_verified=True).count()
    new_users_this_week = User.objects.filter(created_at__gte=week_ago).count()
    new_users_this_month = User.objects.filter(created_at__gte=month_ago).count()
    
    # Property Statistics
    total_properties = Property.objects.count()
    available_properties = Property.objects.filter(status='available').count()
    rented_properties = Property.objects.filter(status='rented').count()
    pending_properties = Property.objects.filter(status='pending').count()
    new_properties_this_week = Property.objects.filter(created_at__gte=week_ago).count()
    
    # Subscription Statistics
    active_subscriptions = Subscription.objects.filter(status='active').count()
    expired_subscriptions = Subscription.objects.filter(status='expired').count()
    free_subscriptions = Subscription.objects.filter(plan__is_free=True).count()
    paid_subscriptions = Subscription.objects.filter(plan__is_free=False, status='active').count()
    
    # Payment Statistics
    total_payments = Payment.objects.count()
    completed_payments = Payment.objects.filter(status='completed').count()
    failed_payments = Payment.objects.filter(status='failed').count()
    pending_payments = Payment.objects.filter(status='pending').count()
    
    # Revenue Statistics
    total_revenue = Payment.objects.filter(status='completed').aggregate(
        total=Sum('amount')
    )['total'] or 0
    revenue_this_month = Payment.objects.filter(
        status='completed',
        created_at__gte=month_ago
    ).aggregate(total=Sum('amount'))['total'] or 0
    revenue_this_week = Payment.objects.filter(
        status='completed',
        created_at__gte=week_ago
    ).aggregate(total=Sum('amount'))['total'] or 0
    
    # Chat Statistics
    total_chats = ChatRoom.objects.count()
    total_messages = Message.objects.count()
    active_chats = ChatRoom.objects.filter(
        messages__created_at__gte=week_ago
    ).distinct().count()
    
    # Recent Activity
    recent_users = User.objects.order_by('-created_at')[:5]
    recent_properties = Property.objects.order_by('-created_at')[:5]
    recent_payments = Payment.objects.order_by('-created_at')[:5]
    
    # Top performing subscription plans
    top_plans = SubscriptionPlan.objects.annotate(
        subscriber_count=Count('subscription')
    ).order_by('-subscriber_count')[:5]
    
    # User registration trend (last 7 days)
    user_trend_data = []
    for i in range(6, -1, -1):
        date = today - timedelta(days=i)
        count = User.objects.filter(
            created_at__date=date.date()
        ).count()
        user_trend_data.append({
            'date': date.strftime('%a'),
            'count': count
        })
    
    # Property listing trend (last 7 days)
    property_trend_data = []
    for i in range(6, -1, -1):
        date = today - timedelta(days=i)
        count = Property.objects.filter(
            created_at__date=date.date()
        ).count()
        property_trend_data.append({
            'date': date.strftime('%a'),
            'count': count
        })
    
    # Revenue trend (last 7 days)
    revenue_trend_data = []
    for i in range(6, -1, -1):
        date = today - timedelta(days=i)
        revenue = Payment.objects.filter(
            status='completed',
            created_at__date=date.date()
        ).aggregate(total=Sum('amount'))['total'] or 0
        revenue_trend_data.append({
            'date': date.strftime('%a'),
            'revenue': float(revenue)
        })
    
    # Payment status breakdown
    payment_status_breakdown = Payment.objects.values('status').annotate(
        count=Count('id')
    ).order_by('status')
    
    # User type breakdown
    user_type_breakdown = {
        'landlords': total_landlords,
        'tenants': total_tenants,
    }
    
    # Property status breakdown
    property_status_breakdown = {
        'available': available_properties,
        'rented': rented_properties,
        'pending': pending_properties,
    }
    
    context = {
        # User stats
        'total_users': total_users,
        'total_landlords': total_landlords,
        'total_tenants': total_tenants,
        'verified_users': verified_users,
        'new_users_this_week': new_users_this_week,
        'new_users_this_month': new_users_this_month,
        
        # Property stats
        'total_properties': total_properties,
        'available_properties': available_properties,
        'rented_properties': rented_properties,
        'pending_properties': pending_properties,
        'new_properties_this_week': new_properties_this_week,
        
        # Subscription stats
        'active_subscriptions': active_subscriptions,
        'expired_subscriptions': expired_subscriptions,
        'free_subscriptions': free_subscriptions,
        'paid_subscriptions': paid_subscriptions,
        
        # Payment stats
        'total_payments': total_payments,
        'completed_payments': completed_payments,
        'failed_payments': failed_payments,
        'pending_payments': pending_payments,
        
        # Revenue stats
        'total_revenue': total_revenue,
        'revenue_this_month': revenue_this_month,
        'revenue_this_week': revenue_this_week,
        
        # Chat stats
        'total_chats': total_chats,
        'total_messages': total_messages,
        'active_chats': active_chats,
        
        # Recent activity
        'recent_users': recent_users,
        'recent_properties': recent_properties,
        'recent_payments': recent_payments,
        'top_plans': top_plans,
        
        # Charts data
        'user_trend_json': json.dumps(user_trend_data),
        'property_trend_json': json.dumps(property_trend_data),
        'revenue_trend_json': json.dumps(revenue_trend_data),
        'payment_status_json': json.dumps(list(payment_status_breakdown)),
        'user_type_breakdown': user_type_breakdown,
        'property_status_breakdown': property_status_breakdown,
    }
    
    return render(request, 'admin/dashboard.html', context)


@staff_member_required
@staff_member_required
def admin_users(request):
    """Admin panel for managing users."""
    
    users_query = User.objects.all()
    
    # Filter by user type
    user_type = request.GET.get('user_type')
    if user_type:
        users_query = users_query.filter(user_type=user_type)
    
    # Filter by verification status
    verified = request.GET.get('verified')
    if verified:
        users_query = users_query.filter(is_verified=(verified == 'true'))
    
    # Search
    search = request.GET.get('q')
    if search:
        users_query = users_query.filter(
            Q(username__icontains=search) |
            Q(email__icontains=search) |
            Q(first_name__icontains=search) |
            Q(last_name__icontains=search)
        )
    
    users = users_query.order_by('-created_at')
    
    # Pagination
    paginator = Paginator(users, 50)
    page_number = request.GET.get('page', 1)
    users_page = paginator.get_page(page_number)
    
    context = {
        'users': users_page,
        'page_obj': users_page,
        'user_count': users_query.count(),
    }
    
    return render(request, 'admin/users.html', context)


@staff_member_required
def admin_properties(request):
    """Admin panel for managing properties."""
    
    properties_query = Property.objects.select_related('owner', 'category')
    
    # Filter by status
    status = request.GET.get('status')
    if status:
        properties_query = properties_query.filter(status=status)
    
    # Filter by property type
    prop_type = request.GET.get('property_type')
    if prop_type:
        properties_query = properties_query.filter(property_type=prop_type)
    
    # Search
    search = request.GET.get('q')
    if search:
        properties_query = properties_query.filter(
            Q(title__icontains=search) |
            Q(description__icontains=search) |
            Q(location__icontains=search)
        )
    
    properties = properties_query.order_by('-created_at')
    
    context = {
        'properties': properties,
        'property_count': properties_query.count(),
    }
    
    return render(request, 'admin/properties.html', context)


@staff_member_required
def admin_payments(request):
    """Admin panel for managing payments."""
    
    payments_query = Payment.objects.select_related('user', 'subscription')
    
    # Filter by status
    status = request.GET.get('status')
    if status:
        payments_query = payments_query.filter(status=status)
    
    # Search by reference or user
    search = request.GET.get('q')
    if search:
        payments_query = payments_query.filter(
            Q(paystack_reference__icontains=search) |
            Q(user__email__icontains=search) |
            Q(user__username__icontains=search)
        )
    
    payments = payments_query.order_by('-created_at')
    
    # Statistics
    total_amount = payments_query.filter(status='completed').aggregate(
        total=Sum('amount')
    )['total'] or 0
    
    context = {
        'payments': payments,
        'payment_count': payments_query.count(),
        'total_amount': total_amount,
    }
    
    return render(request, 'admin/payments.html', context)


@staff_member_required
def admin_subscriptions(request):
    """Admin panel for managing subscriptions."""
    
    subscriptions_query = Subscription.objects.select_related('user', 'plan')
    
    # Filter by status
    status = request.GET.get('status')
    if status:
        subscriptions_query = subscriptions_query.filter(status=status)
    
    # Filter by plan
    plan = request.GET.get('plan')
    if plan:
        subscriptions_query = subscriptions_query.filter(plan__id=plan)
    
    # Search
    search = request.GET.get('q')
    if search:
        subscriptions_query = subscriptions_query.filter(
            Q(user__email__icontains=search) |
            Q(user__username__icontains=search)
        )
    
    subscriptions = subscriptions_query.order_by('-created_at')
    plans = SubscriptionPlan.objects.all()
    
    context = {
        'subscriptions': subscriptions,
        'subscription_count': subscriptions_query.count(),
        'plans': plans,
    }
    
    return render(request, 'admin/subscriptions.html', context)


@staff_member_required
def admin_analytics(request):
    """Admin analytics and reporting dashboard."""
    
    today = timezone.now()
    month_ago = today - timedelta(days=30)
    year_ago = today - timedelta(days=365)
    
    # Monthly revenue
    monthly_revenue_data = []
    for i in range(11, -1, -1):
        month = today - timedelta(days=30*i)
        month_start = month.replace(day=1)
        if i == 0:
            month_end = today
        else:
            month_end = (today - timedelta(days=30*(i-1))).replace(day=1) - timedelta(days=1)
        
        revenue = Payment.objects.filter(
            status='completed',
            created_at__date__gte=month_start.date(),
            created_at__date__lte=month_end.date()
        ).aggregate(total=Sum('amount'))['total'] or 0
        
        monthly_revenue_data.append({
            'month': month.strftime('%b'),
            'revenue': float(revenue)
        })
    
    # User growth
    user_growth_data = []
    for i in range(11, -1, -1):
        month = today - timedelta(days=30*i)
        count = User.objects.filter(created_at__year=month.year, created_at__month=month.month).count()
        user_growth_data.append({
            'month': month.strftime('%b'),
            'count': count
        })
    
    # Subscription breakdown
    subscription_breakdown = Subscription.objects.filter(status='active').values('plan_id', 'plan__name').annotate(
        count=Count('id'),
        total_revenue=Sum(F('plan__price_monthly'), output_field=DecimalField()),
        avg_revenue=Avg(F('plan__price_monthly'), output_field=DecimalField())
    ).order_by('-count')
    
    context = {
        'revenue_trend_json': json.dumps(monthly_revenue_data),
        'user_growth_json': json.dumps(user_growth_data),
        'subscription_breakdown': subscription_breakdown,
    }
    
    return render(request, 'admin/analytics.html', context)


# Export Functions
@staff_member_required
def export_users_csv(request):
    """Export all users to CSV."""
    users = User.objects.all().order_by('-created_at')
    
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="users.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['Username', 'Email', 'Full Name', 'User Type', 'Verified', 'Joined', 'Last Login'])
    
    for user in users:
        writer.writerow([
            user.username,
            user.email,
            user.get_full_name() or '-',
            user.get_user_type_display(),
            'Yes' if user.is_verified else 'No',
            user.created_at.strftime('%Y-%m-%d %H:%M'),
            user.last_login.strftime('%Y-%m-%d %H:%M') if user.last_login else '-',
        ])
    
    return response


@staff_member_required
def export_properties_csv(request):
    """Export all properties to CSV."""
    properties = Property.objects.all().order_by('-created_at').select_related('owner', 'category')
    
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="properties.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['Title', 'Owner', 'Type', 'Status', 'Price (GHS)', 'Location', 'Bedrooms', 'Bathrooms', 'Posted', 'Updated'])
    
    for prop in properties:
        writer.writerow([
            prop.title,
            prop.owner.email,
            prop.get_property_type_display(),
            prop.get_status_display(),
            prop.price,
            f"{prop.city}, {prop.region}",
            prop.bedrooms,
            prop.bathrooms,
            prop.created_at.strftime('%Y-%m-%d'),
            prop.updated_at.strftime('%Y-%m-%d'),
        ])
    
    return response


@staff_member_required
def export_payments_csv(request):
    """Export all payments to CSV."""
    payments = Payment.objects.all().order_by('-created_at').select_related('user', 'subscription')
    
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="payments.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['Reference', 'User Email', 'Amount (GHS)', 'Status', 'Plan', 'Date', 'Method'])
    
    for payment in payments:
        writer.writerow([
            payment.paystack_reference,
            payment.user.email,
            payment.amount,
            payment.get_status_display(),
            payment.subscription.plan.name if payment.subscription else '-',
            payment.created_at.strftime('%Y-%m-%d %H:%M'),
            payment.payment_method if hasattr(payment, 'payment_method') else '-',
        ])
    
    return response


@staff_member_required
def export_subscriptions_csv(request):
    """Export all subscriptions to CSV."""
    subscriptions = Subscription.objects.all().order_by('-created_at').select_related('user', 'plan')
    
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="subscriptions.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['User Email', 'Plan', 'Status', 'Start Date', 'End Date', 'Duration', 'Price (GHS)'])
    
    for sub in subscriptions:
        writer.writerow([
            sub.user.email,
            sub.plan.name,
            sub.get_status_display(),
            sub.start_date.strftime('%Y-%m-%d'),
            sub.end_date.strftime('%Y-%m-%d'),
            sub.get_duration_display(),
            sub.plan.price_monthly,
        ])
    
    return response

