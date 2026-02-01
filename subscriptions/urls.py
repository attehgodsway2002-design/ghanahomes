from django.urls import path
from . import views

app_name = 'subscriptions'

urlpatterns = [
    path('plans/', views.subscription_plans, name='plans'),
    path('subscribe/<str:plan_type>/', views.subscribe, name='subscribe'),
    path('my-subscription/', views.my_subscription, name='my_subscription'),
    path('cancel/', views.cancel_subscription, name='cancel'),
    path('renew/', views.renew_subscription, name='renew'),
]