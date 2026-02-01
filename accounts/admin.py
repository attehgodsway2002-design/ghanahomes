from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import User, VerificationRequest
from .audit_models import AuditLog, LoginHistory, PaymentAudit, PropertyEditHistory

class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = UserCreationForm.Meta.fields + ("email", "user_type", "phone")

class CustomUserChangeForm(UserChangeForm):
    class Meta(UserChangeForm.Meta):
        model = User
        fields = UserChangeForm.Meta.fields

@admin.register(User)
class CustomUserAdmin(BaseUserAdmin):
    form = CustomUserChangeForm
    add_form = CustomUserCreationForm
    list_display = [
        "username",
        "email",
        "user_type",
        "is_verified",
        "phone",
        "created_at",
    ]
    list_filter = ["user_type", "is_verified", "is_staff", "created_at"]
    search_fields = ["username", "email", "phone", "company_name"]
    ordering = ["-created_at"]
    actions = [
        "verify_users",
        "unverify_users",
        "enable_email_notifications",
        "disable_email_notifications",
    ]

    def verify_users(self, request, queryset):
        queryset.update(is_verified=True)

    verify_users.short_description = "Verify selected users"

    def unverify_users(self, request, queryset):
        queryset.update(is_verified=False)

    unverify_users.short_description = "Remove verification from selected users"

    def enable_email_notifications(self, request, queryset):
        queryset.update(email_notifications=True)

    enable_email_notifications.short_description = "Enable email notifications for selected users"

    def disable_email_notifications(self, request, queryset):
        queryset.update(email_notifications=False)

    disable_email_notifications.short_description = "Disable email notifications for selected users"

    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        (
            "User Type",
            {
                "classes": ("wide",),
                "fields": ("user_type", "phone", "email"),
            },
        ),
    )

    fieldsets = (
        (None, {"fields": ("username", "password")}),
        ("Personal info", {"fields": ("first_name", "last_name", "email", "phone")}),
        (
            "Profile",
            {
                "fields": (
                    "user_type",
                    "profile_picture",
                    "bio",
                    "address",
                    "city",
                    "region",
                )
            },
        ),
        (
            "Business",
            {
                "fields": (
                    "company_name",
                    "license_number",
                    "is_verified",
                    "verification_document",
                ),
                "classes": ("collapse",),
            },
        ),
        (
            "Social Media",
            {"fields": ("whatsapp", "facebook", "instagram"), "classes": ("collapse",)},
        ),
        ("Preferences", {"fields": ("email_notifications", "sms_notifications")}),
        (
            "Permissions",
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                ),
                "classes": ("collapse",),
            },
        ),
        ("Important dates", {"fields": ("last_login", "date_joined")}),
    )


# Audit Log Admin
@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ['action', 'user', 'object_repr', 'timestamp']
    list_filter = ['action', 'timestamp', 'user']
    search_fields = ['user__username', 'object_repr', 'ip_address']
    readonly_fields = ['user', 'action', 'object_repr', 'old_values', 'new_values', 'timestamp']
    
    def has_add_permission(self, request):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser


@admin.register(LoginHistory)
class LoginHistoryAdmin(admin.ModelAdmin):
    list_display = ['user', 'ip_address', 'login_at', 'logout_at', 'is_active']
    list_filter = ['is_active', 'login_at']
    search_fields = ['user__username', 'ip_address']
    readonly_fields = ['user', 'ip_address', 'user_agent', 'login_at', 'logout_at']
    
    def has_add_permission(self, request):
        return False


@admin.register(PaymentAudit)
class PaymentAuditAdmin(admin.ModelAdmin):
    list_display = ['payment', 'event', 'old_status', 'new_status', 'created_at']
    list_filter = ['event', 'created_at']
    search_fields = ['payment__id', 'reference_code']
    readonly_fields = ['payment', 'event', 'details', 'created_at']
    
    def has_add_permission(self, request):
        return False


@admin.register(PropertyEditHistory)
class PropertyEditHistoryAdmin(admin.ModelAdmin):
    list_display = ['property', 'user', 'edited_at']
    list_filter = ['edited_at', 'user']
    search_fields = ['property__title', 'user__username']
    readonly_fields = ['property', 'user', 'old_values', 'new_values', 'edited_at']
    
    def has_add_permission(self, request):
        return False


@admin.register(VerificationRequest)
class VerificationRequestAdmin(admin.ModelAdmin):
    list_display = ['user', 'status', 'created_at', 'reviewed_at', 'reviewed_by']
    list_filter = ['status', 'created_at', 'reviewed_at']
    search_fields = ['user__username', 'user__email', 'license_number']
    readonly_fields = ['user', 'created_at', 'updated_at', 'reviewed_at', 'reviewed_by', 'verification_document']
    actions = ['approve_verification', 'decline_verification']
    
    fieldsets = (
        (None, {
            'fields': ('user', 'license_number', 'verification_document', 'status')
        }),
        ('Review Information', {
            'fields': ('reviewed_by', 'reviewed_at', 'decline_reason'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def approve_verification(self, request, queryset):
        """Approve selected verification requests"""
        count = 0
        for verification_request in queryset.filter(status='pending'):
            verification_request.approve(request.user)
            count += 1
        
        self.message_user(request, f'{count} verification request(s) approved.')
    
    approve_verification.short_description = "✓ Approve selected verification requests"
    
    def decline_verification(self, request, queryset):
        """Decline selected verification requests (requires reason)"""
        # For now, show a message to use the change form to add a reason
        pending_count = queryset.filter(status='pending').count()
        if pending_count == 0:
            self.message_user(request, 'No pending verification requests selected.')
        else:
            self.message_user(request, f'Please edit each request individually to add a decline reason, then update the status to "Declined".')
    
    decline_verification.short_description = "✗ Decline selected verification requests"
    
    def get_readonly_fields(self, request, obj=None):
        """Make status/decline_reason editable only for pending requests"""
        readonly = list(self.readonly_fields)
        if obj and obj.status != 'pending':
            readonly.extend(['status', 'decline_reason'])
        return readonly
    
    def has_add_permission(self, request):
        return False