from django.urls import path
from . import consumers

websocket_urlpatterns = [
    path('ws/conversations/<int:conversation_id>/', consumers.ConversationConsumer.as_asgi()),
    path('ws/group-chats/<int:group_chat_id>/', consumers.GroupChatConsumer.as_asgi()),
] 