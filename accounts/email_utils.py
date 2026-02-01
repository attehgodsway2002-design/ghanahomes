"""
Email template utilities and configuration
"""
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.core.mail import send_mail
from django.conf import settings


def send_templated_email(template_name, context, subject, recipient_email):
    """
    Send an email using a template.
    
    Args:
        template_name (str): Path to email template (e.g., 'emails/password_reset.html')
        context (dict): Context variables for the template
        subject (str): Email subject line
        recipient_email (str): Recipient email address
        
    Returns:
        bool: True if email sent successfully, False otherwise
        
    Example:
        send_templated_email(
            'emails/password_reset.html',
            {'user': user, 'reset_url': 'https://example.com/reset/abc123'},
            'Password Reset Request - GhanaHomes',
            'user@example.com'
        )
    """
    try:
        html_message = render_to_string(template_name, context)
        plain_message = strip_tags(html_message)
        
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[recipient_email],
            html_message=html_message,
            fail_silently=False,
        )
        return True
    except Exception as e:
        print(f'Error sending email: {str(e)}')
        return False


def send_templated_email_to_multiple(template_name, context, subject, recipient_emails):
    """
    Send an email using a template to multiple recipients.
    
    Args:
        template_name (str): Path to email template
        context (dict): Context variables for the template
        subject (str): Email subject line
        recipient_emails (list): List of recipient email addresses
        
    Returns:
        bool: True if all emails sent successfully, False otherwise
    """
    try:
        html_message = render_to_string(template_name, context)
        plain_message = strip_tags(html_message)
        
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=recipient_emails,
            html_message=html_message,
            fail_silently=False,
        )
        return True
    except Exception as e:
        print(f'Error sending email to multiple recipients: {str(e)}')
        return False


