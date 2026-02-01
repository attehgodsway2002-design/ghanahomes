"""
Admin views for verification request management.
Provides a dedicated dashboard for reviewing and managing verification requests.
"""
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Q
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from .models import VerificationRequest
from .email_utils import send_templated_email


@staff_member_required
def verification_dashboard(request):
    """Main verification requests dashboard"""
    
    # Get filter parameters
    status_filter = request.GET.get('status', 'pending')
    search_query = request.GET.get('q', '')
    
    # Build queryset
    queryset = VerificationRequest.objects.select_related('user', 'reviewed_by').all()
    
    if status_filter and status_filter != 'all':
        queryset = queryset.filter(status=status_filter)
    
    if search_query:
        queryset = queryset.filter(
            Q(user__username__icontains=search_query) |
            Q(user__email__icontains=search_query) |
            Q(user__company_name__icontains=search_query) |
            Q(license_number__icontains=search_query)
        )
    
    # Get counts
    pending_count = VerificationRequest.objects.filter(status='pending').count()
    approved_count = VerificationRequest.objects.filter(status='approved').count()
    declined_count = VerificationRequest.objects.filter(status='declined').count()
    
    context = {
        'verification_requests': queryset,
        'pending_count': pending_count,
        'approved_count': approved_count,
        'declined_count': declined_count,
        'current_status': status_filter,
        'search_query': search_query,
    }
    
    return render(request, 'admin/verification_dashboard.html', context)


@staff_member_required
def verification_detail(request, pk):
    """View detailed verification request"""
    verification_request = get_object_or_404(VerificationRequest, pk=pk)
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'approve':
            verification_request.approve(request.user)
            
            # Send approval email to user
            try:
                send_templated_email(
                    'emails/verification_approved.html',
                    {
                        'user': verification_request.user,
                        'profile_url': request.build_absolute_uri(f'/accounts/profile/'),
                    },
                    'Your Account Verification - Approved',
                    verification_request.user.email,
                )
            except Exception as e:
                print(f"Error sending verification approved email: {e}")
            
            # Send admin notification
            try:
                from .email_utils import send_admin_verification_approved
                send_admin_verification_approved(verification_request, request.user)
            except Exception as e:
                print(f"Error sending admin verification approval notification: {e}")
            
            messages.success(request, f'Verification request for {verification_request.user.username} has been approved.')
            return redirect('admin:verification_dashboard')
        
        elif action == 'decline':
            reason = request.POST.get('decline_reason', '')
            
            if not reason:
                messages.error(request, 'Please provide a reason for declining the verification request.')
            else:
                verification_request.decline(request.user, reason)
                
                # Send decline email to user
                try:
                    send_templated_email(
                        'emails/verification_declined.html',
                        {
                            'user': verification_request.user,
                            'reason': reason,
                            'retry_url': request.build_absolute_uri(f'/accounts/verify/'),
                        },
                        'Your Account Verification - Declined',
                        verification_request.user.email,
                    )
                except Exception as e:
                    print(f"Error sending verification declined email: {e}")
                
                # Send admin notification
                try:
                    from .email_utils import send_admin_verification_declined
                    send_admin_verification_declined(verification_request, request.user)
                except Exception as e:
                    print(f"Error sending admin verification decline notification: {e}")
                
                messages.success(request, f'Verification request for {verification_request.user.username} has been declined.')
                return redirect('admin:verification_dashboard')
    
    context = {
        'verification_request': verification_request,
    }
    
    return render(request, 'admin/verification_detail.html', context)


@staff_member_required
@require_http_methods(["POST"])
def verification_quick_approve(request, pk):
    """Quick approve via AJAX"""
    verification_request = get_object_or_404(VerificationRequest, pk=pk)
    
    if verification_request.status != 'pending':
        return JsonResponse({'status': 'error', 'message': 'Only pending requests can be approved.'}, status=400)
    
    verification_request.approve(request.user)
    
    # Send approval email to user
    try:
        send_templated_email(
            'emails/verification_approved.html',
            {
                'user': verification_request.user,
                'profile_url': request.build_absolute_uri(f'/accounts/profile/'),
            },
            'Your Account Verification - Approved',
            verification_request.user.email,
        )
    except Exception as e:
        print(f"Error sending verification approved email: {e}")
    
    # Send admin notification
    try:
        from .email_utils import send_admin_verification_approved
        send_admin_verification_approved(verification_request, request.user)
    except Exception as e:
        print(f"Error sending admin verification approval notification: {e}")
    
    return JsonResponse({
        'status': 'success',
        'message': f'Verification for {verification_request.user.username} approved.',
    })

