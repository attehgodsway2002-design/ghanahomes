from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import User

class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Email Address'
        })
    )
    phone = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '+233XXXXXXXXX'
        })
    )
    
    class Meta:
        model = User
        fields = ['username', 'email', 'user_type', 'phone', 'password1', 'password2']
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Username'
            }),
            'user_type': forms.Select(attrs={
                'class': 'form-control'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Password'
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Confirm Password'
        })
    
    def clean_username(self):
        """Validate username"""
        username = self.cleaned_data.get('username', '').strip()
        
        if len(username) < 3:
            raise forms.ValidationError('Username must be at least 3 characters long.')
        
        if len(username) > 30:
            raise forms.ValidationError('Username must not exceed 30 characters.')
        
        # Check for valid characters
        if not username.replace('_', '').replace('-', '').isalnum():
            raise forms.ValidationError('Username can only contain letters, numbers, hyphens and underscores.')
        
        return username
    
    def clean_email(self):
        """Validate email"""
        email = self.cleaned_data.get('email', '').strip().lower()
        
        if not email:
            raise forms.ValidationError('Email address is required.')
        
        if User.objects.filter(email=email).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError('This email address is already registered.')
        
        return email
    
    def clean_phone(self):
        """Validate phone number"""
        phone = self.cleaned_data.get('phone', '').strip()
        
        if phone and not phone.replace('+', '').replace('-', '').isdigit():
            raise forms.ValidationError('Phone number should only contain digits, + and - characters.')
        
        return phone


class UserLoginForm(AuthenticationForm):
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Username or Email'
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Password'
        })
    )


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = [
            'first_name', 'last_name', 'email', 'phone', 'profile_picture',
            'bio', 'address', 'city', 'region', 'company_name', 
            'whatsapp', 'facebook', 'instagram',
            'email_notifications', 'sms_notifications'
        ]
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+233XXXXXXXXX'}),
            'bio': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'address': forms.TextInput(attrs={'class': 'form-control'}),
            'city': forms.TextInput(attrs={'class': 'form-control'}),
            'region': forms.Select(attrs={'class': 'form-select'}),
            'company_name': forms.TextInput(attrs={'class': 'form-control'}),
            'whatsapp': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+233XXXXXXXXX'}),
            'facebook': forms.URLInput(attrs={'class': 'form-control'}),
            'instagram': forms.URLInput(attrs={'class': 'form-control'}),
            'email_notifications': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'sms_notifications': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
    
    def clean_email(self):
        """Check if email is unique (excluding current user)"""
        email = self.cleaned_data.get('email')
        if email:
            # Check if another user has this email
            existing = User.objects.filter(email=email).exclude(pk=self.instance.pk).exists()
            if existing:
                raise forms.ValidationError('This email address is already in use.')
        return email


class VerificationForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['license_number', 'verification_document']
        widgets = {
            'license_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'License/Registration Number'
            }),
        }
