import os
from django.conf import settings

def ensure_payment_dirs():
    """Ensure required directories exist for payment files"""
    receipts_dir = os.path.join(settings.MEDIA_ROOT, 'receipts')
    if not os.path.exists(receipts_dir):
        os.makedirs(receipts_dir)

# Create required directories
ensure_payment_dirs()
