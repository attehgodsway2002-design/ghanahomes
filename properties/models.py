from django.db import models
from django.conf import settings
from django.utils.text import slugify
import uuid

class PropertyCategory(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True)
    icon = models.CharField(max_length=50, blank=True)  # Font Awesome icon class
    description = models.TextField(blank=True)
    
    class Meta:
        verbose_name_plural = "Property Categories"
        ordering = ['name']
    
    def __str__(self):
        return self.name


class PropertyType(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True)
    icon = models.CharField(max_length=50, blank=True)  # Font Awesome icon class
    description = models.TextField(blank=True)
    
    class Meta:
        verbose_name_plural = "Property Types"
        ordering = ['name']
    
    def __str__(self):
        return self.name


# Region choices
REGION_CHOICES = [
    ('greater-accra', 'Greater Accra'),
    ('ashanti', 'Ashanti'),
    ('western', 'Western'),
    ('eastern', 'Eastern'),
    ('central', 'Central'),
    ('northern', 'Northern'),
    ('upper-east', 'Upper East'),
    ('upper-west', 'Upper West'),
    ('volta', 'Volta'),
    ('bono', 'Bono'),
    ('bono-east', 'Bono East'),
    ('ahafo', 'Ahafo'),
    ('savannah', 'Savannah'),
    ('north-east', 'North East'),
    ('oti', 'Oti'),
    ('western-north', 'Western North'),
]


class Property(models.Model):
    PROPERTY_TYPE_CHOICES = (
        ('apartment', 'Apartment'),
        ('house', 'House'),
        ('villa', 'Villa'),
        ('duplex', 'Duplex'),
        ('studio', 'Studio'),
        ('commercial', 'Commercial'),
        ('office', 'Office Space'),
        ('shop', 'Shop'),
        ('warehouse', 'Warehouse'),
        ('land', 'Land'),
        ('townhouse', 'Townhouse'),
        ('bungalow', 'Bungalow'),
        ('penthouse', 'Penthouse'),
        ('room', 'Room/Bedsit'),
        ('guest-house', 'Guest House'),
        ('shared-apartment', 'Shared Apartment'),
    )
    
    FURNISHING_CHOICES = (
        ('unfurnished', 'Unfurnished'),
        ('semi-furnished', 'Semi-Furnished'),
        ('fully-furnished', 'Fully Furnished'),
    )
    
    STATUS_CHOICES = (
        ('available', 'Available'),
        ('rented', 'Rented'),
        ('pending', 'Pending'),
        ('unavailable', 'Unavailable'),
    )
    
    CURRENCY_CHOICES = (
        ('GHS', 'Ghana Cedis (GHS)'),
        ('USD', 'US Dollar (USD)'),
        ('EUR', 'Euro (EUR)'),
    )
    
    # Basic Info
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=300)
    slug = models.SlugField(max_length=350, unique=True, blank=True)
    description = models.TextField()
    property_type = models.CharField(max_length=20, choices=PROPERTY_TYPE_CHOICES)
    category = models.ForeignKey(PropertyCategory, on_delete=models.SET_NULL, null=True, related_name='properties')
    
    # Owner
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='properties')
    
    # Location
    region = models.CharField(max_length=100, choices=REGION_CHOICES)
    city = models.CharField(max_length=100)
    area = models.CharField(max_length=200)
    address = models.CharField(max_length=500)
    location = models.CharField(max_length=50, default='5.6037,-0.1870')  # lat,long format
    latitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)
    
    # Pricing
    price = models.DecimalField(max_digits=12, decimal_places=2)
    currency = models.CharField(max_length=3, choices=CURRENCY_CHOICES, default='GHS')
    negotiable = models.BooleanField(default=False)
    
    # Property Details
    bedrooms = models.IntegerField(default=0)
    bathrooms = models.IntegerField(default=0)
    size = models.DecimalField(max_digits=10, decimal_places=2, help_text="Size in square meters")
    furnishing = models.CharField(max_length=20, choices=FURNISHING_CHOICES, default='unfurnished')
    
    # Amenities
    parking = models.BooleanField(default=False)
    security = models.BooleanField(default=False)
    swimming_pool = models.BooleanField(default=False)
    gym = models.BooleanField(default=False)
    garden = models.BooleanField(default=False)
    balcony = models.BooleanField(default=False)
    wifi = models.BooleanField(default=False)
    air_conditioning = models.BooleanField(default=False)
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='available')
    is_featured = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)
    
    # Stats
    views = models.IntegerField(default=0)
    favorites_count = models.IntegerField(default=0)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    published_at = models.DateTimeField(blank=True, null=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = "Properties"
        indexes = [
            models.Index(fields=['owner', 'status']),
            models.Index(fields=['region', 'status']),
            models.Index(fields=['status', '-created_at']),
            models.Index(fields=['is_featured', '-created_at']),
            models.Index(fields=['price', 'status']),
            models.Index(fields=['category', 'status']),
        ]
    
    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)
    
    def increment_views(self):
        self.views += 1
        self.save(update_fields=['views'])
    
    def get_absolute_url(self):
        return f"/properties/{self.slug}/"


class PropertyImage(models.Model):
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='properties/images/')
    caption = models.CharField(max_length=200, blank=True)
    is_primary = models.BooleanField(default=False)
    order = models.IntegerField(default=0)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['order', '-is_primary', '-uploaded_at']
        indexes = [
            models.Index(fields=['property', '-uploaded_at']),
            models.Index(fields=['property', 'is_primary']),
        ]
    
    def __str__(self):
        return f"Image for {self.property.title}"


class PropertyVideo(models.Model):
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='videos')
    video = models.FileField(upload_to='properties/videos/')
    thumbnail = models.ImageField(upload_to='properties/thumbnails/', blank=True)
    title = models.CharField(max_length=200, blank=True)
    duration = models.IntegerField(default=0, help_text="Duration in seconds")
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-uploaded_at']
    
    def __str__(self):
        return f"Video for {self.property.title}"


class Favorite(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='favorites')
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='favorited_by')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['user', 'property']
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['property', '-created_at']),
        ]
    
    def __str__(self):
        return f"{self.user.username} favorited {self.property.title}"


class PropertyView(models.Model):
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='property_views')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    ip_address = models.GenericIPAddressField()
    viewed_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-viewed_at']
        indexes = [
            models.Index(fields=['property', '-viewed_at']),
            models.Index(fields=['user', '-viewed_at']),
        ]


class PropertyReview(models.Model):
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)])
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['property', 'user']
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['property', '-created_at']),
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['rating']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.property.title} ({self.rating}★)"
