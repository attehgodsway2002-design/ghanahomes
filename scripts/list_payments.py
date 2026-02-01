import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
os.environ.setdefault('DJANGO_SETTINGS_MODULE','ghanahomes.settings')
import django
django.setup()
from payments.models import Payment
from django.contrib.auth import get_user_model

print('Recent Payments')
for p in Payment.objects.select_related('user').order_by('-created_at')[:20]:
    print(p.id, p.user.email if p.user else 'no-user', p.amount, p.currency, p.status, p.paystack_reference)

print('\nCount:', Payment.objects.count())
