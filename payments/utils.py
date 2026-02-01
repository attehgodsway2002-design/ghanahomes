import hmac
import hashlib
from django.conf import settings
from typing import Dict, Any, Optional
from decimal import Decimal

def verify_webhook_signature(request_body: bytes, signature_header: str) -> bool:
    """
    Verify that the webhook request came from Paystack
    """
    if not signature_header:
        return False

    # Get the signature sent from Paystack
    expected_signature = signature_header

    # Create a hash using the secret key and the request body
    hash_object = hmac.new(
        settings.PAYSTACK_SECRET_KEY.encode('utf-8'),
        request_body,
        hashlib.sha512
    )
    generated_signature = hash_object.hexdigest()

    return hmac.compare_digest(generated_signature, expected_signature)

def format_amount_for_paystack(amount: Decimal) -> int:
    """
    Convert decimal amount to integer (pesewas) for Paystack
    """
    return int(amount * 100)

def format_paystack_amount(amount: int) -> Decimal:
    """
    Convert Paystack amount (pesewas) to decimal (cedis)
    """
    return Decimal(amount) / Decimal('100')

def get_paystack_error_message(response: Dict[str, Any]) -> str:
    """
    Extract human-readable error message from Paystack API response
    """
    if not isinstance(response, dict):
        return "Invalid response from payment provider"
    
    message = response.get('message', '')
    errors = response.get('errors', [])
    
    if errors:
        if isinstance(errors, list):
            message = '. '.join(errors)
        elif isinstance(errors, dict):
            message = '. '.join(f"{k}: {v}" for k, v in errors.items())
    
    return message or "Payment processing failed"

def validate_paystack_response(response: Dict[str, Any]) -> tuple[bool, Optional[str], Optional[Dict[str, Any]]]:
    """
    Validate Paystack API response and return status, error message, and data
    """
    if not isinstance(response, dict):
        return False, "Invalid response from payment provider", None
    
    status = response.get('status', False)
    data = response.get('data', {})
    
    if not status:
        error_msg = get_paystack_error_message(response)
        return False, error_msg, None
    
    return True, None, data