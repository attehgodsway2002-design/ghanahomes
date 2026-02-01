#!/usr/bin/env python
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ghanahomes.settings')
django.setup()

from properties.models import Property
from django.contrib.auth import get_user_model

User = get_user_model()

print("--- Available Properties ---")
for prop in Property.objects.all():
    print(f"  Title: {prop.title}")
    print(f"  Slug: {prop.slug}")
    print(f"  Owner: {prop.owner.username}")
    print(f"  Category: {prop.category}")
    print()

print("--- Available Users ---")
for user in User.objects.all():
    print(f"  {user.username}")
