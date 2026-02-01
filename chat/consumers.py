import json
import asyncio
import contextlib
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import ChatRoom, Message
from django.utils import timezone


@database_sync_to_async
def _mark_user_last_seen(user_id):
    try:
        from accounts.models import User
        u = User.objects.filter(id=user_id).first()
        if u:
            u.last_seen = timezone.now()
            u.save(update_fields=['last_seen'])
    except Exception:
        # Best-effort; don't raise in async code
        pass

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_id = self.scope['url_route']['kwargs']['room_id']
        self.room_group_name = f'chat_{self.room_id}'

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        # Mark user as active now
        user = self.scope.get('user')
        if user and getattr(user, 'is_authenticated', False):
            await _mark_user_last_seen(user.id)

            # Start heartbeat task to refresh last_seen periodically
            self._heartbeat_interval = 60  # seconds; adjust as needed
            self._heartbeat_task = asyncio.create_task(self._heartbeat_loop(user.id))

        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
        # Cancel heartbeat task and mark user last seen on disconnect
        try:
            task = getattr(self, '_heartbeat_task', None)
            if task and not task.done():
                task.cancel()
                # allow cancellation to propagate
                with contextlib.suppress(asyncio.CancelledError):
                    await task
        except Exception:
            pass

        user = self.scope.get('user')
        if user and getattr(user, 'is_authenticated', False):
            await _mark_user_last_seen(user.id)

    async def receive(self, text_data):
        data = json.loads(text_data)
        message = data['message']
        user_id = data['user_id']

        # Save message to database
        await self.save_message(user_id, message)

        # Send message to room group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message,
                'user_id': user_id,
            }
        )

    async def _heartbeat_loop(self, user_id: int):
        """Periodically update user's last_seen while the socket is open."""
        try:
            while True:
                await asyncio.sleep(self._heartbeat_interval)
                await _mark_user_last_seen(user_id)
        except asyncio.CancelledError:
            # Task cancelled on disconnect — exit silently
            return

    async def chat_message(self, event):
        message = event['message']
        user_id = event['user_id']

        await self.send(text_data=json.dumps({
            'message': message,
            'user_id': user_id,
        }))

    @database_sync_to_async
    def save_message(self, user_id, message):
        from accounts.models import User
        chat_room = ChatRoom.objects.get(id=self.room_id)
        sender = User.objects.get(id=user_id)
        Message.objects.create(
            chat_room=chat_room,
            sender=sender,
            content=message
        )