# Email template registry - maps email types to their configuration
EMAIL_TEMPLATES = {
    'password_reset': {
        'template': 'emails/password_reset.html',
        'subject': 'Password Reset Request - GhanaHomes',
        'description': 'Sent when user requests password reset',
    },
    'password_changed': {
        'template': 'emails/password_changed.html',
        'subject': 'Password Changed Successfully - GhanaHomes',
        'description': 'Confirmation sent after password is changed',
    },
    'welcome': {
        'template': 'emails/welcome.html',
        'subject': 'Welcome to GhanaHomes!',
        'description': 'Generic welcome email',
    },
    'welcome_landlord': {
        'template': 'emails/welcome_landlord.html',
        'subject': 'Welcome to GhanaHomes - Landlord Portal!',
        'description': 'Welcome email for landlords with property posting info',
    },
    'welcome_tenant': {
        'template': 'emails/welcome_tenant.html',
        'subject': 'Welcome to GhanaHomes - Find Your Perfect Home!',
        'description': 'Welcome email for tenants with browsing info',
    },
    'payment_success_landlord': {
        'template': 'emails/payment_success_landlord.html',
        'subject': 'Payment Successful - Start Posting Properties!',
        'description': 'Post-payment email for landlords with property limits',
    },
    'email_verification': {
        'template': 'emails/email_verification.html',
        'subject': 'Verify Your Email Address - GhanaHomes',
        'description': 'Email verification link for account activation',
    },
    'account_activated': {
        'template': 'emails/account_activated.html',
        'subject': 'Your Account is Activated! - GhanaHomes',
        'description': 'Confirmation email after email verification',
    },
    'subscription_renewal_reminder': {
        'template': 'emails/subscription_renewal_reminder.html',
        'subject': 'Your Subscription Expires Soon - Renew Now',
        'description': 'Reminder email before subscription expiration',
    },
    'subscription_expired': {
        'template': 'emails/subscription_expired.html',
        'subject': 'Your Subscription Has Expired - GhanaHomes',
        'description': 'Alert when subscription expires',
    },
    'subscription_cancelled': {
        'template': 'emails/subscription_cancelled.html',
        'subject': 'Subscription Cancelled - GhanaHomes',
        'description': 'Confirmation of subscription cancellation',
    },
    'payment_failed': {
        'template': 'emails/payment_failed.html',
        'subject': 'Payment Failed - Please Try Again',
        'description': 'Alert when payment fails with retry option',
    },
    'property_listed': {
        'template': 'emails/property_listed.html',
        'subject': 'Property Successfully Listed! - GhanaHomes',
        'description': 'Confirmation when property is posted',
    },
    'property_expired': {
        'template': 'emails/property_expired.html',
        'subject': 'Your Property Listing Has Expired',
        'description': 'Alert when property listing expires',
    },
    'new_inquiry': {
        'template': 'emails/new_inquiry.html',
        'subject': 'New Inquiry Received! 🎉 - GhanaHomes',
        'description': 'Alert when landlord receives new inquiry',
    },
    'chat_room_created': {
        'template': 'emails/chat_room_created.html',
        'subject': 'New Conversation Started - GhanaHomes',
        'description': 'Notification of new chat room creation',
    },
    'refund_confirmation': {
        'template': 'emails/refund_confirmation.html',
        'subject': 'Refund Processed Successfully - GhanaHomes',
        'description': 'Confirmation email when refund is processed',
    },
    'invoice_receipt': {
        'template': 'emails/invoice_receipt.html',
        'subject': 'Payment Invoice & Receipt - GhanaHomes',
        'description': 'Detailed invoice and receipt for payment',
    },
    'verification_approved': {
        'template': 'emails/verification_approved.html',
        'subject': 'Your Account Verification - Approved',
        'description': 'Sent when user account verification is approved',
    },
    'verification_declined': {
        'template': 'emails/verification_declined.html',
        'subject': 'Your Account Verification - Declined',
        'description': 'Sent when user account verification is declined',
    },
    'verification_submitted': {
        'template': 'emails/verification_submitted.html',
        'subject': 'Verification Request Received - GhanaHomes',
        'description': 'Confirmation email when verification request is submitted',
    },
    
    # Admin Notification Emails
    'admin_verification_submitted': {
        'template': 'emails/admin_verification_submitted.html',
        'subject': '[ADMIN] New Verification Request - Review Required',
        'description': 'Admin notification when verification request submitted',
    },
    'admin_verification_approved': {
        'template': 'emails/admin_verification_approved.html',
        'subject': '[ADMIN] Verification Approved - {{ user.username }}',
        'description': 'Admin notification when verification approved',
    },
    'admin_verification_declined': {
        'template': 'emails/admin_verification_declined.html',
        'subject': '[ADMIN] Verification Declined - {{ user.username }}',
        'description': 'Admin notification when verification declined',
    },
    'admin_property_listed': {
        'template': 'emails/admin_property_listed.html',
        'subject': '[ADMIN] New Property Listed - Review Required',
        'description': 'Admin notification when property is listed',
    },
    'admin_new_inquiry': {
        'template': 'emails/admin_new_inquiry.html',
        'subject': '[ADMIN] New Inquiry - Action Required',
        'description': 'Admin notification when new inquiry received',
    },
    'admin_payment_completed': {
        'template': 'emails/admin_payment_completed.html',
        'subject': '[ADMIN] Payment Completed - {{ currency }}{{ amount }}',
        'description': 'Admin notification when payment completed',
    },
    'admin_payment_failed': {
        'template': 'emails/admin_payment_failed.html',
        'subject': '[ADMIN] Payment Failed - Attention Required',
        'description': 'Admin notification when payment fails',
    },
}


# Specific email sending functions for new templates

def send_email_verification(user, verification_url):
    """Send email verification link to user."""
    return send_templated_email(
        'emails/email_verification.html',
        {
            'user': user,
            'verification_url': verification_url,
        },
        'Verify Your Email Address - GhanaHomes',
        user.email,
    )


def send_account_activated(user, dashboard_url, browse_url):
    """Send account activated confirmation email."""
    return send_templated_email(
        'emails/account_activated.html',
        {
            'user': user,
            'dashboard_url': dashboard_url,
            'browse_url': browse_url,
        },
        'Your Account is Activated! - GhanaHomes',
        user.email,
    )


def send_subscription_renewal_reminder(user, subscription, days_remaining, renewal_url):
    """Send subscription renewal reminder before expiration."""
    return send_templated_email(
        'emails/subscription_renewal_reminder.html',
        {
            'user': user,
            'subscription': subscription,
            'days_remaining': days_remaining,
            'renewal_url': renewal_url,
        },
        'Your Subscription Expires Soon - Renew Now',
        user.email,
    )


