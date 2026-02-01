from django import forms
from .models import Property, PropertyImage, PropertyVideo, PropertyReview, REGION_CHOICES
from django.conf import settings

class PropertyForm(forms.ModelForm):
    
    class Meta:
        model = Property
        fields = [
            'title', 'description', 'property_type', 'category',
            'region', 'city', 'area', 'address', 'location',
            'price', 'currency', 'negotiable',
            'bedrooms', 'bathrooms', 'size', 'furnishing',
            'parking', 'security', 'swimming_pool', 'gym',
            'garden', 'balcony', 'wifi', 'air_conditioning'
        ]
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., Modern 3 Bedroom Apartment in East Legon'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 5,
                'placeholder': 'Describe your property in detail...'
            }),
            'property_type': forms.Select(attrs={'class': 'form-control'}),
            'category': forms.Select(attrs={'class': 'form-control'}),
            'region': forms.Select(attrs={'class': 'form-control'}),
            'city': forms.TextInput(attrs={'class': 'form-control'}),
            'area': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., East Legon, Airport Residential'
            }),
            'address': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Street address'
            }),
            'price': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '0.00'
            }),
            'currency': forms.Select(attrs={'class': 'form-control'}),
            'negotiable': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'bedrooms': forms.NumberInput(attrs={'class': 'form-control'}),
            'bathrooms': forms.NumberInput(attrs={'class': 'form-control'}),
            'size': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Square meters'
            }),
            'furnishing': forms.Select(attrs={'class': 'form-control'}),
            'parking': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'security': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'swimming_pool': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'gym': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'garden': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'balcony': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'wifi': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'air_conditioning': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Dynamically set region choices
        self.fields['region'].choices = [('', 'Select Region')] + REGION_CHOICES
        # Set currency choices
        self.fields['currency'].choices = [
            ('', 'Select Currency'),
        ] + list(Property.CURRENCY_CHOICES)
    
    def clean_title(self):
        """Validate title length and content"""
        title = self.cleaned_data.get('title', '').strip()
        
        if not title:
            raise forms.ValidationError('Property title is required.')
        
        if len(title) < 5:
            raise forms.ValidationError('Property title must be at least 5 characters long.')
        
        if len(title) > 200:
            raise forms.ValidationError('Property title must not exceed 200 characters.')
        
        return title
    
    def clean_description(self):
        """Validate description"""
        description = self.cleaned_data.get('description', '').strip()
        
        if not description:
            raise forms.ValidationError('Property description is required.')
        
        if len(description) < 20:
            raise forms.ValidationError('Property description must be at least 20 characters long.')
        
        if len(description) > 5000:
            raise forms.ValidationError('Property description must not exceed 5000 characters.')
        
        return description
    
    def clean_price(self):
        """Validate price"""
        price = self.cleaned_data.get('price')
        
        if price is None:
            raise forms.ValidationError('Price is required.')
        
        if price <= 0:
            raise forms.ValidationError('Price must be greater than 0.')
        
        if price > 9999999:
            raise forms.ValidationError('Price exceeds maximum allowed value.')
        
        return price
    
    def clean_bedrooms(self):
        """Validate bedrooms"""
        bedrooms = self.cleaned_data.get('bedrooms')
        
        if bedrooms is None:
            raise forms.ValidationError('Number of bedrooms is required.')
        
        if bedrooms < 0:
            raise forms.ValidationError('Number of bedrooms cannot be negative.')
        
        if bedrooms > 100:
            raise forms.ValidationError('Number of bedrooms seems unrealistic.')
        
        return bedrooms
    
    def clean_bathrooms(self):
        """Validate bathrooms"""
        bathrooms = self.cleaned_data.get('bathrooms')
        
        if bathrooms is None:
            raise forms.ValidationError('Number of bathrooms is required.')
        
        if bathrooms < 0:
            raise forms.ValidationError('Number of bathrooms cannot be negative.')
        
        if bathrooms > 100:
            raise forms.ValidationError('Number of bathrooms seems unrealistic.')
        
        return bathrooms
    
    def clean(self):
        """Cross-field validation"""
        cleaned_data = super().clean()
        bedrooms = cleaned_data.get('bedrooms')
        bathrooms = cleaned_data.get('bathrooms')
        
        if bedrooms is not None and bathrooms is not None:
            if bathrooms > bedrooms:
                raise forms.ValidationError(
                    'Number of bathrooms cannot exceed number of bedrooms.'
                )
        
        return cleaned_data


class PropertyImageForm(forms.ModelForm):
    class Meta:
        model = PropertyImage
        fields = ['image', 'caption', 'is_primary']
        widgets = {
            'caption': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Image caption (optional)'
            }),
            'is_primary': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class PropertyVideoForm(forms.ModelForm):
    class Meta:
        model = PropertyVideo
        fields = ['video', 'thumbnail', 'title']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Video title (optional)'
            }),
        }


class PropertySearchForm(forms.Form):
    query = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search properties...'
        })
    )
    property_type = forms.ChoiceField(
        required=False,
        choices=[('', 'All Types')] + list(Property.PROPERTY_TYPE_CHOICES),
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    region = forms.ChoiceField(
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    city = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'City'
        })
    )
    min_price = forms.DecimalField(
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Min Price'
        })
    )
    max_price = forms.DecimalField(
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Max Price'
        })
    )
    bedrooms = forms.IntegerField(
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Bedrooms'
        })
    )
    bathrooms = forms.IntegerField(
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Bathrooms'
        })
    )
    furnishing = forms.ChoiceField(
        required=False,
        choices=[('', 'Any Furnishing')] + list(Property.FURNISHING_CHOICES),
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['region'].choices = [('', 'All Regions')] + REGION_CHOICES


class PropertyReviewForm(forms.ModelForm):
    class Meta:
        model = PropertyReview
        fields = ['rating', 'comment']
        widgets = {
            'rating': forms.Select(attrs={'class': 'form-control'}),
            'comment': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Share your experience...'
            }),
        }