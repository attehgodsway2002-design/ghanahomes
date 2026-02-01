#!/usr/bin/env python
"""
Verification script to ensure all models are properly registered in Django admin
and all admin configurations are working correctly.
"""
import os
import django
import sys

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ghanahomes.settings')
django.setup()

from django.contrib import admin
from accounts.models import User, AuditLog, LoginHistory, PaymentAudit, PropertyEditHistory
from properties.models import Property, PropertyCategory, PropertyImage, PropertyVideo, Favorite, PropertyView, PropertyReview
from subscriptions.models import Subscription, SubscriptionPlan
from payments.models import Payment
from chat.models import ChatRoom, Message

def verify_admin_registration():
    """Verify all models are registered in admin"""
    print("=" * 80)
    print("DJANGO ADMIN REGISTRATION VERIFICATION")
    print("=" * 80)
    
    admin_site = admin.site
    registered_models = admin_site._registry.keys()
    
    models_to_check = [
        # Accounts
        (User, 'Accounts'),
        (AuditLog, 'Accounts'),
        (LoginHistory, 'Accounts'),
        (PaymentAudit, 'Accounts'),
        (PropertyEditHistory, 'Accounts'),
        # Properties
        (Property, 'Properties'),
        (PropertyCategory, 'Properties'),
        (PropertyImage, 'Properties'),
        (PropertyVideo, 'Properties'),
        (Favorite, 'Properties'),
        (PropertyView, 'Properties'),
        (PropertyReview, 'Properties'),
        # Subscriptions
        (Subscription, 'Subscriptions'),
        (SubscriptionPlan, 'Subscriptions'),
        # Payments
        (Payment, 'Payments'),
        # Chat
        (ChatRoom, 'Chat'),
        (Message, 'Chat'),
    ]
    
    app_sections = {}
    all_registered = True
    
    for model, app in models_to_check:
        is_registered = model in registered_models
        status = "✓ REGISTERED" if is_registered else "✗ NOT REGISTERED"
        
        if app not in app_sections:
            app_sections[app] = []
        
        app_sections[app].append({
            'model': model.__name__,
            'registered': is_registered,
            'status': status
        })
        
        if not is_registered:
            all_registered = False
    
    # Print by app section
    for app in ['Accounts', 'Properties', 'Subscriptions', 'Payments', 'Chat']:
        print(f"\n📦 {app}")
        print("-" * 80)
        for item in app_sections[app]:
            print(f"  {item['status']:20} {item['model']}")
    
    print("\n" + "=" * 80)
    if all_registered:
        print("✓ SUCCESS: All models are registered in Django admin!")
    else:
        print("✗ ERROR: Some models are not registered!")
        sys.exit(1)
    
    # Check admin configurations
    print("\n📋 ADMIN CONFIGURATIONS")
    print("=" * 80)
    
    checks = {
        'list_display': [],
        'list_filter': [],
        'search_fields': [],
        'readonly_fields': [],
        'fieldsets': [],
        'actions': [],
    }
    
    for model in registered_models:
        model_admin = admin_site._registry[model]
        
        # Check for common admin features
        if hasattr(model_admin, 'list_display') and model_admin.list_display:
            checks['list_display'].append(model.__name__)
        if hasattr(model_admin, 'list_filter') and model_admin.list_filter:
            checks['list_filter'].append(model.__name__)
        if hasattr(model_admin, 'search_fields') and model_admin.search_fields:
            checks['search_fields'].append(model.__name__)
        if hasattr(model_admin, 'readonly_fields') and model_admin.readonly_fields:
            checks['readonly_fields'].append(model.__name__)
        if hasattr(model_admin, 'fieldsets') and model_admin.fieldsets:
            checks['fieldsets'].append(model.__name__)
        if hasattr(model_admin, 'actions') and model_admin.actions:
            checks['actions'].append(model.__name__)
    
    # Print summary
    print(f"\n✓ Models with list_display: {len(checks['list_display'])}")
    print(f"✓ Models with list_filter: {len(checks['list_filter'])}")
    print(f"✓ Models with search_fields: {len(checks['search_fields'])}")
    print(f"✓ Models with readonly_fields: {len(checks['readonly_fields'])}")
    print(f"✓ Models with fieldsets: {len(checks['fieldsets'])}")
    print(f"✓ Models with custom actions: {len(checks['actions'])}")
    
    print("\n" + "=" * 80)
    print("✓ ADMIN VERIFICATION COMPLETE")
    print("=" * 80)
    
    # Provide summary statistics
    total_models = len(registered_models)
    total_checks_passed = sum(len(v) for v in checks.values())
    
    print(f"\n📊 SUMMARY")
    print(f"  Total Registered Models: {total_models}")
    print(f"  Total Admin Features Configured: {total_checks_passed}")
    print(f"  Average Features per Model: {total_checks_passed / total_models:.1f}")
    
    return all_registered

if __name__ == '__main__':
    try:
        success = verify_admin_registration()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n✗ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
