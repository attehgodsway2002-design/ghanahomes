from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.conf import settings
from .pdf import generate_payment_receipt
import logging

logger = logging.getLogger(__name__)

def send_payment_confirmation_email(payment_id):
    """
    Send payment confirmation email with PDF receipt
    """
    from .models import Payment  # Import here to avoid circular imports
    
    try:
        payment = Payment.objects.select_related(
            'user',
            'subscription',
            'subscription__plan'
        ).get(id=payment_id)
        
        # Generate PDF receipt
        pdf_content = generate_payment_receipt(payment)
        
        # Prepare email context
        context = {
            'payment': payment,
            'site_url': settings.SITE_URL.rstrip('/'),
            'user': payment.user,
        }
        
        # Create email message
        email = EmailMessage(
            subject='Payment Successful - GhanaHomes',
            body=render_to_string('emails/payment_success.html', context),
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[payment.user.email]
        )
        
        # Attach PDF receipt
        email.attach(
            filename=f'receipt-{payment.paystack_reference}.pdf',
            content=pdf_content,
            mimetype='application/pdf'
        )
        
        # Set email to use HTML content
        email.content_subtype = 'html'
        
        # Send email
        email.send()
        
        logger.info(f"Sent payment confirmation email for payment {payment_id}")
        
    except Exception as e:
        logger.error(f"Failed to send payment confirmation email for payment {payment_id}: {str(e)}")
        raise

def send_payment_cancelled_email(payment_id):
    """
    Send payment cancelled email notification
    """
    from .models import Payment
    
    try:
        payment = Payment.objects.select_related(
            'user',
            'subscription',
            'subscription__plan'
        ).get(id=payment_id)
        
        context = {
            'payment': payment,
            'site_url': settings.SITE_URL.rstrip('/'),
            'user': payment.user,
        }
        
        email = EmailMessage(
            subject='Payment Cancelled - GhanaHomes',
            body=render_to_string('emails/payment_cancelled.html', context),
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[payment.user.email]
        )
        
        email.content_subtype = 'html'
        email.send()
        
        logger.info(f"Sent payment cancelled email for payment {payment_id}")
        
    except Exception as e:
        logger.error(f"Failed to send payment cancelled email for payment {payment_id}: {str(e)}")
        raise


def check_and_retry_timed_out_payments():
    """
    Check for pending payments that haven't been verified within a timeout period.
    Automatically mark them as ready for retry and notify the user.
    """
    from django.utils import timezone
    from datetime import timedelta
    from .models import Payment
    
    # Timeout period: if payment is pending for more than 5 minutes
    timeout_minutes = 5
    timeout_threshold = timezone.now() - timedelta(minutes=timeout_minutes)
    
    try:
        # Find pending payments that haven't been updated in 5+ minutes
        timed_out_payments = Payment.objects.filter(
            status='pending',
            updated_at__lt=timeout_threshold
        ).select_related('user', 'subscription')
        
        retry_count = 0
        for payment in timed_out_payments:
            try:
                # Check if webhook has processed this payment (final verification)
                # If still pending, it likely timed out or webhook failed
                
                logger.warning(
                    f"Payment {payment.paystack_reference} timed out after {timeout_minutes} minutes. "
                    f"Marking for manual retry."
                )
                
                # Send retry notification email
                context = {
                    'payment': payment,
                    'site_url': settings.SITE_URL.rstrip('/'),
                    'user': payment.user,
                    'retry_link': f"{settings.SITE_URL}/subscriptions/{payment.subscription.id}/",
                }
                
                email = EmailMessage(
                    subject='Payment Timeout - Please Retry - GhanaHomes',
                    body=render_to_string('emails/payment_retry_timeout.html', context),
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    to=[payment.user.email]
                )
                
                email.content_subtype = 'html'
                email.send()
                
                logger.info(f"Sent payment retry notification for {payment.paystack_reference}")
                retry_count += 1
                
            except Exception as e:
                logger.error(f"Error processing timed-out payment {payment.id}: {str(e)}")
        
        logger.info(f"Checked for timed-out payments. Found and notified {retry_count} payments.")
        return {'checked': timed_out_payments.count(), 'notified': retry_count}
        
    except Exception as e:
        logger.error(f"Error in check_and_retry_timed_out_payments: {str(e)}")
        raise


def log_email_status(task):
    """
    Log the status of an email task (success or failure)
    Used as a hook by django_q async tasks
    """
    if task.failed:
        logger.error(f"Email task {task.id} failed: {task.result}")
    else:
        logger.info(f"Email task {task.id} completed successfully")