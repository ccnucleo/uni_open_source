from django.contrib import admin
from .models import Follow, Message

@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    list_display = ('follower', 'following', 'created_at')
    search_fields = ('follower__username', 'following__username')
    list_filter = ('created_at',)

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('sender', 'recipient', 'subject', 'is_read', 'created_at')
    search_fields = ('sender__username', 'recipient__username', 'subject', 'body')
    list_filter = ('is_read', 'created_at')
