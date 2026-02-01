from django.db import models
from django.conf import settings

class ChatRoom(models.Model):
    property = models.ForeignKey('properties.Property', on_delete=models.CASCADE, related_name='chat_rooms')
    tenant = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='tenant_chats')
    landlord = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='landlord_chats')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['property', 'tenant', 'landlord']
        ordering = ['-updated_at']
        indexes = [
            models.Index(fields=['tenant', '-updated_at']),
            models.Index(fields=['landlord', '-updated_at']),
            models.Index(fields=['property']),
        ]
    
    def __str__(self):
        return f"Chat: {self.tenant.username} <-> {self.landlord.username} - {self.property.title}"


class Message(models.Model):
    chat_room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    content = models.TextField()
    
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['created_at']
        indexes = [
            models.Index(fields=['chat_room', '-created_at']),
            models.Index(fields=['is_read', '-created_at']),
            models.Index(fields=['sender']),
        ]
    
    def __str__(self):
        return f"{self.sender.username}: {self.content[:50]}"