from django import forms
from .models import SubscriptionPlan

class SubscriptionForm(forms.Form):
    plan_type = forms.ChoiceField(
        choices=SubscriptionPlan.PLAN_TYPE_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    duration = forms.ChoiceField(
        choices=SubscriptionPlan.DURATION_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    auto_renew = forms.TypedChoiceField(
        choices=(('false', 'No'), ('true', 'Yes')),
        coerce=lambda value: value == 'true',
        widget=forms.HiddenInput()
    )