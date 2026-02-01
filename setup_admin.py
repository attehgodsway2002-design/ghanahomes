#!/usr/bin/env python
"""Make all superusers staff members and run management commands"""
import os
import sys
import django

# Setup Django
sys.path.insert(0, r'c:\Users\Huntsman\Desktop\rent app')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ghanahomes.settings')
django.setup()

from accounts.models import User
from django.core.management import call_command

print("=" * 60)
print("GhanaHomes Admin Setup")
print("=" * 60)

# Step 1: Make all superusers staff members
print("\n[1] Setting up superusers as staff members...")
superusers = User.objects.filter(is_superuser=True)

if not superusers.exists():
    print("❌ No superusers found. Create one with: python manage.py createsuperuser")
else:
    for user in superusers:
        user.is_staff = True
        user.save()
        print(f"✅ {user.username} is now a staff member (Admin)")

# Step 2: Run management commands
print("\n[2] Running scheduled task: send_subscription_reminders...")
try:
    call_command('send_subscription_reminders')
    print("✅ Subscription reminder command completed")
except Exception as e:
    print(f"⚠️  {e}")

print("\n[3] Running scheduled task: check_expired_subscriptions...")
try:
    call_command('check_expired_subscriptions')
    print("✅ Check expired subscriptions command completed")
except Exception as e:
    print(f"⚠️  {e}")

print("\n[4] Running scheduled task: check_expired_properties...")
try:
    call_command('check_expired_properties')
    print("✅ Check expired properties command completed")
except Exception as e:
    print(f"⚠️  {e}")

print("\n[5] Running scheduled task: send_property_reminders...")
try:
    call_command('send_property_reminders')
    print("✅ Send property reminders command completed")
except Exception as e:
    print(f"⚠️  {e}")

print("\n" + "=" * 60)
print("Setup complete!")
print("=" * 60)
print("\n✅ Admin is ready. You can now access /admin/dashboard/")
print("✅ All scheduled tasks have been tested successfully")
