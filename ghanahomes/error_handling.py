"""
Error handling utilities for GhanaHomes
"""
import logging
import traceback
from django.http import JsonResponse, HttpResponse
from django.template.loader import render_to_string
from django.conf import settings
from django.views.decorators.http import require_http_methods

logger = logging.getLogger(__name__)


class GhanaHomesException(Exception):
    """Base exception for GhanaHomes application."""
    def __init__(self, message, status_code=400, user_message=None, error_code=None):
        self.message = message
        self.status_code = status_code
        self.user_message = user_message or message
        self.error_code = error_code or 'ERROR'
        super().__init__(self.message)


class ValidationException(GhanaHomesException):
    """Validation error exception."""
    def __init__(self, message, status_code=400, field=None):
        self.field = field
        super().__init__(message, status_code, message, 'VALIDATION_ERROR')


class PaymentException(GhanaHomesException):
    """Payment processing error."""
    def __init__(self, message, status_code=402):
        super().__init__(message, status_code, message, 'PAYMENT_ERROR')


class PermissionException(GhanaHomesException):
    """Permission denied error."""
    def __init__(self, message="You don't have permission to perform this action"):
        super().__init__(message, 403, message, 'PERMISSION_DENIED')


class ResourceNotFoundException(GhanaHomesException):
    """Resource not found error."""
    def __init__(self, resource_type="Resource", resource_id=None):
        message = f"{resource_type} not found"
        if resource_id:
            message += f" (ID: {resource_id})"
        super().__init__(message, 404, message, 'NOT_FOUND')


def log_error(request, exception, level=logging.ERROR):
    """Log error with request details."""
    logger.log(
        level,
        f"Error in {request.method} {request.path}",
        extra={
            'user': request.user if request.user.is_authenticated else 'Anonymous',
            'ip': get_client_ip(request),
            'exception': str(exception),
            'traceback': traceback.format_exc(),
        }
    )


def get_client_ip(request):
    """Get client IP address from request."""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def get_error_response(request, exception, is_ajax=False):
    """Generate appropriate error response based on request type."""
    if isinstance(exception, GhanaHomesException):
        status_code = exception.status_code
        message = exception.user_message
        error_code = exception.error_code
    else:
        status_code = 500
        message = 'An unexpected error occurred' if settings.DEBUG else 'Internal server error'
        error_code = 'INTERNAL_ERROR'
    
    if is_ajax or request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse(
            {
                'status': 'error',
                'message': message,
                'error_code': error_code,
            },
            status=status_code,
        )
    else:
        context = {
            'status_code': status_code,
            'message': message,
            'error_code': error_code,
            'exception': str(exception) if settings.DEBUG else None,
        }
        try:
            html = render_to_string(f'errors/{status_code}.html', context)
            return HttpResponse(html, status=status_code)
        except Exception:
            # Fallback to generic error page
            return HttpResponse(f'Error {status_code}: {message}', status=status_code)


class ErrorHandlingMiddleware:
    """Middleware for handling and logging exceptions."""
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        try:
            response = self.get_response(request)
        except GhanaHomesException as e:
            log_error(request, e, logging.WARNING)
            response = get_error_response(request, e)
        except Exception as e:
            log_error(request, e, logging.ERROR)
            response = get_error_response(request, e)
        
        return response


# Error handler decorators

def handle_errors(view_func=None, status_code=500):
    """Decorator to handle errors in views."""
    def decorator(func):
        def wrapper(request, *args, **kwargs):
            try:
                return func(request, *args, **kwargs)
            except GhanaHomesException as e:
                log_error(request, e, logging.WARNING)
                return get_error_response(request, e)
            except Exception as e:
                log_error(request, e, logging.ERROR)
                return get_error_response(request, e)
        return wrapper
    
    if view_func:
        return decorator(view_func)
    return decorator


def validate_payment_data(data):
    """Validate payment data and raise exception if invalid."""
    if not data.get('amount'):
        raise ValidationException("Amount is required", field='amount')
    
    if not isinstance(data['amount'], (int, float)) or data['amount'] <= 0:
        raise ValidationException("Amount must be greater than 0", field='amount')
    
    if not data.get('reference'):
        raise ValidationException("Payment reference is required", field='reference')
    
    return True


def validate_property_data(data):
    """Validate property data and raise exception if invalid."""
    required_fields = ['title', 'description', 'property_type', 'price', 'bedrooms', 'bathrooms']
    
    for field in required_fields:
        if not data.get(field):
            raise ValidationException(f"{field.replace('_', ' ')} is required", field=field)
    
    try:
        price = float(data['price'])
        if price <= 0:
            raise ValueError
    except (ValueError, TypeError):
        raise ValidationException("Price must be a valid positive number", field='price')
    
    return True


def validate_user_data(data):
    """Validate user registration data and raise exception if invalid."""
    required_fields = ['username', 'email', 'password', 'user_type']
    
    for field in required_fields:
        if not data.get(field):
            raise ValidationException(f"{field.replace('_', ' ')} is required", field=field)
    
    if len(data['password']) < 8:
        raise ValidationException("Password must be at least 8 characters long", field='password')
    
    if data['user_type'] not in ['tenant', 'landlord']:
        raise ValidationException("Invalid user type", field='user_type')
    
    return True
