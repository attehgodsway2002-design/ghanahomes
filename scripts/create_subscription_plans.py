import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
os.environ.setdefault('DJANGO_SETTINGS_MODULE','ghanahomes.settings')
import django
django.setup()

from subscriptions.models import SubscriptionPlan

# Create or update subscription plans
plans = [
    {
        'name': 'Basic',
        'plan_type': 'basic',
        'description': 'Perfect for individual landlords and small property managers.',
        'price_monthly': '50.00',
        'price_quarterly': '140.00',
        'price_yearly': '540.00',
        'property_limit': 3,
        'featured_listings': 0,
        'photo_limit': 10,
        'video_limit': 0,
    },
    {
        'name': 'Standard',
        'plan_type': 'standard',
        'description': 'Ideal for growing property portfolios with enhanced features.',
        'price_monthly': '100.00',
        'price_quarterly': '270.00',
        'price_yearly': '1020.00',
        'property_limit': 10,
        'featured_listings': 2,
        'photo_limit': 20,
        'video_limit': 1,
        'analytics': True,
    },
    {
        'name': 'Premium',
        'plan_type': 'premium',
        'description': 'Full-featured solution for professional real estate businesses.',
        'price_monthly': '200.00',
        'price_quarterly': '540.00',
        'price_yearly': '2040.00',
        'property_limit': 25,
        'featured_listings': 5,
        'photo_limit': 30,
        'video_limit': 2,
        'analytics': True,
        'priority_support': True,
        'verified_badge': True,
    },
    {
        'name': 'Enterprise',
        'plan_type': 'enterprise',
        'description': 'Custom solution for large agencies and property developers.',
        'price_monthly': '500.00',
        'price_quarterly': '1350.00',
        'price_yearly': '5100.00',
        'property_limit': 100,
        'featured_listings': 20,
        'photo_limit': 50,
        'video_limit': 5,
        'analytics': True,
        'priority_support': True,
        'verified_badge': True,
        'social_media_promotion': True,
    },
]

for plan_data in plans:
    plan, created = SubscriptionPlan.objects.get_or_create(
        plan_type=plan_data['plan_type'],
        defaults=plan_data
    )
    
    if not created:
        # Update existing plan
        for key, value in plan_data.items():
            setattr(plan, key, value)
        plan.save()
    
    action = 'Created' if created else 'Updated'
    print(f'{action} {plan.name} plan')

print('\nCurrent Subscription Plans:')
for plan in SubscriptionPlan.objects.all():
    print(f'{plan.name}: ₵{plan.price_monthly}/month - {plan.property_limit} properties')