from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import PasswordChangeView
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.tokens import default_token_generator
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.urls import reverse, reverse_lazy
from .forms import UserRegistrationForm, UserLoginForm, UserProfileForm, VerificationForm
from .models import User, VerificationRequest
from properties.models import Property
from subscriptions.models import Subscription

def register(request):
    if request.user.is_authenticated:
        return redirect('properties:home')
    
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            
            # Send role-specific welcome email
            try:
                from django.urls import reverse
                browse_url = request.build_absolute_uri(reverse('properties:home'))
                dashboard_url = request.build_absolute_uri(reverse('properties:my_properties'))
                
                # Determine which template to use based on user type
                if user.is_landlord():
                    template_name = 'emails/welcome_landlord.html'
                    subject = 'Welcome to GhanaHomes - Landlord Portal!'
                    context = {
                        'user': user,
                        'dashboard_url': dashboard_url
                    }
                else:
                    template_name = 'emails/welcome_tenant.html'
                    subject = 'Welcome to GhanaHomes - Find Your Perfect Home!'
                    context = {
                        'user': user,
                        'browse_url': browse_url
                    }
                
                html_message = render_to_string(template_name, context)
                plain_message = strip_tags(html_message)
                
                send_mail(
                    subject=subject,
                    message=plain_message,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[user.email],
                    html_message=html_message,
                    fail_silently=True,
                )
            except:
                pass
            
            login(request, user)
            messages.success(request, 'Registration successful! Welcome to GhanaHomes.')
            
            # Redirect based on user type
            if user.is_landlord():
                return redirect('subscriptions:plans')
            return redirect('properties:home')
    else:
        form = UserRegistrationForm()
    
    return render(request, 'accounts/register.html', {'form': form})


def user_login(request):
    if request.user.is_authenticated:
        return redirect('properties:home')
    
    if request.method == 'POST':
        form = UserLoginForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            
            if user is not None:
                login(request, user)
                messages.success(request, f'Welcome back, {user.username}!')
                
                # Redirect to next or dashboard
                next_url = request.GET.get('next')
                if next_url:
                    return redirect(next_url)
                return redirect('accounts:dashboard')
        else:
            messages.error(request, 'Invalid username or password.')
    else:
        form = UserLoginForm()
    
    return render(request, 'accounts/login.html', {'form': form})


@login_required
def user_logout(request):
    logout(request)
    messages.info(request, 'You have been logged out successfully.')
    return redirect('properties:home')


@login_required
def profile(request):
    context = {
        'user': request.user,
    }
    
    if request.user.is_landlord():
        properties = Property.objects.filter(owner=request.user)
        context['properties_count'] = properties.count()
        context['active_properties'] = properties.filter(status='available').count()
        
        try:
            subscription = Subscription.objects.get(user=request.user)
            context['subscription'] = subscription
        except Subscription.DoesNotExist:
            context['subscription'] = None
    
    return render(request, 'accounts/profile.html', context)


@login_required
def edit_profile(request):
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('accounts:profile')
    else:
        form = UserProfileForm(instance=request.user)
    
    return render(request, 'accounts/edit_profile.html', {'form': form})


