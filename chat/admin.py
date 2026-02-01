from django.contrib import admin
from django.utils.html import format_html
from .models import ChatRoom, Message

@admin.register(ChatRoom)
class ChatRoomAdmin(admin.ModelAdmin):
    list_display = ['chat_id', 'property_link', 'tenant_link', 'landlord_link', 'message_count', 'created_at']
    list_filter = ['created_at', 'updated_at', 'property__property_type']
    search_fields = ['property__title', 'tenant__username', 'landlord__username', 'id']
    raw_id_fields = ['property', 'tenant', 'landlord']
    date_hierarchy = 'created_at'
    list_per_page = 50
    readonly_fields = ['created_at', 'updated_at', 'message_count']
    
    fieldsets = (
        ('Room Information', {
            'fields': ('property', 'tenant', 'landlord')
        }),
        ('Statistics', {
            'fields': ('message_count',)
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def chat_id(self, obj):
        return format_html('<code style="background-color: #f0f0f0; padding: 2px 5px;">{}</code>', str(obj.id)[:12])
    chat_id.short_description = 'Chat ID'
    
    def property_link(self, obj):
        from django.urls import reverse
        url = reverse('admin:properties_property_change', args=[obj.property.id])
        return format_html('<a href="{}">{}</a>', url, obj.property.title[:40])
    property_link.short_description = 'Property'
    
    def tenant_link(self, obj):
        from django.urls import reverse
        url = reverse('admin:accounts_user_change', args=[obj.tenant.id])
        return format_html('<a href="{}">{}</a>', url, obj.tenant.username)
    tenant_link.short_description = 'Tenant'
    
    def landlord_link(self, obj):
        from django.urls import reverse
        url = reverse('admin:accounts_user_change', args=[obj.landlord.id])
        return format_html('<a href="{}">{}</a>', url, obj.landlord.username)
    landlord_link.short_description = 'Landlord'
    
    def message_count(self, obj):
        count = obj.messages.count()
        return format_html('<span style="background-color: #007bff; color: white; padding: 3px 8px; border-radius: 3px; font-weight: bold;">{}</span>', count)
    message_count.short_description = 'Messages'


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ['message_id', 'chat_room_link', 'sender_link', 'content_preview', 'read_badge', 'created_at']
    list_filter = ['is_read', 'created_at', 'chat_room__property__property_type']
    search_fields = ['chat_room__property__title', 'sender__username', 'content', 'id']
    raw_id_fields = ['chat_room', 'sender']
    date_hierarchy = 'created_at'
    readonly_fields = ['created_at', 'id']
    list_per_page = 50
    save_on_top = True
    
    actions = ['mark_as_read', 'mark_as_unread']
    
    fieldsets = (
        ('Message Information', {
            'fields': ('chat_room', 'sender', 'content')
        }),
        ('Status', {
            'fields': ('is_read',)
        }),
        ('Metadata', {
            'fields': ('created_at', 'id'),
            'classes': ('collapse',)
        }),
    )

    def mark_as_read(self, request, queryset):
        updated = queryset.update(is_read=True)
        self.message_user(request, f'{updated} messages marked as read')
    mark_as_read.short_description = "✓ Mark selected messages as read"

    def mark_as_unread(self, request, queryset):
        updated = queryset.update(is_read=False)
        self.message_user(request, f'{updated} messages marked as unread')
    mark_as_unread.short_description = "◯ Mark selected messages as unread"
    
    def message_id(self, obj):
        return format_html('<code style="background-color: #f0f0f0; padding: 2px 5px;">{}</code>', str(obj.id)[:12])
    message_id.short_description = 'Message ID'
    
    def chat_room_link(self, obj):
        from django.urls import reverse
        url = reverse('admin:chat_chatroom_change', args=[obj.chat_room.id])
        return format_html('<a href="{}">{} → {}</a>', url, obj.chat_room.tenant.username[:15], obj.chat_room.landlord.username[:15])
    chat_room_link.short_description = 'Chat Room'
    
    def sender_link(self, obj):
        from django.urls import reverse
        url = reverse('admin:accounts_user_change', args=[obj.sender.id])
        return format_html('<a href="{}">{}</a>', url, obj.sender.username)
    sender_link.short_description = 'Sender'
    
    def content_preview(self, obj):
        preview = obj.content[:60] + '...' if len(obj.content) > 60 else obj.content
        return preview
    content_preview.short_description = 'Content'
    
    def read_badge(self, obj):
        if obj.is_read:
            return format_html('<span style="color: #6c757d;">✓ Read</span>')
        return format_html('<span style="color: #007bff; font-weight: bold;">◯ Unread</span>')
    read_badge.short_description = 'Status'

