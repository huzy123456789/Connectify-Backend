import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from accounts.models import User
from .models import Conversation, GroupChat, Message, MessageReadStatus, UserBlock


class BaseChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope["user"]
        
        if not self.user.is_authenticated:
            await self.close()
            return
        
        # Check if user has access to this chat
        if not await self.has_access():
            await self.close()
            return
        
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()
    
    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
    
    async def receive(self, text_data):
        data = json.loads(text_data)
        message_type = data.get('type', 'message')
        
        if message_type == 'message':
            await self.handle_message(data)
        elif message_type == 'typing':
            await self.handle_typing(data)
        elif message_type == 'read':
            await self.handle_read(data)
    
    async def handle_message(self, data):
        content = data.get('content')
        reply_to_id = data.get('reply_to')
        
        if not content:
            return
        
        # Save message to database
        message = await self.save_message(content, reply_to_id)
        
        # Send message to room group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': {
                    'id': message.id,
                    'sender_id': self.user.id,
                    'sender_username': self.user.username,
                    'content': content,
                    'created_at': message.created_at.isoformat(),
                    'reply_to': reply_to_id
                }
            }
        )
    
    async def handle_typing(self, data):
        is_typing = data.get('is_typing', False)
        
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'user_typing',
                'user_id': self.user.id,
                'username': self.user.username,
                'is_typing': is_typing
            }
        )
    
    async def handle_read(self, data):
        message_id = data.get('message_id')
        
        if not message_id:
            return
        
        # Mark message as read
        await self.mark_message_read(message_id)
        
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'message_read',
                'user_id': self.user.id,
                'message_id': message_id
            }
        )
    
    async def chat_message(self, event):
        message = event['message']
        
        await self.send(text_data=json.dumps({
            'type': 'message',
            'message': message
        }))
    
    async def user_typing(self, event):
        await self.send(text_data=json.dumps({
            'type': 'typing',
            'user_id': event['user_id'],
            'username': event['username'],
            'is_typing': event['is_typing']
        }))
    
    async def message_read(self, event):
        await self.send(text_data=json.dumps({
            'type': 'read',
            'user_id': event['user_id'],
            'message_id': event['message_id']
        }))
    
    async def has_access(self):
        # Override in subclasses
        return False
    
    async def save_message(self, content, reply_to_id):
        # Override in subclasses
        pass
    
    @database_sync_to_async
    def mark_message_read(self, message_id):
        try:
            message = Message.objects.get(id=message_id)
            MessageReadStatus.objects.get_or_create(
                message=message,
                user=self.user
            )
        except Message.DoesNotExist:
            pass


class ConversationConsumer(BaseChatConsumer):
    async def connect(self):
        self.conversation_id = self.scope['url_route']['kwargs']['conversation_id']
        self.room_group_name = f'conversation_{self.conversation_id}'
        await super().connect()
    
    @database_sync_to_async
    def has_access(self):
        try:
            conversation = Conversation.objects.get(id=self.conversation_id)
            
            # Check if user is a participant
            if not conversation.participants.filter(id=self.user.id).exists():
                return False
            
            # Check if user is blocked
            other_participant = conversation.participants.exclude(id=self.user.id).first()
            if UserBlock.objects.filter(
                blocker=other_participant,
                blocked=self.user,
                organization=conversation.organization
            ).exists():
                return False
            
            self.conversation = conversation
            return True
        except Conversation.DoesNotExist:
            return False
    
    @database_sync_to_async
    def save_message(self, content, reply_to_id):
        reply_to = None
        if reply_to_id:
            try:
                reply_to = Message.objects.get(id=reply_to_id)
            except Message.DoesNotExist:
                pass
        
        message = Message.objects.create(
            conversation=self.conversation,
            sender=self.user,
            content=content,
            reply_to=reply_to
        )
        return message


class GroupChatConsumer(BaseChatConsumer):
    async def connect(self):
        self.group_chat_id = self.scope['url_route']['kwargs']['group_chat_id']
        self.room_group_name = f'group_chat_{self.group_chat_id}'
        await super().connect()
    
    @database_sync_to_async
    def has_access(self):
        try:
            group_chat = GroupChat.objects.get(id=self.group_chat_id)
            
            # Check if user is a member
            if not group_chat.members.filter(id=self.user.id).exists():
                return False
            
            self.group_chat = group_chat
            return True
        except GroupChat.DoesNotExist:
            return False
    
    @database_sync_to_async
    def save_message(self, content, reply_to_id):
        reply_to = None
        if reply_to_id:
            try:
                reply_to = Message.objects.get(id=reply_to_id)
            except Message.DoesNotExist:
                pass
        
        message = Message.objects.create(
            group_chat=self.group_chat,
            sender=self.user,
            content=content,
            reply_to=reply_to
        )
        return message 