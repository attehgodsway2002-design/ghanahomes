from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from properties.models import Property

class Command(BaseCommand):
    help = 'Check and archive old properties (listed more than 90 days ago)'

    def handle(self, *args, **options):
        today = timezone.now()
        ninety_days_ago = today - timedelta(days=90)
        
        # Get properties that have been listed for more than 90 days
        old_properties = Property.objects.filter(
            status='available',
            published_at__lt=ninety_days_ago
        ).select_related('owner')
        
        count = 0
        for property_obj in old_properties:
            try:
                # Mark as unavailable (archived)
                property_obj.status = 'unavailable'
                property_obj.save()
                count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'Archived property "{property_obj.title}" for {property_obj.owner.email}')
                )
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'Failed to process property "{property_obj.title}": {str(e)}')
                )
        
        self.stdout.write(
            self.style.SUCCESS(f'Successfully archived {count} old properties')
        )
