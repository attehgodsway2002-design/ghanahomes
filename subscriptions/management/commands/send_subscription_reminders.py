from django.core.management.base import BaseCommand
from django.utils import timezone
from accounts.email_utils import send_subscription_renewal_reminder, send_subscription_expired
from subscriptions.models import Subscription

class Command(BaseCommand):
    help = 'Send subscription renewal reminders to users with expiring subscriptions (7 days before)'

    def handle(self, *args, **options):
        from datetime import timedelta
        
        # Get subscriptions expiring in 7 days
        today = timezone.now().date()
        target_date = today + timedelta(days=7)
        
        expiring_soon = Subscription.objects.filter(
            status='active',
            end_date=target_date
        ).select_related('user', 'plan')
        
        count = 0
        for subscription in expiring_soon:
            try:
                send_subscription_renewal_reminder(subscription)
                count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'Sent reminder to {subscription.user.email}')
                )
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'Failed to send reminder to {subscription.user.email}: {str(e)}')
                )
        
        self.stdout.write(
            self.style.SUCCESS(f'Successfully sent {count} subscription renewal reminders')
        )