@login_required
def verify_account(request):
    if not request.user.is_landlord():
        messages.error(request, 'Only landlords/agents can request verification.')
        return redirect('accounts:profile')
    
    if request.user.is_verified:
        messages.info(request, 'Your account is already verified.')
        return redirect('accounts:profile')
    
    # Check if user already has a pending verification request
    pending_request = VerificationRequest.objects.filter(
        user=request.user,
        status='pending'
    ).first()
    
    if request.method == 'POST':
        form = VerificationForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            # Get the license number and document from form
            license_number = form.cleaned_data.get('license_number')
            verification_document = request.FILES.get('verification_document')
            
            # Create or update verification request
            if pending_request:
                # Update existing pending request
                pending_request.license_number = license_number
                if verification_document:
                    pending_request.verification_document = verification_document
                pending_request.save()
                
                # Send update confirmation email
                try:
                    from .email_utils import send_verification_submitted
                    send_verification_submitted(request.user, license_number, pending_request.updated_at)
                except Exception as e:
                    print(f"Error sending verification update email: {e}")
                
                messages.info(request, 'Your verification request has been updated. We will review it shortly.')
            else:
                # Create new verification request
                verification_request = VerificationRequest.objects.create(
                    user=request.user,
                    license_number=license_number,
                    verification_document=verification_document
                )
                
                # Send submission confirmation email to user
                try:
                    from .email_utils import send_verification_submitted
                    send_verification_submitted(request.user, license_number, verification_request.created_at)
                except Exception as e:
                    print(f"Error sending verification submission email: {e}")
                
                # Send admin notification
                try:
                    from .email_utils import send_admin_verification_submitted
                    send_admin_verification_submitted(verification_request, request)
                except Exception as e:
                    print(f"Error sending admin verification notification: {e}")
                
                messages.success(request, 'Verification request submitted! We will review it shortly.')
            
            return redirect('accounts:profile')
    else:
        form = VerificationForm(instance=request.user)
    
    context = {
        'form': form,
        'pending_request': pending_request,
    }
    
    return render(request, 'accounts/verify.html', context)


@login_required
def dashboard(request):
    context = {}
    
    if request.user.is_landlord():
        properties = Property.objects.filter(owner=request.user)
        context['total_properties'] = properties.count()
        context['available_properties'] = properties.filter(status='available').count()
        context['total_views'] = sum(p.views for p in properties)
        context['total_favorites'] = sum(p.favorites_count for p in properties)
        context['recent_properties'] = properties[:5]
        
        try:
            subscription = Subscription.objects.get(user=request.user)
            context['subscription'] = subscription
        except Subscription.DoesNotExist:
            context['subscription'] = None
    
    else:  # Tenant
        from properties.models import Favorite
        favorites = Favorite.objects.filter(user=request.user)
        context['favorites_count'] = favorites.count()
        context['recent_favorites'] = favorites[:5]
    
    return render(request, 'accounts/dashboard.html', context)


def contact(request):
    """Contact page - display contact information and contact form"""
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        email = request.POST.get('email', '').strip()
        phone = request.POST.get('phone', '').strip()
        subject = request.POST.get('subject', '').strip()
        message = request.POST.get('message', '').strip()
        
        if not all([name, email, subject, message]):
            messages.error(request, 'Please fill in all required fields.')
            return render(request, 'accounts/contact.html')
        
        try:
            # Send email to support
            email_body = f"""
New Contact Form Submission

Name: {name}
Email: {email}
Phone: {phone}
Subject: {subject}

Message:
{message}
            """
            
            send_mail(
                subject=f'Contact Form: {subject}',
                message=email_body,
                from_email=email,
                recipient_list=[settings.DEFAULT_FROM_EMAIL],
                fail_silently=False,
            )
            
            # Send confirmation to user
            send_mail(
                subject='We received your message - GhanaHomes',
                message=f'Hello {name},\n\nThank you for contacting GhanaHomes. We have received your message and will get back to you shortly.\n\nBest regards,\nThe GhanaHomes Team',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[email],
                fail_silently=True,
            )
            
            messages.success(request, 'Thank you for contacting us! We will get back to you shortly.')
            return redirect('accounts:contact')
        
        except Exception as e:
            messages.error(request, f'Error sending message: {str(e)}')
    
    context = {
        'support_email': 'realhuntsmen.tech@gmail.com',
        'support_phone': '+233 55 606 7555',
        'support_location': 'Koforidua, Ghana',
    }
    
    return render(request, 'accounts/contact.html', context)


@login_required
def change_password(request):
    """Allow logged-in users to change their password using Django's built-in PasswordChangeView"""
    if request.method == 'POST':
        # Accept old password under both 'oldpassword' (legacy) and 'old_password'
        post_data = request.POST.copy()
        if 'oldpassword' in post_data and 'old_password' not in post_data:
            post_data['old_password'] = post_data.get('oldpassword')
        form = PasswordChangeForm(request.user, post_data)
        if form.is_valid():
            user = form.save()
            # Update session to avoid logout
            update_session_auth_hash(request, user)
            messages.success(request, 'Your password was successfully updated!')
            return redirect('accounts:profile')
    else:
        form = PasswordChangeForm(request.user)
    
    return render(request, 'accounts/change_password.html', {'form': form})


