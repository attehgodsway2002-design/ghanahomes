from django.contrib import admin
from django.utils.html import format_html
from .models import PropertyCategory, PropertyType, Property, PropertyImage, PropertyVideo, Favorite, PropertyView, PropertyReview

@admin.register(PropertyCategory)
class PropertyCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'icon', 'property_count']
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ['name', 'description']
    list_per_page = 50
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'slug', 'icon')
        }),
        ('Description', {
            'fields': ('description',)
        }),
    )
    
    def property_count(self, obj):
        count = obj.properties.count()
        return format_html('<span style="color: #417690; font-weight: bold;">{}</span>', count)
    property_count.short_description = 'Properties'


@admin.register(PropertyType)
class PropertyTypeAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'icon']
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ['name', 'description']
    list_per_page = 50
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'slug', 'icon')
        }),
        ('Description', {
            'fields': ('description',)
        }),
    )



class PropertyImageInline(admin.TabularInline):
    model = PropertyImage
    extra = 1
    fields = ['image', 'caption', 'is_primary', 'order']


class PropertyVideoInline(admin.TabularInline):
    model = PropertyVideo
    extra = 0
    fields = ['video', 'thumbnail', 'title']


@admin.register(Property)
class PropertyAdmin(admin.ModelAdmin):
    list_display = ['title_link', 'owner', 'property_type', 'city', 'price_display', 'status_badge', 'featured_badge', 'views', 'created_at']
    list_filter = ['property_type', 'status', 'is_featured', 'is_verified', 'region', 'furnishing', 'created_at']
    search_fields = ['title', 'description', 'address', 'city', 'owner__username', 'area']
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ['views', 'favorites_count', 'created_at', 'updated_at']
    date_hierarchy = 'created_at'
    raw_id_fields = ['owner']
    autocomplete_fields = ['category']
    save_on_top = True
    list_per_page = 50
    inlines = [PropertyImageInline, PropertyVideoInline]
    actions = ['make_featured', 'make_unfeatured', 'verify_properties', 'mark_as_available', 'mark_as_rented', 'mark_as_pending']

    def make_featured(self, request, queryset):
        updated = queryset.update(is_featured=True)
        self.message_user(request, f'{updated} properties marked as featured')
    make_featured.short_description = "⭐ Mark selected properties as featured"

    def make_unfeatured(self, request, queryset):
        updated = queryset.update(is_featured=False)
        self.message_user(request, f'{updated} properties removed from featured')
    make_unfeatured.short_description = "Remove featured status from selected properties"

    def verify_properties(self, request, queryset):
        updated = queryset.update(is_verified=True)
        self.message_user(request, f'{updated} properties verified')
    verify_properties.short_description = "✓ Verify selected properties"

    def mark_as_available(self, request, queryset):
        updated = queryset.update(status='available')
        self.message_user(request, f'{updated} properties marked as available')
    mark_as_available.short_description = "Mark as available"

    def mark_as_rented(self, request, queryset):
        updated = queryset.update(status='rented')
        self.message_user(request, f'{updated} properties marked as rented')
    mark_as_rented.short_description = "Mark as rented"
    
    def mark_as_pending(self, request, queryset):
        updated = queryset.update(status='pending')
        self.message_user(request, f'{updated} properties marked as pending')
    mark_as_pending.short_description = "Mark as pending"
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'slug', 'description', 'property_type', 'category', 'owner')
        }),
        ('Location', {
            'fields': ('region', 'city', 'area', 'address', 'location', 'latitude', 'longitude'),
            'classes': ('collapse',)
        }),
        ('Pricing', {
            'fields': ('price', 'currency', 'negotiable')
        }),
        ('Property Details', {
            'fields': ('bedrooms', 'bathrooms', 'size', 'furnishing')
        }),
        ('Amenities', {
            'fields': ('parking', 'security', 'swimming_pool', 'gym', 'garden', 'balcony', 'wifi', 'air_conditioning'),
            'classes': ('collapse',),
            'description': 'Select which amenities are available at this property'
        }),
        ('Status & Features', {
            'fields': ('status', 'is_featured', 'is_verified'),
            'classes': ('wide',)
        }),
        ('Statistics', {
            'fields': ('views', 'favorites_count', 'created_at', 'updated_at', 'published_at'),
            'classes': ('collapse',)
        }),
    )
    
    def title_link(self, obj):
        url = obj.get_absolute_url()
        return format_html('<a href="{}" target="_blank"><strong>{}</strong></a>', url, obj.title[:50])
    title_link.short_description = 'Title'
    
    def status_badge(self, obj):
        colors = {
            'available': '#28a745',
            'rented': '#ffc107',
            'pending': '#6c757d',
            'unavailable': '#dc3545'
        }
        color = colors.get(obj.status, '#6c757d')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; border-radius: 3px; font-weight: bold;">{}</span>',
            color, obj.get_status_display()
        )
    status_badge.short_description = 'Status'
    
    def featured_badge(self, obj):
        if obj.is_featured:
            return format_html('<span style="color: #ffc107; font-size: 18px;">⭐</span>')
        return '-'
    featured_badge.short_description = 'Featured'
    
    def price_display(self, obj):
        return format_html('{}{}', obj.currency, obj.price)
    price_display.short_description = 'Price'


