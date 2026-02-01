from django.db.models.signals import post_save
from django.dispatch import receiver
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
from django.urls import reverse
from .models import Message, ChatRoom

# Use django-q to queue email sending tasks asynchronously
try:
    from django_q.tasks import async_task
except Exception:
    async_task = None


def user_is_active_recently(user, minutes=10):
    """Determine if a user has been active recently.

    This is a simple heuristic: check the user's `last_login` and
    `updated_at` timestamps if available. Returns True if the user
    was active within the given minutes window.
    """
    from django.utils import timezone
    import datetime

    now = timezone.now()
    # Prefer explicit last_seen timestamp if available
    if getattr(user, 'last_seen', None):
        return (now - user.last_seen) <= datetime.timedelta(minutes=minutes)
    last_activity_candidates = []

    if getattr(user, 'last_login', None):
        last_activity_candidates.append(user.last_login)

    if hasattr(user, 'updated_at'):
        last_activity_candidates.append(user.updated_at)

    if not last_activity_candidates:
        return False

    most_recent = max(last_activity_candidates)
    return (now - most_recent) <= datetime.timedelta(minutes=minutes)


@receiver(post_save, sender=Message)
def notify_recipient_on_message(sender, instance: Message, created, **kwargs):
    """Send email notification to recipient when a new chat message arrives.

    Only send email if:
    - Message is newly created
    - Recipient has `email_notifications` enabled
    - Recipient is not recently active (heuristic)
    """
    if not created:
        return

    try:
        chat_room: ChatRoom = instance.chat_room
        sender_user = instance.sender

        # Determine recipient
        if sender_user == chat_room.tenant:
            recipient = chat_room.landlord
        else:
            recipient = chat_room.tenant

        # Do not notify sender
        if recipient == sender_user:
            return

        # Respect recipient preferences
        if not getattr(recipient, 'email_notifications', True):
            return

        # Skip if recipient is recently active in-app
        if user_is_active_recently(recipient, minutes=15):
            return

        # Build email context
        context = {
            'recipient': recipient,
            'sender': sender_user,
            'message': instance,
            'chat_room': chat_room,
            'site_url': getattr(settings, 'SITE_URL', '').rstrip('/'),
        }

        # Choose template based on recipient type
        if recipient.is_landlord():
            template_name = 'emails/chat_message_landlord.html'
            subject = f'New message from {sender_user.get_full_name_or_username()} regarding {chat_room.property.title}'
        else:
            template_name = 'emails/chat_message_tenant.html'
            subject = f'New message from {sender_user.get_full_name_or_username()} about {chat_room.property.title}'

        html_message = render_to_string(template_name, context)
        plain_message = strip_tags(html_message)

        # If django-q is available, queue the email sending task
        if async_task:
            try:
                async_task(
                    'chat.tasks.send_chat_notification_email',
                    recipient.email,
                    subject,
                    plain_message,
                    html_message,
                )
            except Exception:
                # Fallback to synchronous send if queuing fails
                try:
                    from django.core.mail import send_mail
                    send_mail(
                        subject=subject,
                        message=plain_message,
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        recipient_list=[recipient.email],
                        html_message=html_message,
                        fail_silently=True,
                    )
                except Exception:
                    pass
        else:
            # No queue available — send synchronously (best-effort)
            try:
                from django.core.mail import send_mail
                send_mail(
                    subject=subject,
                    message=plain_message,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[recipient.email],
                    html_message=html_message,
                    fail_silently=True,
                )
            except Exception:
                pass

    except Exception:
        # Don't let notification failures interrupt message creation
        pass


@receiver(post_save, sender=ChatRoom)
def notify_on_chat_room_created(sender, instance: ChatRoom, created, **kwargs):
    """Send notification emails when a new chat room is created."""
    if not created:
        return
    
    try:
        from accounts.email_utils import send_chat_room_created
        from django.utils import timezone
        
        chat_room = instance
        initiator = chat_room.tenant if hasattr(chat_room, '_initiator_is_tenant') else chat_room.landlord
        recipient = chat_room.landlord if initiator == chat_room.tenant else chat_room.tenant
        property_obj = chat_room.property
        chat_url = reverse('chat:chat_room', kwargs={'room_id': chat_room.id})
        
        # Get the first message if available
        first_message = chat_room.messages.first()
        initial_message = first_message.content if first_message else None
        
        send_chat_room_created(
            recipient,
            initiator,
            property_obj,
            initial_message,
            chat_url,
            timezone.now(),
        )
    except Exception as e:
        print(f"Error sending chat room creation email: {e}")
