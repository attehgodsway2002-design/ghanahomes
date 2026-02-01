from django.contrib.admin import AdminSite
from django.utils.translation import gettext_lazy as _

class GhanaHomesAdmin(AdminSite):
    # General admin site settings
    site_title = _('GhanaHomes Admin')
    site_header = _('GhanaHomes Administration')
    index_title = _('Site Administration')
    
    # Custom welcome message on admin index
    index_template = 'admin/custom_index.html'
    
    def each_context(self, request):
        context = super().each_context(request)
        context.update({
            'environment_name': 'Production' if not request.META.get('REMOTE_ADDR').startswith('127.0.0.1') else 'Development',
        })
        return context

# Create custom admin site instance
# Use the conventional 'admin' namespace so built-in admin URL reversing
# (e.g. 'admin:app_model_changelist') continues to work with templates
admin_site = GhanaHomesAdmin(name='admin')
# Optionally register app models with the custom admin site.
# Importing admin classes here allows the custom admin site to use the
# same ModelAdmin classes defined in each app's admin.py
try:
    # Accounts
    from accounts.models import User
    from accounts.admin import UserAdmin
    admin_site.register(User, UserAdmin)

    # Properties
    from properties.models import (
        PropertyCategory, Property, PropertyImage, PropertyVideo,
        Favorite, PropertyView, PropertyReview
    )
    from properties.admin import (
        PropertyCategoryAdmin, PropertyAdmin, PropertyImageAdmin,
        PropertyVideoAdmin, FavoriteAdmin, PropertyViewAdmin,
        PropertyReviewAdmin
    )
    admin_site.register(PropertyCategory, PropertyCategoryAdmin)
    admin_site.register(Property, PropertyAdmin)
    admin_site.register(PropertyImage, PropertyImageAdmin)
    admin_site.register(PropertyVideo, PropertyVideoAdmin)
    admin_site.register(Favorite, FavoriteAdmin)
    admin_site.register(PropertyView, PropertyViewAdmin)
    admin_site.register(PropertyReview, PropertyReviewAdmin)

    # Chat
    from chat.models import ChatRoom, Message
    from chat.admin import ChatRoomAdmin, MessageAdmin
    admin_site.register(ChatRoom, ChatRoomAdmin)
    admin_site.register(Message, MessageAdmin)

    # Subscriptions
    from subscriptions.models import SubscriptionPlan, Subscription
    from subscriptions.admin import SubscriptionPlanAdmin, SubscriptionAdmin
    admin_site.register(SubscriptionPlan, SubscriptionPlanAdmin)
    admin_site.register(Subscription, SubscriptionAdmin)

    # Payments
    from payments.models import Payment
    from payments.admin import PaymentAdmin
    admin_site.register(Payment, PaymentAdmin)
except Exception:
    # Avoid breaking imports during manage.py operations (migrations, etc.)
    pass