def send_subscription_expired(user, subscription, renew_url):
    """Send subscription expired alert."""
    return send_templated_email(
        'emails/subscription_expired.html',
        {
            'user': user,
            'subscription': subscription,
            'renew_url': renew_url,
        },
        'Your Subscription Has Expired - GhanaHomes',
        user.email,
    )


def send_subscription_cancelled(user, subscription, cancellation_date, plans_url):
    """Send subscription cancellation confirmation."""
    return send_templated_email(
        'emails/subscription_cancelled.html',
        {
            'user': user,
            'subscription': subscription,
            'cancellation_date': cancellation_date,
            'plans_url': plans_url,
        },
        'Subscription Cancelled - GhanaHomes',
        user.email,
    )


def send_payment_failed(user, amount, plan_name, reference_code, failure_reason, retry_url):
    """Send payment failed alert."""
    return send_templated_email(
        'emails/payment_failed.html',
        {
            'user': user,
            'amount': amount,
            'plan_name': plan_name,
            'reference_code': reference_code,
            'failure_reason': failure_reason,
            'retry_url': retry_url,
        },
        'Payment Failed - Please Try Again',
        user.email,
    )


def send_property_listed(user, property_obj, posted_date, property_url):
    """Send property listed confirmation."""
    return send_templated_email(
        'emails/property_listed.html',
        {
            'user': user,
            'property': property_obj,
            'posted_date': posted_date,
            'property_url': property_url,
        },
        'Property Successfully Listed! - GhanaHomes',
        user.email,
    )


def send_property_expired(user, property_obj, expiry_date, renew_url):
    """Send property expiration alert."""
    return send_templated_email(
        'emails/property_expired.html',
        {
            'user': user,
            'property': property_obj,
            'expiry_date': expiry_date,
            'renew_url': renew_url,
        },
        'Your Property Listing Has Expired',
        user.email,
    )


def send_new_inquiry(landlord, tenant, property_obj, message, chat_url, inquiry_date):
    """Send new inquiry notification to landlord."""
    return send_templated_email(
        'emails/new_inquiry.html',
        {
            'landlord': landlord,
            'tenant': tenant,
            'property': property_obj,
            'message': message,
            'chat_url': chat_url,
            'inquiry_date': inquiry_date,
        },
        'New Inquiry Received! 🎉 - GhanaHomes',
        landlord.email,
    )


def send_chat_room_created(recipient, initiator, property_obj, initial_message, chat_url, conversation_date):
    """Send chat room creation notification."""
    return send_templated_email(
        'emails/chat_room_created.html',
        {
            'recipient': recipient,
            'initiator': initiator,
            'property': property_obj,
            'initial_message': initial_message,
            'chat_url': chat_url,
            'conversation_date': conversation_date,
        },
        'New Conversation Started - GhanaHomes',
        recipient.email,
    )


def send_refund_confirmation(user, refund_amount, reference_code, refund_date, refund_reason):
    """Send refund confirmation email."""
    return send_templated_email(
        'emails/refund_confirmation.html',
        {
            'user': user,
            'refund_amount': refund_amount,
            'reference_code': reference_code,
            'refund_date': refund_date,
            'refund_reason': refund_reason,
        },
        'Refund Processed Successfully - GhanaHomes',
        user.email,
    )


def send_verification_submitted(user, license_number, submitted_date):
    """Send confirmation email when verification request is submitted."""
    return send_templated_email(
        'emails/verification_submitted.html',
        {
            'user': user,
            'license_number': license_number,
            'submitted_date': submitted_date.strftime('%B %d, %Y at %I:%M %p'),
        },
        'Verification Request Received - GhanaHomes',
        user.email,
    )


def send_verification_approved(user, profile_url):
    """Send confirmation email when verification is approved."""
    return send_templated_email(
        'emails/verification_approved.html',
        {
            'user': user,
            'profile_url': profile_url,
        },
        'Your Account Verification - Approved',
        user.email,
    )


