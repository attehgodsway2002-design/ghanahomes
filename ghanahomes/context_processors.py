from django.conf import settings


def google_maps_api_key(request):
    """Add GOOGLE_MAPS_API_KEY to template context."""
    return {
        'GOOGLE_MAPS_API_KEY': getattr(settings, 'GOOGLE_MAPS_API_KEY', '')
    }


def paystack_settings(request):
    """Add Paystack settings to template context."""
    return {
        'PAYSTACK_PUBLIC_KEY': getattr(settings, 'PAYSTACK_PUBLIC_KEY', '')
    }