@admin.register(PropertyImage)
class PropertyImageAdmin(admin.ModelAdmin):
    list_display = ['property', 'image_preview', 'is_primary', 'order', 'uploaded_at']
    list_filter = ['is_primary', 'uploaded_at', 'property']
    search_fields = ['property__title', 'caption']
    list_editable = ['order', 'is_primary']
    readonly_fields = ['image_preview', 'uploaded_at']
    list_per_page = 50
    raw_id_fields = ['property']
    
    fieldsets = (
        ('Image Information', {
            'fields': ('property', 'image', 'image_preview')
        }),
        ('Details', {
            'fields': ('caption', 'is_primary', 'order')
        }),
        ('Metadata', {
            'fields': ('uploaded_at',),
            'classes': ('collapse',)
        }),
    )
    
    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="max-width: 200px; max-height: 200px;" />', obj.image.url)
        return '-'
    image_preview.short_description = 'Preview'


@admin.register(PropertyVideo)
class PropertyVideoAdmin(admin.ModelAdmin):
    list_display = ['property', 'title', 'duration_display', 'uploaded_at']
    list_filter = ['uploaded_at', 'property']
    search_fields = ['property__title', 'title']
    readonly_fields = ['uploaded_at', 'duration_display']
    list_per_page = 50
    raw_id_fields = ['property']
    
    fieldsets = (
        ('Video Information', {
            'fields': ('property', 'video', 'thumbnail', 'title')
        }),
        ('Details', {
            'fields': ('duration', 'duration_display')
        }),
        ('Metadata', {
            'fields': ('uploaded_at',),
            'classes': ('collapse',)
        }),
    )
    
    def duration_display(self, obj):
        minutes = obj.duration // 60
        seconds = obj.duration % 60
        return f"{minutes}m {seconds}s" if obj.duration > 0 else '-'
    duration_display.short_description = 'Duration (readable)'


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ['user', 'property_link', 'created_at']
    list_filter = ['created_at', 'property__property_type']
    search_fields = ['user__username', 'property__title']
    raw_id_fields = ['user', 'property']
    date_hierarchy = 'created_at'
    list_per_page = 50
    readonly_fields = ['created_at']
    
    fieldsets = (
        ('Favorite Information', {
            'fields': ('user', 'property')
        }),
        ('Metadata', {
            'fields': ('created_at',)
        }),
    )
    
    def property_link(self, obj):
        return format_html('<a href="{}">{}</a>', obj.property.get_absolute_url(), obj.property.title[:50])
    property_link.short_description = 'Property'


@admin.register(PropertyView)
class PropertyViewAdmin(admin.ModelAdmin):
    list_display = ['property_link', 'user', 'ip_address', 'viewed_at']
    list_filter = ['viewed_at', 'property__property_type']
    search_fields = ['property__title', 'user__username', 'ip_address']
    raw_id_fields = ['property', 'user']
    date_hierarchy = 'viewed_at'
    list_per_page = 50
    readonly_fields = ['property', 'user', 'ip_address', 'viewed_at']
    
    fieldsets = (
        ('View Information', {
            'fields': ('property', 'user', 'ip_address')
        }),
        ('Metadata', {
            'fields': ('viewed_at',)
        }),
    )
    
    def has_add_permission(self, request):
        return False
    
    def property_link(self, obj):
        return format_html('<a href="{}">{}</a>', obj.property.get_absolute_url(), obj.property.title[:50])
    property_link.short_description = 'Property'


@admin.register(PropertyReview)
class PropertyReviewAdmin(admin.ModelAdmin):
    list_display = ['property_link', 'user', 'rating_display', 'created_at']
    list_filter = ['rating', 'created_at', 'property__property_type']
    search_fields = ['property__title', 'user__username', 'comment']
    raw_id_fields = ['property', 'user']
    date_hierarchy = 'created_at'
    list_per_page = 50
    readonly_fields = ['created_at', 'rating_display']
    
    fieldsets = (
        ('Review Information', {
            'fields': ('property', 'user', 'rating', 'rating_display')
        }),
        ('Comment', {
            'fields': ('comment',)
        }),
        ('Metadata', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    
    def rating_display(self, obj):
        stars = '⭐' * obj.rating + '☆' * (5 - obj.rating)
        return format_html('<span style="font-size: 16px;">{} ({})</span>', stars, obj.rating)
    rating_display.short_description = 'Rating'
    
    def property_link(self, obj):
        return format_html('<a href="{}">{}</a>', obj.property.get_absolute_url(), obj.property.title[:50])
    property_link.short_description = 'Property'
