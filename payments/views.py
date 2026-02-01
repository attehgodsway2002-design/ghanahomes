from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.utils import timezone
from subscriptions.models import Subscription
from .models import Payment
import json
import uuid
import logging
from django_ratelimit.decorators import ratelimit
from html import escape

# Paystack utility
from pypaystack2 import PaystackClient
from django.core.exceptions import ImproperlyConfigured
from django.urls import reverse
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags

# Local utils
from .utils import verify_webhook_signature, format_amount_for_paystack
from accounts.email_utils import send_templated_email, send_invoice_receipt, send_refund_confirmation

logger = logging.getLogger(__name__)

def get_paystack_instance():
    # Fail fast if secret key is not configured
    if not getattr(settings, 'PAYSTACK_SECRET_KEY', ''):
        raise ImproperlyConfigured('PAYSTACK_SECRET_KEY is not set. Please set it in your environment (.env)')
    return PaystackClient(secret_key=settings.PAYSTACK_SECRET_KEY)


@login_required
def initialize_payment(request, subscription_id):
    """Initialize payment and show confirmation page"""
    subscription = get_object_or_404(Subscription, id=subscription_id, user=request.user)
    
    # Check if it's a free plan - skip payment
    if subscription.plan.is_free:
        subscription.status = 'active'
        subscription.save()
        messages.success(request, f'Welcome to {subscription.plan.name}! Your free subscription is now active.')
        return redirect('properties:property_list')
    
    # Calculate amount based on duration
    amount = subscription.plan.get_price(subscription.duration)
    
    # Generate unique reference
    reference = f"GH-{uuid.uuid4().hex[:12].upper()}"
    
    # Create payment record
    payment = Payment.objects.create(
        user=request.user,
        subscription=subscription,
        amount=amount,
        currency='GHS',
        status='pending',
        paystack_reference=reference,
    )
    
    context = {
        'subscription': subscription,
        'payment': payment,
    }
    
    return render(request, 'payments/confirm_fixed.html', context)

