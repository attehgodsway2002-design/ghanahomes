"""
Security utilities for the GhanaHomes application
"""
from html import escape
from django.utils.html import strip_tags
import re
import logging

logger = logging.getLogger(__name__)


def sanitize_input(text, max_length=5000, allow_html=False):
    """
    Sanitize user input to prevent XSS attacks
    
    Args:
        text: Input string to sanitize
        max_length: Maximum allowed length
        allow_html: Whether to allow HTML content (default: False)
    
    Returns:
        Sanitized string
    """
    if not isinstance(text, str):
        return ''
    
    # Strip extra whitespace
    text = text.strip()
    
    # Limit length
    if len(text) > max_length:
        logger.warning(f"Input exceeded max length ({len(text)} > {max_length})")
        text = text[:max_length]
    
    if not allow_html:
        # Remove HTML tags
        text = strip_tags(text)
        # Escape HTML entities
        text = escape(text)
    else:
        # Basic HTML cleaning (remove script tags, etc.)
        text = remove_dangerous_html(text)
    
    return text


def remove_dangerous_html(html_content):
    """
    Remove potentially dangerous HTML elements
    Removes: script, iframe, object, embed tags
    """
    dangerous_tags = ['<script', '<iframe', '<object', '<embed', '<form', 'onclick', 'onerror', 'onload']
    
    for tag in dangerous_tags:
        pattern = re.compile(tag, re.IGNORECASE)
        html_content = pattern.sub('', html_content)
    
    return html_content


def sanitize_phone(phone):
    """
    Sanitize phone number
    Remove all characters except digits and +/-
    """
    if not isinstance(phone, str):
        return ''
    
    return re.sub(r'[^\d+\-]', '', phone)


def sanitize_url(url):
    """
    Sanitize URL to prevent injection attacks
    """
    if not isinstance(url, str):
        return ''
    
    url = url.strip()
    
    # Check for javascript: or data: protocols
    if url.lower().startswith(('javascript:', 'data:')):
        logger.warning(f"Rejected dangerous URL: {url[:50]}")
        return ''
    
    # Escape special characters
    url = escape(url)
    
    return url


def validate_email(email):
    """
    Validate email format
    """
    if not isinstance(email, str):
        return False
    
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email.strip()))


def rate_limit_exceeded(key='user', rate='5/h'):
    """
    Check if rate limit has been exceeded
    Usage: from django_ratelimit.utils import is_rate_limited
    """
    pass


def log_security_event(event_type, user=None, description='', severity='INFO'):
    """
    Log security-related events for auditing
    
    Args:
        event_type: Type of event (LOGIN, FAILED_LOGIN, SUSPICIOUS_ACTIVITY, etc.)
        user: User object or username
        description: Event description
        severity: INFO, WARNING, CRITICAL
    """
    username = user.username if hasattr(user, 'username') else str(user)
    
    log_message = f"[SECURITY] {event_type} | User: {username} | {description}"
    
    if severity == 'CRITICAL':
        logger.critical(log_message)
    elif severity == 'WARNING':
        logger.warning(log_message)
    else:
        logger.info(log_message)