def send_verification_declined(user, reason, retry_url):
    """Send notification email when verification is declined."""
    return send_templated_email(
        'emails/verification_declined.html',
        {
            'user': user,
            'reason': reason,
            'retry_url': retry_url,
        },
        'Your Account Verification - Declined',
        user.email,
    )

def send_invoice_receipt(user, payment, subscription, invoice_data):
    """Send detailed invoice and receipt email."""
    context = {
        'user': user,
        'payment': payment,
        'subscription': subscription,
        **invoice_data,
    }
    return send_templated_email(
        'emails/invoice_receipt.html',
        context,
        'Payment Invoice & Receipt - GhanaHomes',
        user.email,
    )

# ============================================================================
# ADMIN NOTIFICATION EMAIL FUNCTIONS
# ============================================================================

def get_admin_emails():
    """Get list of admin emails from settings."""
    from django.conf import settings
    return getattr(settings, 'ADMIN_NOTIFICATION_EMAILS', ['realhuntsmen.tech@gmail.com'])


def should_send_admin_notification(notification_type):
    """Check if this notification type should be sent."""
    from django.conf import settings
    notifications = getattr(settings, 'ADMIN_NOTIFICATIONS', {})
    return notifications.get(notification_type, True)


def send_admin_verification_submitted(verification_request, request_obj=None):
    """Send admin notification when verification request is submitted."""
    if not should_send_admin_notification('verification_submitted'):
        return
    
    from django.urls import reverse
    base_url = getattr(request_obj, 'build_absolute_uri', lambda x: '') if request_obj else None
    
    try:
        admin_verification_url = '/accounts/admin/verification/{}/'.format(verification_request.id)
        admin_user_url = '/admin/accounts/user/{}/change/'.format(verification_request.user.id)
        
        context = {
            'user': verification_request.user,
            'license_number': verification_request.license_number,
            'submitted_date': verification_request.created_at.strftime('%B %d, %Y at %I:%M %p'),
            'admin_verification_url': admin_verification_url,
            'admin_user_url': admin_user_url,
        }
        
        subject = '[ADMIN] New Verification Request - Review Required'
        recipient_emails = get_admin_emails()
        
        return send_templated_email_to_multiple(
            'emails/admin_verification_submitted.html',
            context,
            subject,
            recipient_emails,
        )
    except Exception as e:
        print(f"Error sending admin verification notification: {e}")
        return False


def send_admin_verification_approved(verification_request, approved_by_user):
    """Send admin notification when verification is approved."""
    if not should_send_admin_notification('verification_approved'):
        return
    
    try:
        context = {
            'user': verification_request.user,
            'approved_by': approved_by_user.get_full_name() or approved_by_user.username,
            'approved_at': verification_request.reviewed_at.strftime('%B %d, %Y at %I:%M %p'),
        }
        
        subject = '[ADMIN] Verification Approved - {}'.format(verification_request.user.username)
        recipient_emails = get_admin_emails()
        
        return send_templated_email_to_multiple(
            'emails/admin_verification_approved.html',
            context,
            subject,
            recipient_emails,
        )
    except Exception as e:
        print(f"Error sending admin verification approval notification: {e}")
        return False


def send_admin_verification_declined(verification_request, declined_by_user):
    """Send admin notification when verification is declined."""
    if not should_send_admin_notification('verification_declined'):
        return
    
    try:
        context = {
            'user': verification_request.user,
            'declined_by': declined_by_user.get_full_name() or declined_by_user.username,
            'declined_at': verification_request.reviewed_at.strftime('%B %d, %Y at %I:%M %p'),
            'decline_reason': verification_request.decline_reason,
        }
        
        subject = '[ADMIN] Verification Declined - {}'.format(verification_request.user.username)
        recipient_emails = get_admin_emails()
        
        return send_templated_email_to_multiple(
            'emails/admin_verification_declined.html',
            context,
            subject,
            recipient_emails,
        )
    except Exception as e:
        print(f"Error sending admin verification decline notification: {e}")
        return False


