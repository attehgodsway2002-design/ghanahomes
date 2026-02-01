from django.contrib import admin
from django.contrib import admin as default_admin
from .admin import admin_site
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from . import admin_views

urlpatterns = [
    # Admin Dashboard Routes - MUST be before Django's admin() to avoid catch-all
    path('admin/dashboard/', admin_views.admin_dashboard, name='admin_dashboard'),
    path('admin/users/', admin_views.admin_users, name='admin_users'),
    path('admin/properties/', admin_views.admin_properties, name='admin_properties'),
    path('admin/payments/', admin_views.admin_payments, name='admin_payments'),
    path('admin/subscriptions/', admin_views.admin_subscriptions, name='admin_subscriptions'),
    path('admin/analytics/', admin_views.admin_analytics, name='admin_analytics'),
    
    # Admin Export Routes
    path('admin/export/users/', admin_views.export_users_csv, name='export_users_csv'),
    path('admin/export/properties/', admin_views.export_properties_csv, name='export_properties_csv'),
    path('admin/export/payments/', admin_views.export_payments_csv, name='export_payments_csv'),
    path('admin/export/subscriptions/', admin_views.export_subscriptions_csv, name='export_subscriptions_csv'),
    
    # Use the default admin site's URLs so decorators like @admin.register
    # in app admin modules (which register with the default site) resolve
    # correctly. If you prefer the custom AdminSite, ensure models are
    # explicitly registered to `admin_site`.
    path('admin/', default_admin.site.urls),
    
    path('', include('properties.urls')),
    path('accounts/', include('accounts.urls')),
    path('subscriptions/', include('subscriptions.urls')),
    path('payments/', include('payments.urls')),
    path('chat/', include('chat.urls')),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# Customize admin