@login_required
@ratelimit(key='user', rate='10/h', method='POST')
def process_payment(request, payment_id):
    """Process payment with Paystack"""
    if request.method != 'POST':
        return redirect('subscriptions:plans')

    payment = get_object_or_404(Payment, id=payment_id, user=request.user)
    
    # Validate payment state
    if payment.status != 'pending':
        messages.error(request, 'This payment has already been processed.')
        return redirect('subscriptions:plans')
    
    try:
        # Ensure Paystack is properly configured
        if not settings.PAYSTACK_SECRET_KEY or not settings.PAYSTACK_PUBLIC_KEY:
            logger.error("Paystack keys not configured")
            messages.error(request, 'Payment system is not properly configured. Please contact support.')
            return redirect('subscriptions:plans')

        paystack = get_paystack_instance()
        
        # Build absolute callback URL
        callback_url = request.build_absolute_uri(reverse('payments:verify'))
        
        # Log payment attempt
        logger.info(f"Payment Initialization Details:")
        logger.info(f"- Reference: {payment.paystack_reference}")
        logger.info(f"- Amount: {payment.amount} {payment.currency}")
        logger.info(f"- Email: {request.user.email}")
        logger.info(f"- Callback URL: {callback_url}")
        
        # Prepare metadata
        metadata = {
            'payment_id': str(payment.id),
            'subscription_id': str(payment.subscription.id),
            'user_id': str(request.user.id),
            'plan_name': payment.subscription.plan.name,
            'duration': payment.subscription.duration,
            'customer_email': request.user.email,
            'environment': 'development' if settings.DEBUG else 'production'
        }
        
        # Initialize transaction with retry
        max_retries = 2
        for attempt in range(max_retries):
            try:
                response = paystack.transactions.initialize(
                    email=request.user.email,
                    amount=int(payment.amount * 100),  # Convert to pesewas
                    reference=payment.paystack_reference,
                    callback_url=callback_url,
                    currency=payment.currency,
                    metadata=metadata,
                )
                break  # Success, exit retry loop
            except Exception as e:
                if attempt == max_retries - 1:  # Last attempt
                    raise  # Re-raise the exception
                logger.warning(f"Paystack API call failed (attempt {attempt + 1}): {str(e)}")
                import time
                time.sleep(1)  # Wait before retry
        
        # Log complete response for debugging
        resp_status = getattr(response, 'status', None)
        resp_message = getattr(response, 'message', '')
        resp_data = getattr(response, 'data', None)

        # Attempt to coerce resp_data to a dict if it's a pydantic model
        try:
            if hasattr(resp_data, 'dict'):
                resp_data = resp_data.dict()
        except Exception:
            pass

        logger.info(f"Paystack Response for {payment.paystack_reference}:")
        logger.info(f"- Status: {resp_status}")
        logger.info(f"- Message: {resp_message}")
        logger.info(f"- Data: {resp_data}")

        if not resp_status:
            error_msg = resp_message or 'Payment initialization failed'
            logger.error(f"Paystack error: {error_msg}")
            messages.error(request, f'Unable to initialize payment: {error_msg}')
            return redirect('subscriptions:plans')

        # Get required data from response
        data = resp_data or {}
        if isinstance(data, dict):
            access_code = data.get('access_code')
            auth_url = data.get('authorization_url')
        else:
            access_code = getattr(data, 'access_code', None)
            auth_url = getattr(data, 'authorization_url', None)

        if not access_code or not auth_url:
            logger.error(f"Missing required data from Paystack: access_code={bool(access_code)}, auth_url={bool(auth_url)}")
            messages.error(request, 'Invalid response from payment provider. Please try again.')
            return redirect('subscriptions:plans')

        # Update payment record
        payment.paystack_access_code = access_code
        payment.save()

        # Log successful initialization
        logger.info(f"Payment {payment.paystack_reference} successfully initialized")

        # Return the authorization URL and access code as JSON
        return JsonResponse({
            'status': True,
            'message': 'Payment initialized',
            'data': {
                'authorization_url': auth_url,
                'access_code': access_code,
                'reference': payment.paystack_reference
            }
        })
            
    except Exception as e:
        import traceback
        logger.error(f"Payment processing error for {payment.paystack_reference}")
        logger.error(f"Error details: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        
        # Update payment status to failed
        payment.status = 'failed'
        payment.save()
        
        messages.error(request, 'Unable to process payment. Please try again or contact support.')
        return redirect('subscriptions:plans')


@login_required
@ratelimit(key='user', rate='20/h', method='GET')
def verify_payment(request):
    """Verify Paystack payment"""
    reference = request.GET.get('reference')
    
    if not reference:
        messages.error(request, 'Invalid payment reference.')
        return redirect('subscriptions:plans')
    
    try:
        payment = Payment.objects.get(paystack_reference=reference, user=request.user)
    except Payment.DoesNotExist:
        messages.error(request, 'Payment record not found.')
        return redirect('subscriptions:plans')
    
    try:
        import json
        
        # Verify with Paystack
        paystack = get_paystack_instance()
        response = paystack.transactions.verify(reference=reference)
        
        logger.info(f"Raw Paystack response object: {response}")
        logger.info(f"Response type: {type(response)}")
        logger.info(f"Response dir: {[attr for attr in dir(response) if not attr.startswith('_')]}")
        
        # The pypaystack2 library returns a Response object
        response_data = {}
        
        try:
            # Try the most likely structure first - pypaystack2.Response has a .data attribute
            if hasattr(response, 'status'):
                # Response object itself might have status
                is_success = response.status is True
                logger.info(f"Found status on response object directly: {is_success}")
            
            if hasattr(response, 'data'):
                data_obj = response.data
                logger.info(f"Found .data attribute: {data_obj}, type: {type(data_obj)}")
                
                # Convert to dict
                if hasattr(data_obj, 'dict') and callable(data_obj.dict):
                    response_data = data_obj.dict()
                elif hasattr(data_obj, 'model_dump') and callable(data_obj.model_dump):
                    response_data = data_obj.model_dump()
                elif isinstance(data_obj, dict):
                    response_data = data_obj
                else:
                    response_data = vars(data_obj) if hasattr(data_obj, '__dict__') else {}
                
                logger.info(f"Converted response_data: {response_data}")
        except Exception as e:
            logger.error(f"Failed to extract response data: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
        
        # Extract transaction status
        transaction_status = response_data.get('status', '')
        logger.info(f"Transaction status from data: {transaction_status}")
        
        # Check if payment was successful
        is_success = transaction_status == 'success'
        logger.info(f"Final is_success determination: {is_success}")
        
        if is_success:
            # Update payment
            payment.status = 'completed'
            
            # Extract channel - handle different response formats
            channel = response_data.get('channel', 'unknown')
            if not channel and isinstance(response_data.get('data'), dict):
                channel = response_data['data'].get('channel', 'unknown')
            payment.payment_method = channel
            payment.save()
            
            # Activate subscription
            subscription = payment.subscription
            subscription.status = 'active'
            
            # Reset property count for new plans (first time or upgrade)
            # Only reset if it's a new subscription or if plan changed
            if subscription.property_count == 0 or subscription.plan.id != getattr(subscription, '_previous_plan_id', None):
                subscription.property_count = 0  # Reset to allow new posts
            
            # Set end_date based on subscription duration
            from datetime import timedelta
            if subscription.duration == 'monthly':
                subscription.end_date = timezone.now() + timedelta(days=30)
            elif subscription.duration == 'quarterly':
                subscription.end_date = timezone.now() + timedelta(days=90)
            elif subscription.duration == 'yearly':
                subscription.end_date = timezone.now() + timedelta(days=365)
            else:
                subscription.end_date = timezone.now() + timedelta(days=30)  # Default to monthly
            
            subscription.save()
            
            # Send confirmation email
            # Queue confirmation email with PDF receipt
            try:
                from django_q.tasks import async_task
                async_task(
                    'payments.tasks.send_payment_confirmation_email',
                    payment.id,
                    hook='payments.tasks.log_email_status'
                )
            except Exception as e:
                logger.error(f"Failed to queue confirmation email: {str(e)}")
            
            # Send admin notification for completed payment
            try:
                from accounts.email_utils import send_admin_payment_completed
                send_admin_payment_completed(payment)
            except Exception as e:
                logger.error(f"Failed to send admin payment notification: {str(e)}")
            
            messages.success(request, 'Payment successful! Your subscription is now active.')
            return redirect('payments:success')
        else:
            # Log the response for debugging
            logger.warning(f"Payment verification failed for {payment.paystack_reference}. Response: {response_data}")
            payment.status = 'failed'
            payment.save()
            
            # Send admin notification for failed payment
            try:
                from accounts.email_utils import send_admin_payment_failed
                failure_reason = response_data.get('gateway_response', 'Unknown error')
                send_admin_payment_failed(payment, failure_reason)
            except Exception as e:
                logger.error(f"Failed to send admin payment failure notification: {str(e)}")
            
            messages.error(request, 'Payment verification failed. Please contact support if the amount was debited.')
            return redirect('payments:cancel')
            
    except Exception as e:
        messages.error(request, f'Verification error: {str(e)}')
        return redirect('subscriptions:plans')


@login_required
def payment_success(request):
    """Payment success page"""
    # Find the most recent completed payment for this user
    payment = Payment.objects.filter(user=request.user, status='completed').order_by('-created_at').first()
    context = {}

    if payment:
        subscription = getattr(payment, 'subscription', None)
        plan = getattr(subscription, 'plan', None) if subscription else None

        # For landlords, compute property limits and provide CTA to create property
        if request.user.is_landlord():
            try:
                # Prefer a related name `properties` on the user if available
                properties_posted = request.user.properties.count()
            except Exception:
                # Fallback to querying Property model
                from properties.models import Property
                properties_posted = Property.objects.filter(owner=request.user).count()

            properties_limit = getattr(plan, 'property_limit', 10) if plan else 10
            properties_remaining = max(0, properties_limit - properties_posted)
            post_property_url = reverse('properties:property_create')

            context.update({
                'payment': payment,
                'subscription': subscription,
                'plan': plan,
                'properties_posted': properties_posted,
                'properties_limit': properties_limit,
                'properties_remaining': properties_remaining,
                'post_property_url': post_property_url,
            })
        else:
            context.update({'payment': payment})

    return render(request, 'payments/success.html', context)


@login_required
def payment_cancel(request):
    """Handle payment cancellation"""
    # Try to find the most recent cancelled/failed/pending payment to offer retry
    retry_subscription = None
    try:
        payment = Payment.objects.filter(
            user=request.user,
            status__in=['pending', 'failed']
        ).latest('created_at')

        # Mark pending payments as cancelled
        if payment.status == 'pending':
            payment.status = 'cancelled'
            payment.save()

        # Queue cancellation email for record (best-effort)
        try:
            from django_q.tasks import async_task
            async_task(
                'payments.tasks.send_payment_cancelled_email',
                payment.id,
                hook='payments.tasks.log_email_status'
            )
        except Exception as e:
            logger.error(f"Failed to queue cancellation email: {str(e)}")

        retry_subscription = payment.subscription
        messages.info(request, 'Payment was cancelled. You can try again anytime.')
    except Payment.DoesNotExist:
        messages.warning(request, 'No pending or failed payment found.')

    context = {
        'retry_subscription': retry_subscription,
    }

    return render(request, 'payments/cancel.html', context)


@login_required
@ratelimit(key='user', rate='5/h', method='POST')
def retry_payment(request, subscription_id):
    """Create a new Payment for the subscription and redirect to initialize view"""
    if request.method != 'POST':
        return redirect('subscriptions:plans')

    subscription = get_object_or_404(Subscription, id=subscription_id, user=request.user)

    # Create new payment record
    payment = Payment.objects.create(
        user=request.user,
        subscription=subscription,
        amount=subscription.plan.get_price(subscription.duration),
        currency='GHS',
        status='pending',
        paystack_reference=f"GH-{uuid.uuid4().hex[:12].upper()}"
    )

    messages.info(request, 'A new payment has been created. Redirecting to confirmation...')
    return redirect('payments:initialize', subscription_id=subscription.id)


@csrf_exempt
def paystack_webhook(request):
    """Handle Paystack webhooks"""
    if request.method != 'POST':
        return HttpResponse(status=405)

    # Get Paystack signature from headers
    signature = request.headers.get('x-paystack-signature')

    try:
        # Verify webhook signature
        if not verify_webhook_signature(request.body, signature):
            logger.warning("Invalid webhook signature received")
            return HttpResponse(status=401)

        payload = json.loads(request.body)
        event = payload.get('event')
        
        logger.info(f"Received Paystack webhook: {event}")
        
        if event == 'charge.success':
            data = payload.get('data', {})
            reference = data.get('reference')
            
            if not reference:
                logger.error("No reference in webhook data")
                return HttpResponse(status=400)
            
            try:
                # Get and validate payment
                payment = Payment.objects.select_related('subscription', 'user').get(
                    paystack_reference=reference,
                    status='pending'
                )
                
                # Verify amount
                expected_amount = format_amount_for_paystack(payment.amount)
                received_amount = data.get('amount')
                
                if received_amount != expected_amount:
                    logger.error(f"Amount mismatch for {reference}: expected {expected_amount}, got {received_amount}")
                    return HttpResponse(status=400)
                
                # Update payment details
                payment.status = 'completed'
                payment.payment_method = data.get('channel', '')
                payment.save()
                
                # Activate subscription
                subscription = payment.subscription
                subscription.status = 'active'
                subscription.save()
                
                # Send role-specific confirmation email
                try:
                    from django.urls import reverse
                    user = payment.user
                    plan = subscription.plan
                    
                    if user.is_landlord():
                        # Send landlord post-payment email with property posting info
                        post_property_url = reverse('properties:property_create')
                        
                        # Get landlord's property count for this subscription
                        properties_posted = user.properties.count()
                        properties_limit = plan.property_limit if hasattr(plan, 'property_limit') else 10
                        properties_remaining = max(0, properties_limit - properties_posted)
                        
                        context = {
                            'payment': payment,
                            'reference_code': payment.paystack_reference,
                            'amount': payment.amount,
                            'payment_date': payment.created_at,
                            'plan_name': plan.name,
                            'properties_limit': properties_limit,
                            'properties_posted': properties_posted,
                            'properties_remaining': properties_remaining,
                            'post_property_url': reverse('properties:property_create'),
                        }
                        
                        html_message = render_to_string('emails/payment_success_landlord.html', context)
                        subject = f'Payment Successful - Start Posting Properties! ({properties_remaining} slots available)'
                    else:
                        # Send tenant payment confirmation
                        context = {
                            'payment': payment,
                            'site_url': settings.SITE_URL.rstrip('/'),
                        }
                        
                        html_message = render_to_string('emails/payment_success.html', context)
                        subject = 'Payment Successful - GhanaHomes'
                    
                    plain_message = strip_tags(html_message)
                    
                    send_mail(
                        subject=subject,
                        message=plain_message,
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        recipient_list=[user.email],
                        html_message=html_message,
                        fail_silently=True
                    )
                    
                    # Also send invoice/receipt
                    try:
                        invoice_data = {
                            'invoice_number': f"INV-{payment.paystack_reference}",
                            'invoice_date': payment.created_at,
                            'plan_name': plan.name,
                            'unit_price': plan.get_price(subscription.duration),
                            'quantity': 1,
                            'subtotal': payment.amount,
                            'total_amount': payment.amount,
                            'payment_method': 'Card',
                            'transaction_id': payment.paystack_reference,
                            'payment_date': payment.created_at,
                            'start_date': subscription.start_date,
                            'end_date': subscription.end_date,
                        }
                        send_invoice_receipt(user, payment, subscription, invoice_data)
                    except Exception as e:
                        logger.warning(f"Failed to send invoice: {str(e)}")
                    
                except Exception as e:
                    logger.error(f"Failed to send confirmation email: {str(e)}")
                
                logger.info(f"Successfully processed payment {reference}")
                return HttpResponse(status=200)
                
            except Payment.DoesNotExist:
                logger.warning(f"Payment not found for reference {reference}")
                return HttpResponse(status=404)
            
        return HttpResponse(status=200)
        
    except json.JSONDecodeError:
        logger.error("Invalid JSON in webhook body")
        return HttpResponse(status=400)
    except Exception as e:
        logger.exception("Error processing webhook")
        return HttpResponse(status=500)


@login_required
def payment_history(request):
    """View payment history"""
    payments = Payment.objects.filter(user=request.user).order_by('-created_at')
    
    context = {
        'payments': payments,
    }
    
    return render(request, 'payments/history.html', context)


@login_required
def payment_dashboard(request):
    """Dashboard showing payment analytics and stats"""
    from django.db.models import Sum, Count, Q
    from django.utils import timezone
    from datetime import timedelta
    
    # Get all payments for the current user
    user_payments = Payment.objects.filter(user=request.user)
    
    # Calculate statistics
    total_payments = user_payments.count()
    total_spent = user_payments.filter(status='completed').aggregate(Sum('amount'))['amount__sum'] or 0
    completed_payments = user_payments.filter(status='completed').count()
    pending_payments = user_payments.filter(status='pending').count()
    failed_payments = user_payments.filter(status='failed').count()
    
    # Calculate average payment amount
    avg_payment = user_payments.filter(status='completed').aggregate(Sum('amount'))['amount__sum'] or 0
    if completed_payments > 0:
        avg_payment = avg_payment / completed_payments
    
    # Recent payments (last 10)
    recent_payments = user_payments.order_by('-created_at')[:10]
    
    # Payments this month
    today = timezone.now()
    month_start = today.replace(day=1)
    payments_this_month = user_payments.filter(
        created_at__gte=month_start,
        status='completed'
    ).count()
    
    # Payments by status (for chart)
    payments_by_status = {
        'completed': user_payments.filter(status='completed').count(),
        'pending': user_payments.filter(status='pending').count(),
        'failed': user_payments.filter(status='failed').count(),
        'cancelled': user_payments.filter(status='cancelled').count(),
    }
    
    context = {
        'total_payments': total_payments,
        'total_spent': total_spent,
        'completed_payments': completed_payments,
        'pending_payments': pending_payments,
        'failed_payments': failed_payments,
        'avg_payment': round(float(avg_payment), 2),
        'recent_payments': recent_payments,
        'payments_this_month': payments_this_month,
        'payments_by_status': payments_by_status,
    }
    
    return render(request, 'payments/dashboard.html', context)
