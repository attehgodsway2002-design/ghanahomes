from django.core.management.base import BaseCommand
from subscriptions.models import SubscriptionPlan


class Command(BaseCommand):
    help = 'Create or update the free tier subscription plan'

    def handle(self, *args, **options):
        free_plan, created = SubscriptionPlan.objects.update_or_create(
            plan_type='free',
            defaults={
                'name': 'Free',
                'description': 'Perfect for trying out GhanaHomes. Limited but fully functional.',
                'price_monthly': 0,
                'is_free': True,
                'property_limit': 3,
                'featured_listings': 0,
                'photo_limit': 5,
                'video_limit': 0,
                'priority_support': False,
                'analytics': False,
                'verified_badge': False,
                'social_media_promotion': False,
                'is_active': True,
            }
        )
        
        if created:
            self.stdout.write(
                self.style.SUCCESS(f'✓ Free tier plan created: {free_plan.name}')
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(f'✓ Free tier plan updated: {free_plan.name}')
            )
        
        self.stdout.write(self.style.SUCCESS('\nFree Tier Features:'))
        self.stdout.write(f'  - 3 properties max')
        self.stdout.write(f'  - 5 photos per property')
        self.stdout.write(f'  - No featured listings')
        self.stdout.write(f'  - No videos')
        self.stdout.write(f'  - Standard support')
