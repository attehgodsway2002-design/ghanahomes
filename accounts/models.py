from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import RegexValidator
from django.utils import timezone
from .audit_models import AuditLog, LoginHistory, PaymentAudit, PropertyEditHistory

class User(AbstractUser):
    USER_TYPE_CHOICES = (
        ('tenant', 'Tenant'),
        ('landlord', 'Landlord/Agent'),
    )
    
    user_type = models.CharField(max_length=20, choices=USER_TYPE_CHOICES, default='tenant')
    phone_regex = RegexValidator(regex=r'^\+?233?\d{9,10}$', message="Phone number must be in format: '+233XXXXXXXXX'")
    phone = models.CharField(validators=[phone_regex], max_length=15, blank=True)
    profile_picture = models.ImageField(upload_to='profiles/', blank=True, null=True)
    bio = models.TextField(blank=True)
    
    # For Landlords/Agents
    company_name = models.CharField(max_length=200, blank=True)
    license_number = models.CharField(max_length=100, blank=True)
    is_verified = models.BooleanField(default=False)
    verification_document = models.FileField(upload_to='verifications/', blank=True, null=True)
    
    # Location
    address = models.CharField(max_length=300, blank=True)
    city = models.CharField(max_length=100, blank=True)
    region = models.CharField(max_length=100, blank=True)
    
    # Social Media
    whatsapp = models.CharField(max_length=15, blank=True)
    facebook = models.URLField(blank=True)
    instagram = models.URLField(blank=True)
    
    # Preferences
    email_notifications = models.BooleanField(default=True)
    sms_notifications = models.BooleanField(default=False)
    # Presence
    last_seen = models.DateTimeField(null=True, blank=True, db_index=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user_type', '-created_at']),
            models.Index(fields=['is_verified']),
            models.Index(fields=['email']),
        ]
    
    def __str__(self):
        return f"{self.username} ({self.get_user_type_display()})"
    
    def is_landlord(self):
        return self.user_type == 'landlord'
    
    def is_tenant(self):
        return self.user_type == 'tenant'
    
    def get_full_name_or_username(self):
        full_name = f"{self.first_name} {self.last_name}".strip()
        return full_name if full_name else self.username


class VerificationRequest(models.Model):
    """
    Track user verification requests and their status.
    Allows admins to review, accept, or decline verification submissions.
    """
    
    STATUS_CHOICES = (
        ('pending', 'Pending Review'),
        ('approved', 'Approved'),
        ('declined', 'Declined'),
    )
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='verification_requests')
    license_number = models.CharField(max_length=100)
    verification_document = models.FileField(upload_to='verifications/')
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', db_index=True)
    
    # Review info
    reviewed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='verification_reviews')
    reviewed_at = models.DateTimeField(null=True, blank=True)
    decline_reason = models.TextField(blank=True, help_text='Reason for declining the verification request')
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status', '-created_at']),
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['status']),
        ]
    
    def __str__(self):
        return f"Verification Request - {self.user.username} ({self.get_status_display()})"
    
    def approve(self, reviewed_by_user):
        """Approve the verification request and update user status"""
        self.status = 'approved'
        self.reviewed_by = reviewed_by_user
        self.reviewed_at = timezone.now()
        self.save()
        
        # Update user's verification status
        self.user.is_verified = True
        self.user.license_number = self.license_number
        self.user.verification_document = self.verification_document
        self.user.save()
        
        # Log the action
        AuditLog.objects.create(
            user=reviewed_by_user,
            action='VERIFICATION_APPROVED',
            object_repr=f"Verification approved for {self.user.username}",
        )
    
    def decline(self, reviewed_by_user, reason=''):
        """Decline the verification request"""
        self.status = 'declined'
        self.reviewed_by = reviewed_by_user
        self.reviewed_at = timezone.now()
        self.decline_reason = reason
        self.save()
        
        # Log the action
        AuditLog.objects.create(
            user=reviewed_by_user,
            action='VERIFICATION_DECLINED',
            object_repr=f"Verification declined for {self.user.username}: {reason}",
        )
