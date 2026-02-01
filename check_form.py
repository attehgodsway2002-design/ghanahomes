#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ghanahomes.settings')
django.setup()

from django.contrib.auth.forms import PasswordChangeForm
from accounts.models import User

# Check field names
print("PasswordChangeForm field names:")
print(PasswordChangeForm.base_fields.keys())
