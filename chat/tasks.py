from django.core.mail import send_mail
from django.conf import settings


def send_chat_notification_email(recipient_email: str, subject: str, plain_message: str, html_message: str):
    """Task to send a chat notification email. Designed to be called via django-q async_task."""
    try:
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[recipient_email],
            html_message=html_message,
            fail_silently=False,
        )
    except Exception:
        # Swallow exceptions to avoid task retries spamming logs; consider logging locally if needed
        pass
