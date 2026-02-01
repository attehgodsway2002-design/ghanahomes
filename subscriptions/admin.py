from django.contrib import admin
from django.utils.html import format_html
from django.utils import timezone
from datetime import timedelta
from .models import SubscriptionPlan, Subscription

@admin.register(SubscriptionPlan)
class SubscriptionPlanAdmin(admin.ModelAdmin):
    list_display = ['name', 'plan_type_badge', 'price_display', 'property_limit', 'featured_listings', 'active_badge']
    list_filter = ['plan_type', 'is_free', 'is_active']
    save_as = True
    ordering = ['is_free', 'price_monthly']
    search_fields = ['name', 'description']
    list_per_page = 50
    
    fieldsets = (
        ('Plan Information', {
            'fields': ('name', 'plan_type', 'description', 'is_free', 'is_active')
        }),
        ('Pricing', {
            'fields': ('price_monthly', 'price_quarterly', 'price_yearly')
        }),
        ('Property Limits', {
            'fields': ('property_limit', 'photo_limit', 'video_limit', 'featured_listings')
        }),
        ('Features', {
            'fields': ('priority_support', 'analytics', 'verified_badge', 'social_media_promotion'),
            'description': 'Premium features included in this plan'
        }),
    )
    
    readonly_fields = []
    
    def price_display(self, obj):
        if obj.is_free:
            return format_html('<span style="color: #28a745; font-weight: bold;">FREE</span>')
        return format_html('₵{}<br/><small style="color: #6c757d;">₵{}/qtr | ₵{}/yr</small>', 
                          obj.price_monthly, obj.price_quarterly, obj.price_yearly)
    price_display.short_description = "Pricing"
    
    def plan_type_badge(self, obj):
        colors = {'basic': '#17a2b8', 'premium': '#007bff', 'enterprise': '#6f42c1'}
        color = colors.get(obj.plan_type, '#6c757d')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; border-radius: 3px; font-weight: bold;">{}</span>',
            color, obj.get_plan_type_display()
        )
    plan_type_badge.short_description = "Plan Type"
    
    def active_badge(self, obj):
        if obj.is_active:
            return format_html('<span style="color: #28a745;">✓ Active</span>')
        return format_html('<span style="color: #dc3545;">✗ Inactive</span>')
    active_badge.short_description = "Status"


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ['user_link', 'plan', 'duration', 'start_date', 'end_date_display', 'status_badge', 'property_count']
    list_filter = ['status', 'duration', 'plan', 'start_date', 'plan__plan_type']
    search_fields = ['user__username', 'user__email', 'plan__name']
    readonly_fields = ['created_at', 'updated_at', 'days_remaining']
    actions = ['extend_subscription_month', 'cancel_subscription', 'reactivate_subscription']
    date_hierarchy = 'start_date'
    save_on_top = True
    list_per_page = 50
    raw_id_fields = ['user']
    autocomplete_fields = ['plan']
    
    fieldsets = (
        ('Subscription Information', {
            'fields': ('user', 'plan', 'status')
        }),
        ('Duration', {
            'fields': ('duration', 'start_date', 'end_date', 'days_remaining')
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def extend_subscription_month(self, request, queryset):
        count = 0
        for subscription in queryset:
            if subscription.end_date > timezone.now():
                subscription.end_date += timedelta(days=30)
            else:
                subscription.end_date = timezone.now() + timedelta(days=30)
                subscription.status = 'active'
            subscription.save()
            count += 1
        self.message_user(request, f'{count} subscriptions extended by 1 month')
    extend_subscription_month.short_description = "⏱ Extend selected subscriptions by 1 month"

    def cancel_subscription(self, request, queryset):
        updated = queryset.update(status='cancelled')
        self.message_user(request, f'{updated} subscriptions cancelled')
    cancel_subscription.short_description = "❌ Cancel selected subscriptions"

    def reactivate_subscription(self, request, queryset):
        updated = queryset.update(status='active')
        self.message_user(request, f'{updated} subscriptions reactivated')
    reactivate_subscription.short_description = "✓ Reactivate selected subscriptions"
    
    def user_link(self, obj):
        from django.urls import reverse
        url = reverse('admin:accounts_user_change', args=[obj.user.id])
        return format_html('<a href="{}">{}</a>', url, obj.user.username)
    user_link.short_description = 'User'
    
    def status_badge(self, obj):
        colors = {'active': '#28a745', 'cancelled': '#dc3545', 'expired': '#ffc107', 'pending': '#6c757d'}
        color = colors.get(obj.status, '#6c757d')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; border-radius: 3px; font-weight: bold;">{}</span>',
            color, obj.get_status_display()
        )
    status_badge.short_description = "Status"
    
    def end_date_display(self, obj):
        days_left = (obj.end_date - timezone.now()).days
        if days_left < 0:
            return format_html('<span style="color: #dc3545; font-weight: bold;">EXPIRED</span>')
        elif days_left < 7:
            return format_html('<span style="color: #ffc107; font-weight: bold;">{} days left</span>', days_left)
        return format_html('{} ({} days)', obj.end_date.strftime('%Y-%m-%d'), days_left)
    end_date_display.short_description = "End Date"
    
    def days_remaining(self, obj):
        days = (obj.end_date - timezone.now()).days
        return max(0, days)
    days_remaining.short_description = "Days Remaining"

