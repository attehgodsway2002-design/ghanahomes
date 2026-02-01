from django.db import models
from django.conf import settings
from django.utils import timezone
from datetime import timedelta

class SubscriptionPlan(models.Model):
    PLAN_TYPE_CHOICES = (
        ('free', 'Free'),
        ('basic', 'Basic'),
        ('standard', 'Standard'),
        ('premium', 'Premium'),
        ('enterprise', 'Enterprise'),
    )
    
    DURATION_CHOICES = (
        ('monthly', 'Monthly'),
        ('quarterly', 'Quarterly'),
        ('yearly', 'Yearly'),
    )
    
    name = models.CharField(max_length=100)
    plan_type = models.CharField(max_length=20, choices=PLAN_TYPE_CHOICES, unique=True)
    description = models.TextField()
    price_monthly = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    price_quarterly = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    price_yearly = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    is_free = models.BooleanField(default=False, help_text="Mark as free tier plan")
    
    # Limits
    property_limit = models.IntegerField(help_text="Number of properties allowed")
    featured_listings = models.IntegerField(default=0)
    photo_limit = models.IntegerField(default=10)
    video_limit = models.IntegerField(default=0)
    
    # Features
    priority_support = models.BooleanField(default=False)
    analytics = models.BooleanField(default=False)
    verified_badge = models.BooleanField(default=False)
    social_media_promotion = models.BooleanField(default=False)
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['price_monthly']
    
    def __str__(self):
        if self.is_free:
            return f"{self.name} - Free"
        return f"{self.name} - ₵{self.price_monthly}/month"
    
    def get_price(self, duration='monthly'):
        prices = {
            'monthly': self.price_monthly,
            'quarterly': self.price_quarterly or self.price_monthly * 3,
            'yearly': self.price_yearly or self.price_monthly * 12,
        }
        return prices.get(duration, self.price_monthly)


class Subscription(models.Model):
    STATUS_CHOICES = (
        ('active', 'Active'),
        ('expired', 'Expired'),
        ('cancelled', 'Cancelled'),
        ('pending', 'Pending'),
    )
    
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='subscription')
    plan = models.ForeignKey(SubscriptionPlan, on_delete=models.SET_NULL, null=True)
    duration = models.CharField(max_length=20, default='monthly')
    
    start_date = models.DateTimeField(default=timezone.now)
    end_date = models.DateTimeField()
    
    property_count = models.IntegerField(default=0)
    featured_count = models.IntegerField(default=0)
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    auto_renew = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'status']),
            models.Index(fields=['status', '-created_at']),
            models.Index(fields=['end_date', 'status']),
            models.Index(fields=['plan', 'status']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.plan.name if self.plan else 'No Plan'}"
    
    def is_active(self):
        return self.status == 'active' and self.end_date > timezone.now()
    
    def can_add_property(self):
        if not self.is_active() or not self.plan:
            return False
        # Count actual properties instead of relying on counter
        actual_count = self.user.properties.filter(status='available').count()
        return actual_count < self.plan.property_limit
    
    def can_add_featured(self):
        return self.is_active() and self.featured_count < self.plan.featured_listings
