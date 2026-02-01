from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from properties.models import Property

class Command(BaseCommand):
    help = 'Send property activity reminders to landlords with inactive listings'

    def handle(self, *args, **options):
        today = timezone.now()
        thirty_days_ago = today - timedelta(days=30)
        sixty_days_ago = today - timedelta(days=60)
        
        # Get properties published 30-60 days ago (may need renewal reminders)
        inactive_properties = Property.objects.filter(
            status='available',
            published_at__gte=sixty_days_ago,
            published_at__lt=thirty_days_ago
        ).select_related('owner')
        
        count = 0
        for property_obj in inactive_properties:
            try:
                # Log reminder for activity
                count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'Reminder: Property "{property_obj.title}" ({property_obj.id}) may need renewal')
                )
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'Failed to send reminder for "{property_obj.title}": {str(e)}')
                )
        
        self.stdout.write(
            self.style.SUCCESS(f'Successfully processed {count} property reminders')
        )
