from django.contrib import admin
from .models import ChatSession, ChatMessage


@admin.register(ChatSession)
class ChatSessionAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'get_title', 'created_at', 'updated_at', 'is_active')
    list_filter = ('is_active', 'created_at', 'updated_at')
    search_fields = ('user__username', 'title')
    readonly_fields = ('created_at', 'updated_at')
    list_per_page = 20
    
    def get_title(self, obj):
        return obj.get_title()
    get_title.short_description = 'Title'


@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ('id', 'session', 'get_user', 'is_user', 'content_preview', 'model_used', 'tokens_used', 'created_at')
    list_filter = ('is_user', 'model_used', 'created_at')
    search_fields = ('content', 'session__user__username')
    readonly_fields = ('created_at',)
    list_per_page = 50
    
    def get_user(self, obj):
        return obj.session.user.username
    get_user.short_description = 'User'
    
    def content_preview(self, obj):
        return obj.content[:100] + "..." if len(obj.content) > 100 else obj.content
    content_preview.short_description = 'Content Preview'
