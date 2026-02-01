"""
Management command to create default property types
"""
from django.core.management.base import BaseCommand
from properties.models import PropertyType

class Command(BaseCommand):
    help = 'Create default property types'

    def handle(self, *args, **options):
        property_types = [
            {
                'name': 'Apartment',
                'icon': 'fas fa-building',
                'description': 'Modern apartments and flats'
            },
            {
                'name': 'House',
                'icon': 'fas fa-home',
                'description': 'Single family homes'
            },
            {
                'name': 'Villa',
                'icon': 'fas fa-crown',
                'description': 'Luxury villas and premium homes'
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
                'name': 'Commercial',
                'icon': 'fas fa-store',
                'description': 'Shops, offices and commercial spaces'
            },
            {
                'name': 'Office Space',
                'icon': 'fas fa-briefcase',
                'description': 'Office suites and business spaces'
            },
            {
                'name': 'Shop',
                'icon': 'fas fa-shop',
                'description': 'Retail shops and kiosks'
            },
            {
                'name': 'Warehouse',
                'icon': 'fas fa-warehouse',
                'description': 'Warehouses and storage facilities'
            },
            {
                'name': 'Land',
                'icon': 'fas fa-map',
                'description': 'Residential and commercial plots'
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
        for type_data in property_types:
            property_type, created = PropertyType.objects.get_or_create(
                name=type_data['name'],
                defaults={
                    'slug': type_data['name'].lower().replace(' ', '-').replace('/', '-'),
                    'icon': type_data['icon'],
                    'description': type_data['description'],
                }
            )
            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'✓ Created: {type_data["name"]}')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'- Already exists: {type_data["name"]}')
                )

        total_types = PropertyType.objects.count()
        self.stdout.write(
            self.style.SUCCESS(f'\n✅ Property Types Setup Complete!')
        )
        self.stdout.write(f'   Created: {created_count} new types')
        self.stdout.write(f'   Total: {total_types} property types in database')
