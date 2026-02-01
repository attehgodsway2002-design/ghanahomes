from django.urls import path
from . import views
from .email_monitoring import email_task_dashboard, retry_failed_email_task

app_name = 'payments'

urlpatterns = [
    path('initialize/<int:subscription_id>/', views.initialize_payment, name='initialize'),
    path('process/<int:payment_id>/', views.process_payment, name='process'),
    path('verify/', views.verify_payment, name='verify'),
    path('success/', views.payment_success, name='success'),
    path('cancel/', views.payment_cancel, name='cancel'),
    path('webhook/', views.paystack_webhook, name='webhook'),
    path('history/', views.payment_history, name='history'),
    path('dashboard/', views.payment_dashboard, name='dashboard'),
    path('retry/<int:subscription_id>/', views.retry_payment, name='retry'),
    path('email-dashboard/', email_task_dashboard, name='email_dashboard'),
    path('email-dashboard/retry/<str:task_id>/', retry_failed_email_task, name='retry_email_task'),
]