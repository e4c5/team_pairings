from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class ChatSession(models.Model):
    """
    Represents a chat session for a user.
    Each user can have multiple chat sessions.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='chat_sessions')
    title = models.CharField(max_length=200, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['-updated_at']

    def __str__(self):
        return f"Chat Session {self.id} - {self.user.username}"

    def get_title(self):
        """Get session title or generate from first message"""
        if self.title:
            return self.title
        first_message = self.messages.filter(is_user=True).first()
        if first_message:
            return first_message.content[:50] + "..." if len(first_message.content) > 50 else first_message.content
        return f"Chat Session {self.id}"


class ChatMessage(models.Model):
    """
    Represents a single message in a chat session.
    Can be from user or AI assistant.
    """
    session = models.ForeignKey(ChatSession, on_delete=models.CASCADE, related_name='messages')
    content = models.TextField()
    is_user = models.BooleanField(default=True)  # True for user messages, False for AI responses
    created_at = models.DateTimeField(auto_now_add=True)
    
    # Optional fields for AI responses
    model_used = models.CharField(max_length=100, blank=True, null=True)
    tokens_used = models.IntegerField(blank=True, null=True)
    response_time = models.FloatField(blank=True, null=True)  # in seconds

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        sender = "User" if self.is_user else "AI"
        content_preview = self.content[:50] + "..." if len(self.content) > 50 else self.content
        return f"{sender}: {content_preview}"
