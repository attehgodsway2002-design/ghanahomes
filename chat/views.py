from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from .models import ChatRoom, Message
from .forms import MessageForm
from properties.models import Property

@login_required
def chat_list(request):
    """List all user's chat rooms"""
    if request.user.is_landlord():
        chat_rooms = ChatRoom.objects.filter(landlord=request.user).order_by('-updated_at')
    else:
        chat_rooms = ChatRoom.objects.filter(tenant=request.user).order_by('-updated_at')
    
    # Add unread counts to chat rooms
    for room in chat_rooms:
        room.unread_count = room.messages.filter(is_read=False).exclude(sender=request.user).count()
    
    context = {
        'chat_rooms': chat_rooms,
    }
    
    return render(request, 'chat/chat_list.html', context)


@login_required
def chat_room(request, room_id):
    """Chat room view"""
    chat_room = get_object_or_404(ChatRoom, id=room_id)
    
    # Check access permission
    if request.user != chat_room.tenant and request.user != chat_room.landlord:
        messages.error(request, 'Access denied.')
        return redirect('chat:chat_list')
    
    # Mark messages as read
    unread_messages = Message.objects.filter(
        chat_room=chat_room,
        is_read=False
    ).exclude(sender=request.user)
    unread_messages.update(is_read=True)
    
    messages_list = Message.objects.filter(chat_room=chat_room).order_by('created_at')
    
    context = {
        'chat_room': chat_room,
        'messages': messages_list,
        'form': MessageForm(),
    }
    
    return render(request, 'chat/chat_room.html', context)


@login_required
def start_chat(request, property_id):
    """Start a new chat about a property"""
    property = get_object_or_404(Property, id=property_id)
    
    if request.user == property.owner:
        messages.error(request, 'You cannot chat with yourself about your own property.')
        return redirect('properties:property_detail', slug=property.slug)
    
    # Check if chat room already exists
    chat_room, created = ChatRoom.objects.get_or_create(
        property=property,
        tenant=request.user,
        landlord=property.owner
    )
    
    if created:
        # Send initial message
        initial_message = f"Hi! I'm interested in your property: {property.title}"
        Message.objects.create(
            chat_room=chat_room,
            sender=request.user,
            content=initial_message
        )
        
        # Send admin notification for new inquiry
        try:
            from accounts.email_utils import send_admin_new_inquiry
            send_admin_new_inquiry(chat_room, initial_message, request)
        except Exception as e:
            print(f"Error sending admin inquiry notification: {e}")
    
    return redirect('chat:chat_room', room_id=chat_room.id)


# API endpoint for sending messages (AJAX)
@login_required
def send_message(request, room_id):
    """Send message via AJAX"""
    if request.method == 'POST':
        chat_room = get_object_or_404(ChatRoom, id=room_id)
        
        # Check access
        if request.user not in [chat_room.tenant, chat_room.landlord]:
            return JsonResponse({'error': 'Access denied'}, status=403)
        
        content = request.POST.get('content', '').strip()
        
        if content:
            message = Message.objects.create(
                chat_room=chat_room,
                sender=request.user,
                content=content
            )
            
            # Update chat room timestamp
            chat_room.save()  # This will update updated_at
            
            return JsonResponse({
                'success': True,
                'message': {
                    'id': message.id,
                    'content': message.content,
                    'sender': message.sender.username,
                    'created_at': message.created_at.strftime('%H:%M'),
                }
            })
        
        return JsonResponse({'error': 'Empty message'}, status=400)
    
    return JsonResponse({'error': 'Invalid request'}, status=405)