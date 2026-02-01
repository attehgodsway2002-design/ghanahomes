"""
Audit logging middleware for capturing request context and tracking login/logout
"""
from django.utils.deprecation import MiddlewareMixin
from django.contrib.auth.signals import user_logged_in, user_logged_out
from django.dispatch import receiver
from .audit_models import LoginHistory
from .audit_utils import extract_request_info
from django.utils import timezone


class AuditLoggingMiddleware(MiddlewareMixin):
    """
    Middleware to capture and store request context for audit logging.
    Makes request info available to views and signals.
    """
    
    def process_request(self, request):
        """Store request info in thread-local storage"""
        ip_address, user_agent = extract_request_info(request)
        request.audit_ip_address = ip_address
        request.audit_user_agent = user_agent
        return None


@receiver(user_logged_in)
def log_user_login(sender, request, user, **kwargs):
    """Track user login"""
    try:
        ip_address, user_agent = extract_request_info(request)
        LoginHistory.objects.create(
            user=user,
            ip_address=ip_address or '0.0.0.0',
            user_agent=user_agent,
            is_active=True
        )
    except Exception as e:
        print(f"Error logging user login: {e}")


@receiver(user_logged_out)
def log_user_logout(sender, request, user, **kwargs):
    """Track user logout"""
    try:
        if user:
            # Find and close the most recent active session
            last_login = LoginHistory.objects.filter(
                user=user,
                is_active=True
            ).order_by('-login_at').first()
            
            if last_login:
                last_login.logout_at = timezone.now()
                last_login.is_active = False
                last_login.save(update_fields=['logout_at', 'is_active'])
    except Exception as e:
        print(f"Error logging user logout: {e}")