def send_admin_property_listed(property_obj, request_obj=None):
    """Send admin notification when property is listed."""
    if not should_send_admin_notification('property_listed'):
        return
    
    try:
        admin_property_url = '/admin/properties/property/{}/change/'.format(property_obj.id)
        admin_user_url = '/admin/accounts/user/{}/change/'.format(property_obj.owner.id)
        
        context = {
            'property': property_obj,
            'listed_date': property_obj.created_at.strftime('%B %d, %Y at %I:%M %p'),
            'admin_property_url': admin_property_url,
            'admin_user_url': admin_user_url,
        }
        
        subject = '[ADMIN] New Property Listed - Review Required'
        recipient_emails = get_admin_emails()
        
        return send_templated_email_to_multiple(
            'emails/admin_property_listed.html',
            context,
            subject,
            recipient_emails,
        )
    except Exception as e:
        print(f"Error sending admin property notification: {e}")
        return False


def send_admin_new_inquiry(chat_room, message_content, request_obj=None):
    """Send admin notification when new inquiry is received."""
    if not should_send_admin_notification('new_inquiry'):
        return
    
    try:
        admin_tenant_url = '/admin/accounts/user/{}/change/'.format(chat_room.tenant.id)
        admin_landlord_url = '/admin/accounts/user/{}/change/'.format(chat_room.landlord.id)
        admin_property_url = '/admin/properties/property/{}/change/'.format(chat_room.property.id)
        
        context = {
            'tenant': chat_room.tenant,
            'landlord': chat_room.landlord,
            'property': chat_room.property,
            'message': message_content[:500],  # First 500 chars
            'preferred_contact': getattr(chat_room, 'preferred_contact', 'Not specified'),
            'inquiry_date': chat_room.created_at.strftime('%B %d, %Y at %I:%M %p'),
            'admin_tenant_url': admin_tenant_url,
            'admin_landlord_url': admin_landlord_url,
            'admin_property_url': admin_property_url,
        }
        
        subject = '[ADMIN] New Inquiry - Action Required'
        recipient_emails = get_admin_emails()
        
        return send_templated_email_to_multiple(
            'emails/admin_new_inquiry.html',
            context,
            subject,
            recipient_emails,
        )
    except Exception as e:
        print(f"Error sending admin inquiry notification: {e}")
        return False


def send_admin_payment_completed(payment_obj):
    """Send admin notification when payment is completed."""
    if not should_send_admin_notification('payment_completed'):
        return
    
    try:
        admin_user_url = '/admin/accounts/user/{}/change/'.format(payment_obj.user.id)
        
        context = {
            'user': payment_obj.user,
            'amount': payment_obj.amount,
            'currency': payment_obj.currency,
            'plan_name': payment_obj.subscription.plan.name if payment_obj.subscription else 'N/A',
            'reference_code': payment_obj.paystack_reference or str(payment_obj.id),
            'payment_date': payment_obj.created_at.strftime('%B %d, %Y at %I:%M %p'),
            'admin_user_url': admin_user_url,
        }
        
        subject = '[ADMIN] Payment Completed - {}${}'.format(payment_obj.currency, payment_obj.amount)
        recipient_emails = get_admin_emails()
        
        return send_templated_email_to_multiple(
            'emails/admin_payment_completed.html',
            context,
            subject,
            recipient_emails,
        )
    except Exception as e:
        print(f"Error sending admin payment notification: {e}")
        return False


def send_admin_payment_failed(payment_obj, failure_reason=''):
    """Send admin notification when payment fails."""
    if not should_send_admin_notification('payment_failed'):
        return
    
    try:
        admin_user_url = '/admin/accounts/user/{}/change/'.format(payment_obj.user.id)
        
        context = {
            'user': payment_obj.user,
            'amount': payment_obj.amount,
            'currency': payment_obj.currency,
            'plan_name': payment_obj.subscription.plan.name if payment_obj.subscription else 'N/A',
            'failure_reason': failure_reason or 'Unknown error',
            'payment_date': payment_obj.created_at.strftime('%B %d, %Y at %I:%M %p'),
            'admin_user_url': admin_user_url,
        }
        
        subject = '[ADMIN] Payment Failed - {}${} - Attention Required'.format(
            payment_obj.currency, payment_obj.amount
        )
        recipient_emails = get_admin_emails()
        
        return send_templated_email_to_multiple(
            'emails/admin_payment_failed.html',
            context,
            subject,
            recipient_emails,
        )
    except Exception as e:
        print(f"Error sending admin payment failure notification: {e}")
        return False