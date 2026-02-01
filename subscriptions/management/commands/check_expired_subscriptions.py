from django.core.management.base import BaseCommand
from django.utils import timezone
from subscriptions.models import Subscription

class Command(BaseCommand):
    help = 'Check and expire subscriptions that have reached their end date'

    def handle(self, *args, **options):
        today = timezone.now().date()
        
        # Get subscriptions that have expired
        expired = Subscription.objects.filter(
            status='active',
            end_date__lt=today
        ).select_related('user', 'plan')
        
        count = 0
        for subscription in expired:
            try:
                # Mark as expired
                subscription.status = 'expired'
                subscription.save()
                count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'Expired subscription for {subscription.user.email}')
                )
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'Failed to process subscription for {subscription.user.email}: {str(e)}')
                )
        
        self.stdout.write(
            self.style.SUCCESS(f'Successfully expired {count} subscriptions')
        )
