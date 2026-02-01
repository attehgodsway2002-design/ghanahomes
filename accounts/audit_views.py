"""
Admin views for audit logging dashboard
"""
from django.contrib.admin.views.decorators import staff_member_required
from django.http import JsonResponse
from django.shortcuts import render
from django.utils import timezone
from datetime import timedelta
from django.db.models import Count, Q
from .audit_models import AuditLog, LoginHistory, PaymentAudit, PropertyEditHistory


@staff_member_required
def audit_dashboard(request):
    """Dashboard view for audit logs"""
    now = timezone.now()
    last_24h = now - timedelta(hours=24)
    last_7d = now - timedelta(days=7)
    last_30d = now - timedelta(days=30)
    
    # Get statistics
    stats = {
        'total_audits': AuditLog.objects.count(),
        'audits_24h': AuditLog.objects.filter(timestamp__gte=last_24h).count(),
        'audits_7d': AuditLog.objects.filter(timestamp__gte=last_7d).count(),
        'audits_30d': AuditLog.objects.filter(timestamp__gte=last_30d).count(),
        
        'total_logins': LoginHistory.objects.count(),
        'active_sessions': LoginHistory.objects.filter(is_active=True).count(),
        'logins_24h': LoginHistory.objects.filter(login_at__gte=last_24h).count(),
        
        'total_payments': PaymentAudit.objects.count(),
        'payments_24h': PaymentAudit.objects.filter(created_at__gte=last_24h).count(),
        
        'total_edits': PropertyEditHistory.objects.count(),
        'edits_24h': PropertyEditHistory.objects.filter(edited_at__gte=last_24h).count(),
    }
    
    # Action breakdown
    action_breakdown = AuditLog.objects.filter(
        timestamp__gte=last_7d
    ).values('action').annotate(count=Count('id')).order_by('-count')[:10]
    
    # Recent audits
    recent_audits = AuditLog.objects.select_related('user').order_by('-timestamp')[:20]
    
    # Recent logins
    recent_logins = LoginHistory.objects.select_related('user').order_by('-login_at')[:10]
    
    # Recent payment events
    recent_payments = PaymentAudit.objects.select_related('user', 'payment').order_by('-created_at')[:10]
    
    # Recent property edits
    recent_edits = PropertyEditHistory.objects.select_related('user', 'property').order_by('-edited_at')[:10]
    
    context = {
        'stats': stats,
        'action_breakdown': action_breakdown,
        'recent_audits': recent_audits,
        'recent_logins': recent_logins,
        'recent_payments': recent_payments,
        'recent_edits': recent_edits,
    }
    
    return render(request, 'admin/audit_dashboard.html', context)


@staff_member_required
def audit_timeline(request, user_id):
    """View full audit trail for a specific user"""
    from accounts.models import User
    
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return JsonResponse({'error': 'User not found'}, status=404)
    
    # Get all audit events for this user
    audits = AuditLog.objects.filter(user=user).order_by('-timestamp')[:100]
    logins = LoginHistory.objects.filter(user=user).order_by('-login_at')[:50]
    payments = PaymentAudit.objects.filter(user=user).order_by('-created_at')[:50]
    
    context = {
        'user': user,
        'audits': audits,
        'logins': logins,
        'payments': payments,
        'total_logins': logins.count(),
        'active_sessions': logins.filter(is_active=True).count(),
    }
    
    return render(request, 'admin/audit_timeline.html', context)


@staff_member_required
def property_edit_history(request, property_id):
    """View edit history for a specific property"""
    from properties.models import Property
    
    try:
        prop = Property.objects.get(id=property_id)
    except Property.DoesNotExist:
        return JsonResponse({'error': 'Property not found'}, status=404)
    
    edits = PropertyEditHistory.objects.filter(property=prop).order_by('-edited_at')
    
    context = {
        'property': prop,
        'edits': edits,
        'total_edits': edits.count(),
    }
    
    return render(request, 'admin/property_edit_history.html', context)


@staff_member_required
def payment_audit_trail(request, payment_id):
    """View full audit trail for a payment"""
    from payments.models import Payment
    
    try:
        payment = Payment.objects.get(id=payment_id)
    except Payment.DoesNotExist:
        return JsonResponse({'error': 'Payment not found'}, status=404)
    
    audit_trail = PaymentAudit.objects.filter(payment=payment).order_by('created_at')
    
    context = {
        'payment': payment,
        'audit_trail': audit_trail,
    }
    
    return render(request, 'admin/payment_audit_trail.html', context)
