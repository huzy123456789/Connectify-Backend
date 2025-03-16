from django.urls import path
from .views import (
    # Conversation views
    conversation_list, conversation_create, conversation_detail,
    conversation_update, conversation_delete, conversation_messages,
    conversation_send_message,
    
    # Group Chat views
    group_chat_list, group_chat_create, group_chat_detail,
    group_chat_update, group_chat_delete, group_chat_messages,
    group_chat_send_message, group_chat_add_members,
    group_chat_remove_member, group_chat_change_role,
    
    # Message views
    message_detail, message_delete, message_edit,
    message_react, message_unreact,
    
    # User Block views
    user_block_list, user_block_create, user_block_detail, user_block_delete
)

app_name = 'messaging'

urlpatterns = [
    # Conversation URLs
    path('conversations/', conversation_list, name='conversation-list'),
    path('conversations/create/', conversation_create, name='conversation-create'),
    path('conversations/<int:pk>/', conversation_detail, name='conversation-detail'),
    path('conversations/<int:pk>/update/', conversation_update, name='conversation-update'),
    path('conversations/<int:pk>/delete/', conversation_delete, name='conversation-delete'),
    path('conversations/<int:pk>/messages/', conversation_messages, name='conversation-messages'),
    path('conversations/<int:pk>/send-message/', conversation_send_message, name='conversation-send-message'),
    
    # Group Chat URLs
    path('group-chats/', group_chat_list, name='group-chat-list'),
    path('group-chats/create/', group_chat_create, name='group-chat-create'),
    path('group-chats/<int:pk>/', group_chat_detail, name='group-chat-detail'),
    path('group-chats/<int:pk>/update/', group_chat_update, name='group-chat-update'),
    path('group-chats/<int:pk>/delete/', group_chat_delete, name='group-chat-delete'),
    path('group-chats/<int:pk>/messages/', group_chat_messages, name='group-chat-messages'),
    path('group-chats/<int:pk>/send-message/', group_chat_send_message, name='group-chat-send-message'),
    path('group-chats/<int:pk>/add-members/', group_chat_add_members, name='group-chat-add-members'),
    path('group-chats/<int:pk>/remove-member/', group_chat_remove_member, name='group-chat-remove-member'),
    path('group-chats/<int:pk>/change-role/', group_chat_change_role, name='group-chat-change-role'),
    
    # Message URLs
    path('messages/<int:pk>/', message_detail, name='message-detail'),
    path('messages/<int:pk>/delete/', message_delete, name='message-delete'),
    path('messages/<int:pk>/edit/', message_edit, name='message-edit'),
    path('messages/<int:pk>/react/', message_react, name='message-react'),
    path('messages/<int:pk>/unreact/', message_unreact, name='message-unreact'),
    
    # User Block URLs
    path('blocks/', user_block_list, name='user-block-list'),
    path('blocks/create/', user_block_create, name='user-block-create'),
    path('blocks/<int:pk>/', user_block_detail, name='user-block-detail'),
    path('blocks/<int:pk>/delete/', user_block_delete, name='user-block-delete'),
] 