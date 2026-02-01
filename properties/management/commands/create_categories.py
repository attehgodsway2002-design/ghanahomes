"""
Management command to create default property categories
"""
from django.core.management.base import BaseCommand
from properties.models import PropertyCategory

class Command(BaseCommand):
    help = 'Create default property categories'

    def handle(self, *args, **options):
        categories = [
            {
                'name': 'Apartment',
                'icon': 'fas fa-building',
                'description': 'Modern apartments and flats'
            },
            {
                'name': 'House',
                'icon': 'fas fa-home',
                'description': 'Single family homes and villas'
            },
            {
                'name': 'Commercial',
                'icon': 'fas fa-store',
                'description': 'Shops, offices and commercial spaces'
            },
            {
                'name': 'Land',
                'icon': 'fas fa-map',
                'description': 'Residential and commercial plots'
            },
            {
                'name': 'Duplex',
                'icon': 'fas fa-home',
                'description': 'Semi-detached and duplex properties'
            },
            {
                'name': 'Studio',
                'icon': 'fas fa-door-open',
                'description': 'Studio apartments and rooms'
            },
            {
                'name': 'Villa',
                'icon': 'fas fa-crown',
                'description': 'Luxury villas and premium homes'
            },
            {
                'name': 'Office Space',
                'icon': 'fas fa-briefcase',
                'description': 'Office suites and business spaces'
            },
            {
                'name': 'Warehouse',
                'icon': 'fas fa-warehouse',
                'description': 'Warehouses and storage facilities'
            },
            {
                'name': 'Shop',
                'icon': 'fas fa-shop',
                'description': 'Retail shops and kiosks'
            },
            {
                'name': 'Townhouse',
                'icon': 'fas fa-objects-column',
                'description': 'Townhouses and row houses'
            },
            {
                'name': 'Bungalow',
                'icon': 'fas fa-house',
                'description': 'Single-story bungalow homes'
            },
            {
                'name': 'Penthouse',
                'icon': 'fas fa-star',
                'description': 'Luxury penthouse apartments'
            },
            {
                'name': 'Room/Bedsit',
                'icon': 'fas fa-bed',
                'description': 'Individual rooms and bedsits'
            },
            {
                'name': 'Guest House',
                'icon': 'fas fa-door-open',
                'description': 'Guest houses and serviced rooms'
            },
            {
                'name': 'Shared Apartment',
                'icon': 'fas fa-users',
                'description': 'Shared apartments and co-living spaces'
            },
        ]

        created_count = 0
        for cat_data in categories:
            category, created = PropertyCategory.objects.get_or_create(
                name=cat_data['name'],
                defaults={
                    'slug': cat_data['name'].lower().replace(' ', '-'),
                    'icon': cat_data['icon'],
                    'description': cat_data['description']
                }
            )
            if created:
                self.stdout.write(
                    self.style.SUCCESS(f'✓ Created: {category.name}')
                )
                created_count += 1
            else:
                self.stdout.write(f'  Already exists: {category.name}')

        self.stdout.write(
            self.style.SUCCESS(f'\n✅ Total created: {created_count} categories')
        )
        total = PropertyCategory.objects.count()
        self.stdout.write(f'📊 Total categories in database: {total}')
