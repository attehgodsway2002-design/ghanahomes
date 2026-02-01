from django.urls import path
from . import views
from . import verification_admin_views

app_name = 'accounts'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('profile/', views.profile, name='profile'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    path('change-password/', views.change_password, name='change_password'),
    path('verify/', views.verify_account, name='verify_account'),
    path('contact/', views.contact, name='contact'),
    path('password-reset/', views.password_reset_request, name='password_reset_request'),
    path('password-reset-confirm/<uidb64>/<token>/', views.password_reset_confirm, name='password_reset_confirm'),
    
    # Admin verification paths
    path('admin/verification/', verification_admin_views.verification_dashboard, name='verification_dashboard'),
    path('admin/verification/<int:pk>/', verification_admin_views.verification_detail, name='verification_detail'),
    path('admin/verification/<int:pk>/quick-approve/', verification_admin_views.verification_quick_approve, name='verification_quick_approve'),
]