def password_reset_request(request):
    """Handle password reset request - user enters email"""
    if request.user.is_authenticated:
        return redirect('properties:home')
    
    if request.method == 'POST':
        email = request.POST.get('email', '').strip()
        
        if not email:
            messages.error(request, 'Please enter your email address.')
            return render(request, 'accounts/password_reset_request.html')
        
        try:
            user = User.objects.get(email=email)
            
            # Generate token
            token = default_token_generator.make_token(user)
            
            # Build reset URL
            reset_url = request.build_absolute_uri(
                reverse('accounts:password_reset_confirm', kwargs={
                    'uidb64': __import__('django.utils.http', fromlist=['urlsafe_base64_encode']).urlsafe_base64_encode(__import__('django.utils.encoding', fromlist=['force_bytes']).force_bytes(user.pk)),
                    'token': token
                })
            )
            
            # Render email template
            html_message = render_to_string('emails/password_reset.html', {
                'user': user,
                'reset_url': reset_url
            })
            plain_message = strip_tags(html_message)
            
            # Send email
            send_mail(
                subject='Password Reset Request - GhanaHomes',
                message=plain_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                html_message=html_message,
                fail_silently=False,
            )
            
            messages.success(request, f'Password reset link sent to {email}. Check your email (including spam folder).')
            return redirect('accounts:login')
            
        except User.DoesNotExist:
            # Don't reveal if email exists for security
            messages.info(request, 'If an account with that email exists, you will receive a password reset link.')
            return redirect('accounts:login')
        
        except Exception as e:
            messages.error(request, f'Error sending reset email: {str(e)}')
    
    return render(request, 'accounts/password_reset_request.html')


def password_reset_confirm(request, uidb64, token):
    """Handle password reset confirmation - user enters new password"""
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    
    # Check token validity
    if user is None or not default_token_generator.check_token(user, token):
        messages.error(request, 'Invalid or expired password reset link. Please request a new one.')
        return redirect('accounts:password_reset_request')
    
    if request.method == 'POST':
        password = request.POST.get('password', '').strip()
        password_confirm = request.POST.get('password_confirm', '').strip()
        
        # Validation
        if not password:
            messages.error(request, 'Password cannot be empty.')
            return render(request, 'accounts/password_reset_confirm.html', {'uidb64': uidb64, 'token': token})
        
        if password != password_confirm:
            messages.error(request, 'Passwords do not match.')
            return render(request, 'accounts/password_reset_confirm.html', {'uidb64': uidb64, 'token': token})
        
        if len(password) < 8:
            messages.error(request, 'Password must be at least 8 characters long.')
            return render(request, 'accounts/password_reset_confirm.html', {'uidb64': uidb64, 'token': token})
        
        # Update password
        try:
            user.set_password(password)
            user.save()
            
            # Log audit event
            from accounts.audit_utils import log_audit
            log_audit(
                user=user,
                action='PASSWORD_CHANGED',
                obj=user,
                ip_address=request.META.get('REMOTE_ADDR'),
                user_agent=request.META.get('HTTP_USER_AGENT', '')
            )
            
            # Send password change confirmation email
            try:
                from django.utils import timezone
                html_message = render_to_string('emails/password_changed.html', {
                    'user': user,
                    'timestamp': timezone.now()
                })
                plain_message = strip_tags(html_message)
                
                send_mail(
                    subject='Password Changed Successfully - GhanaHomes',
                    message=plain_message,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[user.email],
                    html_message=html_message,
                    fail_silently=True,
                )
            except Exception as email_error:
                # Log but don't fail if email fails
                pass
            
            messages.success(request, 'Your password has been reset successfully. You can now login with your new password.')
            return redirect('accounts:login')
        
        except Exception as e:
            messages.error(request, f'Error resetting password: {str(e)}')
    
    return render(request, 'accounts/password_reset_confirm.html', {'uidb64': uidb64, 'token': token})
