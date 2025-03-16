from django.contrib import admin
from .models import (
    Conversation, GroupChat, GroupChatMembership, Message, 
    MessageReaction, MessageAttachment, MessageReadStatus, UserBlock
)

@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = ('id', 'organization', 'created_at', 'updated_at', 'is_active')
    list_filter = ('is_active', 'organization')
    search_fields = ('id', 'organization__name')
    date_hierarchy = 'created_at'
    filter_horizontal = ('participants',)


@admin.register(GroupChat)
class GroupChatAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'organization', 'created_by', 'created_at', 'updated_at', 'is_active')
    list_filter = ('is_active', 'organization')
    search_fields = ('id', 'name', 'organization__name', 'created_by__username')
    date_hierarchy = 'created_at'


@admin.register(GroupChatMembership)
class GroupChatMembershipAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'group_chat', 'role', 'joined_at', 'is_muted')
    list_filter = ('role', 'is_muted', 'group_chat')
    search_fields = ('user__username', 'group_chat__name')
    date_hierarchy = 'joined_at'


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('id', 'get_chat_type', 'sender', 'content_preview', 'created_at', 'is_edited', 'is_deleted', 'reaction_count')
    list_filter = ('is_edited', 'is_deleted')
    search_fields = ('content', 'sender__username')
    date_hierarchy = 'created_at'
    
    def get_chat_type(self, obj):
        if obj.conversation:
            return f"Conversation {obj.conversation.id}"
        return f"Group {obj.group_chat.id}"
    get_chat_type.short_description = 'Chat'
    
    def content_preview(self, obj):
        return obj.content[:50] + ('...' if len(obj.content) > 50 else '')
    content_preview.short_description = 'Content'


@admin.register(MessageReaction)
class MessageReactionAdmin(admin.ModelAdmin):
    list_display = ('id', 'message', 'user', 'emoji', 'created_at')
    list_filter = ('emoji',)
    search_fields = ('user__username', 'message__content')
    date_hierarchy = 'created_at'


@admin.register(MessageAttachment)
class MessageAttachmentAdmin(admin.ModelAdmin):
    list_display = ('id', 'message', 'attachment_type', 'file_name', 'file_size', 'uploaded_at')
    list_filter = ('attachment_type',)
    search_fields = ('file_name', 'message__content')
    date_hierarchy = 'uploaded_at'


@admin.register(MessageReadStatus)
class MessageReadStatusAdmin(admin.ModelAdmin):
    list_display = ('id', 'message', 'user', 'read_at')
    search_fields = ('user__username', 'message__content')
    date_hierarchy = 'read_at'


@admin.register(UserBlock)
class UserBlockAdmin(admin.ModelAdmin):
    list_display = ('id', 'blocker', 'blocked', 'organization', 'created_at')
    list_filter = ('organization',)
    search_fields = ('blocker__username', 'blocked__username', 'organization__name')
    date_hierarchy = 'created_at'
