from django.contrib import admin
from django.utils.html import format_html
from django.utils import timezone
from .models import Payment

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['payment_id', 'user_link', 'amount_display', 'payment_method_badge', 'status_badge', 'created_at']
    list_filter = ['payment_method', 'status', 'currency', 'created_at']
    search_fields = ['user__username', 'user__email', 'paystack_reference', 'id']
    readonly_fields = ['paystack_reference', 'paystack_access_code', 'created_at', 'updated_at']
    raw_id_fields = ['user', 'subscription']
    date_hierarchy = 'created_at'
    list_per_page = 50
    save_on_top = True
    
    actions = ['mark_as_successful', 'mark_as_failed', 'mark_as_pending']
    
    fieldsets = (
        ('Payment Information', {
            'fields': ('user', 'subscription', 'amount', 'currency', 'payment_method')
        }),
        ('Transaction Details', {
            'fields': ('paystack_reference', 'paystack_access_code', 'status')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def mark_as_successful(self, request, queryset):
        updated = queryset.update(status='successful')
        self.message_user(request, f'{updated} payments marked as successful')
    mark_as_successful.short_description = "✓ Mark selected payments as successful"

    def mark_as_failed(self, request, queryset):
        updated = queryset.update(status='failed')
        self.message_user(request, f'{updated} payments marked as failed')
    mark_as_failed.short_description = "❌ Mark selected payments as failed"

    def mark_as_pending(self, request, queryset):
        updated = queryset.update(status='pending')
        self.message_user(request, f'{updated} payments marked as pending')
    mark_as_pending.short_description = "⏱ Mark selected payments as pending"
    
    def payment_id(self, obj):
        return format_html('<code style="background-color: #f0f0f0; padding: 2px 5px;">{}</code>', str(obj.id)[:12])
    payment_id.short_description = 'Payment ID'
    
    def user_link(self, obj):
        from django.urls import reverse
        url = reverse('admin:accounts_user_change', args=[obj.user.id])
        return format_html('<a href="{}">{}</a>', url, obj.user.username)
    user_link.short_description = 'User'
    
    def amount_display(self, obj):
        return format_html('{}{}', obj.currency, obj.amount)
    amount_display.short_description = 'Amount'
    
    def status_badge(self, obj):
        colors = {'successful': '#28a745', 'failed': '#dc3545', 'pending': '#ffc107'}
        color = colors.get(obj.status, '#6c757d')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; border-radius: 3px; font-weight: bold;">{}</span>',
            color, obj.get_status_display()
        )
    status_badge.short_description = "Status"
    
    def payment_method_badge(self, obj):
        colors = {'paystack': '#4636eb', 'momo': '#ff6900', 'card': '#1f1f1f'}
        color = colors.get(obj.payment_method, '#6c757d')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; border-radius: 3px;">{}</span>',
            color, obj.get_payment_method_display()
        )
    payment_method_badge.short_description = "Method"

