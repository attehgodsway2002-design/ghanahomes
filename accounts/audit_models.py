"""
Audit logging models for tracking changes to critical entities
"""
from django.db import models
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
import json


class AuditLog(models.Model):
    """
    Centralized audit log for tracking all changes to critical models.
    
    Fields:
        - user: User who made the change (null for system actions)
        - action: Type of action (CREATE, UPDATE, DELETE, LOGIN, PAYMENT)
        - content_type: Django content type of the modified object
        - object_id: ID of the modified object
        - content_object: Generic reference to the modified object
        - object_repr: String representation of object
        - old_values: JSON dict of previous field values (for updates)
        - new_values: JSON dict of new field values
        - ip_address: IP address of the requester
        - timestamp: When the action occurred
    """
    
    ACTION_CHOICES = (
        ('CREATE', 'Created'),
        ('UPDATE', 'Updated'),
        ('DELETE', 'Deleted'),
        ('LOGIN', 'Login'),
        ('LOGOUT', 'Logout'),
        ('PAYMENT_INITIATED', 'Payment Initiated'),
        ('PAYMENT_COMPLETED', 'Payment Completed'),
        ('PAYMENT_FAILED', 'Payment Failed'),
        ('SUBSCRIPTION_ACTIVATED', 'Subscription Activated'),
        ('SUBSCRIPTION_CANCELLED', 'Subscription Cancelled'),
        ('PASSWORD_CHANGED', 'Password Changed'),
        ('EMAIL_VERIFIED', 'Email Verified'),
        ('VERIFICATION_REQUESTED', 'Verification Requested'),
        ('ADMIN_ACTION', 'Admin Action'),
    )
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='audit_logs'
    )
    action = models.CharField(max_length=30, choices=ACTION_CHOICES)
    
    # Generic relation to any model
    content_type = models.ForeignKey(ContentType, on_delete=models.SET_NULL, null=True, blank=True)
    object_id = models.CharField(max_length=255, blank=True)
    content_object = GenericForeignKey('content_type', 'object_id')
    object_repr = models.CharField(max_length=500, blank=True)
    
    # Change tracking
    old_values = models.JSONField(default=dict, blank=True)
    new_values = models.JSONField(default=dict, blank=True)
    
    # Request info
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True, null=True)
    
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)
    
    class Meta:
        ordering = ['-timestamp']
        verbose_name = 'Audit Log'
        verbose_name_plural = 'Audit Logs'
        indexes = [
            models.Index(fields=['user', '-timestamp']),
            models.Index(fields=['action', '-timestamp']),
            models.Index(fields=['content_type', 'object_id']),
        ]
    
    def __str__(self):
        return f"{self.action} - {self.object_repr} by {self.user or 'System'} at {self.timestamp}"
    
    def get_changes(self):
        """Return dict of field changes (old -> new)"""
        changes = {}
        if self.old_values and self.new_values:
            for key in self.new_values:
                if key in self.old_values and self.old_values[key] != self.new_values[key]:
                    changes[key] = {
                        'old': self.old_values[key],
                        'new': self.new_values[key]
                    }
        return changes


class LoginHistory(models.Model):
    """Track user login/logout history"""
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='login_history')
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField()
    login_at = models.DateTimeField(auto_now_add=True)
    logout_at = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['-login_at']
        indexes = [
            models.Index(fields=['user', '-login_at']),
            models.Index(fields=['is_active', '-login_at']),
        ]
    
    def __str__(self):
        return f"{self.user.username} logged in from {self.ip_address} at {self.login_at}"
    
    @property
    def session_duration(self):
        """Return session duration in seconds"""
        if self.logout_at:
            return (self.logout_at - self.login_at).total_seconds()
        return None


class PaymentAudit(models.Model):
    """Detailed tracking of payment changes and events"""
    
    EVENT_CHOICES = (
        ('INITIATED', 'Payment Initiated'),
        ('PENDING', 'Pending Verification'),
        ('VERIFIED', 'Verified'),
        ('COMPLETED', 'Completed'),
        ('FAILED', 'Failed'),
        ('CANCELLED', 'Cancelled'),
        ('REFUNDED', 'Refunded'),
        ('RETRY', 'Retry Attempted'),
        ('WEBHOOK', 'Webhook Received'),
    )
    
    payment = models.ForeignKey('payments.Payment', on_delete=models.CASCADE, related_name='audit_trail')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    event = models.CharField(max_length=30, choices=EVENT_CHOICES)
    
    old_status = models.CharField(max_length=20, blank=True, null=True)
    new_status = models.CharField(max_length=20, blank=True, null=True)
    
    amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    reference_code = models.CharField(max_length=255, blank=True)
    
    details = models.JSONField(default=dict, blank=True)  # Store any additional info
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Payment Audit'
        verbose_name_plural = 'Payment Audits'
        indexes = [
            models.Index(fields=['payment', '-created_at']),
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['event', '-created_at']),
        ]
    
    def __str__(self):
        return f"{self.event} - Payment {self.payment.id} at {self.created_at}"


class PropertyEditHistory(models.Model):
    """Track all edits to properties"""
    
    property = models.ForeignKey('properties.Property', on_delete=models.CASCADE, related_name='edit_history')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    
    # Changes
    old_values = models.JSONField(default=dict)
    new_values = models.JSONField(default=dict)
    
    # Metadata
    edited_at = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    
    class Meta:
        ordering = ['-edited_at']
        verbose_name = 'Property Edit History'
        verbose_name_plural = 'Property Edit Histories'
        indexes = [
            models.Index(fields=['property', '-edited_at']),
            models.Index(fields=['user', '-edited_at']),
        ]
    
    def __str__(self):
        return f"{self.property.title} edited by {self.user.username} at {self.edited_at}"
    
    def get_changes(self):
        """Return dict of field changes"""
        changes = {}
        for key in self.new_values:
            if key in self.old_values and self.old_values[key] != self.new_values[key]:
                changes[key] = {
                    'old': self.old_values[key],
                    'new': self.new_values[key]
                }
        return changes
