import json
import logging
import asyncio
from django.utils import timezone
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import Conversation, Message, MessageReadStatus, MessageDeliveryStatus

logger = logging.getLogger(__name__)

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope["user"]
        # Initialize attributes to avoid attribute errors
        self.conversations = []
        self.user_channel = f"user_{self.user.id}" if self.user.is_authenticated else None
        
        if not self.user.is_authenticated:
            await self.close(code=4003)
            return

        # Generate unique client ID
        self.client_id = f"user_{self.user.id}_{id(self)}"
        
        # Create a personal channel for this user
        await self.channel_layer.group_add(self.user_channel, self.channel_name)
        
        # Subscribe to all user's conversations
        self.conversations = await self.get_user_conversations()
        for conv_id in self.conversations:
            channel_name = f"conversation_{conv_id}"
            await self.channel_layer.group_add(channel_name, self.channel_name)
        
        # Start heartbeat and message queue handler
        self.message_queue = asyncio.Queue()
        self.heartbeat_task = asyncio.create_task(self.send_heartbeat())
        self.queue_handler = asyncio.create_task(self.handle_message_queue())
        
        await self.accept()
        
        # Store online status in cache
        await self.store_user_in_cache()
        
        # Send initial online status to all conversations
        await self.broadcast_status(True)

    async def disconnect(self, close_code):
        # Cancel background tasks first
        if hasattr(self, 'heartbeat_task') and not self.heartbeat_task.cancelled():
            self.heartbeat_task.cancel()
        if hasattr(self, 'queue_handler') and not self.queue_handler.cancelled():
            self.queue_handler.cancel()

        # Remove online status from cache before broadcasting offline status
        await self.remove_user_from_cache()
        
        # Broadcast offline status
        try:
            await self.broadcast_status(False)
        except Exception as e:
            logger.error(f"Error broadcasting offline status: {str(e)}")

        # Leave all conversation groups
        for conv_id in self.conversations:
            try:
                channel_name = f"conversation_{conv_id}"
                await self.channel_layer.group_discard(channel_name, self.channel_name)
            except Exception as e:
                logger.error(f"Error leaving group {channel_name}: {str(e)}")

        # Leave personal channel only if it is valid
        if self.user_channel:
            try:
                await self.channel_layer.group_discard(self.user_channel, self.channel_name)
            except Exception as e:
                logger.error(f"Error leaving personal channel {self.user_channel}: {str(e)}")

        logger.info(f"WebSocket disconnected for user {self.user.id if self.user.is_authenticated else 'Anonymous'}")

    async def receive(self, text_data):
        try:
            print(f"Received data from client {self.client_id}: {text_data}")
            data = json.loads(text_data)
            action = data.get('action')
            
            handlers = {
                'send_message': self.handle_new_message,
                'typing': self.handle_typing,
                'read': self.handle_read_receipt,
                'heartbeat_ack': self.handle_heartbeat,
                'fetch_messages': self.handle_fetch_messages,
                'heartbeat': self.handle_heartbeat,
                'message_status': self.message_status,
                'typing_indicator': self.typing_indicator,
                'message_read': self.message_read,
                'request_status': self.handle_request_status,  # Add new handler
                'broadcast_status': self.handle_broadcast_status,  # Add new handler
            }
            
            handler = handlers.get(action)
            if handler:
                await handler(data)
            else:
                logger.warning(f"Unknown action: {action}")
                
        except json.JSONDecodeError:
            logger.error("Invalid JSON received")
        except Exception as e:
            logger.error(f"Error processing message: {str(e)}")

    async def handle_request_status(self, data):
        """Handle request for participant statuses in a conversation"""
        conversation_id = data.get('conversation_id')
        
        if not conversation_id:
            logger.error("Invalid request_status data: Missing conversation_id")
            return
        
        try:
            # Fetch participant statuses
            statuses = await self.get_participant_statuses(conversation_id)
            
            # Send response back to the client
            await self.send(text_data=json.dumps({
                "type": "status_response",
                "statuses": statuses
            }))
        except Exception as e:
            logger.error(f"Error handling request_status for conversation {conversation_id}: {str(e)}")

    @database_sync_to_async
    def get_participant_statuses(self, conversation_id):
        """Fetch statuses of all participants in a conversation"""
        from .models import Conversation  # Ensure Conversation model is imported
        from django.core.cache import cache  # Use Django's cache framework (e.g., Redis)

        try:
            conversation = Conversation.objects.filter(id=conversation_id).first()
            if not conversation:
                logger.error(f"Conversation with id {conversation_id} does not exist")
                return []
            
            # Fetch participants and their statuses
            participants = conversation.participants.all()
            statuses = []
            for participant in participants:
                # Fetch online status from cache (or replace with actual logic)
                is_online = cache.get(f"user_{participant.id}_online", False)
                last_status_update = cache.get(f"user_{participant.id}_last_status_update", None)
                
                status = {
                    "user_id": participant.id,
                    "status": "online" if is_online else "offline",
                    "timestamp": last_status_update
                }
                statuses.append(status)
            
            return statuses
        except Exception as e:
            logger.error(f"Error fetching participant statuses for conversation {conversation_id}: {str(e)}")
            return []
    
    @database_sync_to_async
    def save_message(self, conversation_id, content):
        from django.db import transaction
        from .models import Conversation  # Ensure Conversation model is imported
        
        try:
            with transaction.atomic():
                # Validate conversation
                conversation = Conversation.objects.filter(id=conversation_id).first()
                if not conversation:
                    logger.error(f"Conversation with id {conversation_id} does not exist")
                    return None
                
                # Check if the user is a participant in the conversation
                if not conversation.participants.filter(id=self.user.id).exists():
                    logger.error(f"User {self.user.id} is not a participant in conversation {conversation_id}")
                    return None
                
                # Create message
                message = Message.objects.create(
                    conversation=conversation,
                    sender=self.user,
                    content=content,
                    sent_at=timezone.now()
                )
                
                # Create delivery status
                MessageDeliveryStatus.objects.create(
                    message=message,
                    status='sent',
                    timestamp=timezone.now()
                )
                
                return message
                
        except Exception as e:
            logger.error(f"Failed to save message: {str(e)}")
            return None

    async def update_message_status(self, message_id, status):
        await self.save_message_status(message_id, status)
        
        # Notify sender about status update
        await self.channel_layer.group_send(
            f"user_{self.user.id}",
            {
                'type': 'message.status',
                'message_id': message_id,
                'status': status,
                'timestamp': timezone.now().isoformat()
            }
        )

    @database_sync_to_async
    def save_message_status(self, message_id, status):
        try:
            message = Message.objects.get(id=message_id)
            MessageDeliveryStatus.objects.create(
                message=message,
                status=status,
                timestamp=timezone.now()
            )
        except Message.DoesNotExist:
            logger.error(f"Message {message_id} not found for status update")

    async def handle_new_message(self, data):
        conversation_id = data.get('conversation_id')
        content = data.get('content')
        local_id = data.get('local_id')  # Client-side message ID for tracking
        
        if not content or not conversation_id:
            logger.error("Invalid message data: Missing content or conversation_id")
            return
        
        try:
            # Save message to database
            message = await self.save_message(conversation_id, content)
            
            if not message:
                logger.error(f"Failed to save message for conversation_id {conversation_id}")
                await self.send(text_data=json.dumps({
                    'type': 'message.failed',
                    'local_id': local_id,
                    'error': 'Failed to save message'
                }))
                return
            
            # Send to conversation channel
            await self.channel_layer.group_send(
                f"conversation_{conversation_id}",
                {
                    'type': 'chat.message',
                    'message': {
                        'id': message.id,
                        'local_id': local_id,
                        'sender_id': self.user.id,
                        'content': content,
                        'timestamp': message.sent_at.isoformat(),
                        'status': 'sent'
                    }
                }
            )
            
            # Update message status to sent
            await self.update_message_status(message.id, 'sent')
            
        except Exception as e:
            # Notify sender about failure
            await self.send(text_data=json.dumps({
                'type': 'message.failed',
                'local_id': local_id,
                'error': str(e)
            }))
            logger.error(f"Failed to process message: {str(e)}")

    async def message_status(self, event):
        """Handle message status updates"""
        await self.send(text_data=json.dumps({
            'type': 'message.status',
            'message_id': event['message_id'],
            'status': event['status'],
            'timestamp': event['timestamp']
        }))

    @database_sync_to_async
    def get_user_conversations(self):
        return list(Conversation.objects.filter(
            participants=self.user
        ).values_list('id', flat=True))

    async def user_status(self, event):
        """Handle user online/offline status updates"""
        try:
            await self.send(text_data=json.dumps({
                'type': 'user_status',  # Match the frontend expected type
                'user_id': event['user_id'],
                'status': event['status'],
                'timestamp': event['timestamp']
            }))
        except Exception as e:
            logger.error(f"Error sending user status to {self.client_id}: {str(e)}")

    async def broadcast_status(self, is_online):
        """Modified to use correct message type"""
        for conv_id in self.conversations:
            await self.channel_layer.group_send(
                f"conversation_{conv_id}",
                {
                    'type': 'user_status',  # Changed from user.status to user_status
                    'user_id': self.user.id,
                    'status': 'online' if is_online else 'offline',
                    'timestamp': timezone.now().isoformat()
                }
            )

    async def send_heartbeat(self):
        """Send periodic heartbeats to keep connections alive"""
        try:
            while True:
                await asyncio.sleep(30)  # Send heartbeat every 30 seconds
                
                # Create heartbeat message
                heartbeat_time = timezone.now()
                heartbeat_message = {
                    "type": "heartbeat",
                    "timestamp": heartbeat_time.isoformat(),
                    "connection_id": self.client_id
                }
                
                # Send heartbeat
                try:
                    await self.send(text_data=json.dumps(heartbeat_message))
                    logger.debug(f"Heartbeat sent to {self.client_id}")
                except Exception as e:
                    logger.error(f"Failed to send heartbeat to {self.client_id}: {str(e)}")
                    
        except asyncio.CancelledError:
            logger.debug(f"Heartbeat task cancelled for {self.client_id}")
        except Exception as e:
            logger.error(f"Error in heartbeat task for {self.client_id}: {str(e)}")
    
    async def handle_message_queue(self):
        """Process messages from the queue and send them to the WebSocket"""
        try:
            while True:
                # Get message from queue
                message = await self.message_queue.get()
                
                # Send message to WebSocket
                await self.send(text_data=json.dumps(message))
                
                # Mark message as processed
                self.message_queue.task_done()
                
        except asyncio.CancelledError:
            logger.debug(f"Message queue handler cancelled for {self.client_id}")
        except Exception as e:
            logger.error(f"Error in message queue handler for {self.client_id}: {str(e)}")
    
    async def chat_message(self, event):
        """Forward chat messages to the WebSocket"""
        try:
            message = event['message']
            
            await self.send(text_data=json.dumps({
                'type': 'chat_message',
                'message': message
            }))
        except Exception as e:
            logger.error(f"Error sending chat message to {self.client_id}: {str(e)}")
    
    async def typing_indicator(self, event):
        """Forward typing indicators to the WebSocket"""
        try:
            await self.send(text_data=json.dumps({
                'type': 'typing',
                'user_id': event['user_id'],
                'username': event['username'],
                'is_typing': event['is_typing']
            }))
        except Exception as e:
            logger.error(f"Error sending typing indicator to {self.client_id}: {str(e)}")
    
    async def message_read(self, event):
        """Forward read receipts to the WebSocket"""
        try:
            await self.send(text_data=json.dumps({
                'type': 'read',
                'user_id': event['user_id'],
                'message_ids': event['message_ids']
            }))
        except Exception as e:
            logger.error(f"Error sending read receipt to {self.client_id}: {str(e)}")
    
    async def has_access(self):
        """Override in subclasses to check access permissions"""
        return False
    
    @database_sync_to_async
    def mark_messages_read(self, message_ids):
        """Mark messages as read by current user"""
        for message_id in message_ids:
            try:
                message = Message.objects.get(id=message_id)
                if message.sender_id != self.user.id:  # Don't mark own messages
                    MessageReadStatus.objects.get_or_create(
                        message=message,
                        user=self.user
                    )
            except Message.DoesNotExist:
                logger.warning(f"Message {message_id} not found for read status")

    async def handle_typing(self, data):
        """Handle typing indicator from client"""
        conversation_id = data.get('conversation_id')
        is_typing = data.get('is_typing', False)  # Ensure is_typing is assigned before use
        username = getattr(self.user, 'username', None)

        # Debugging log after variable assignment
        print(f"User {self.user.id} is typing: {is_typing}")

        if not conversation_id or username is None:
            return

        await self.channel_layer.group_send(
            f"conversation_{conversation_id}",
            {
                'type': 'typing_indicator',
                'user_id': self.user.id,
                'username': username,
                'is_typing': is_typing
            }
        )

    async def handle_read_receipt(self, data):
        """Handle read receipts from client"""
        message_ids = data.get('message_ids', [])
        conversation_id = data.get('conversation_id')
        
        if not message_ids or not conversation_id:
            return
            
        # Mark messages as read in the database
        await self.mark_messages_read(message_ids)
        
        # Notify other users in the conversation
        await self.channel_layer.group_send(
            f"conversation_{conversation_id}",
            {
                'type': 'message_read',
                'user_id': self.user.id,
                'message_ids': message_ids
            }
        )
        
        logger.debug(f"User {self.user.id} marked messages {message_ids} as read")
    
    async def handle_heartbeat(self, data):
        """Handle heartbeat action from the client"""
        logger.debug(f"Heartbeat received from {self.client_id}")
        # Update the last heartbeat timestamp or perform any necessary logic
        self.last_heartbeat_ack = timezone.now()

    async def handle_fetch_messages(self, data):
        """Handle request to fetch messages"""
        conversation_id = data.get('conversation_id')
        before_id = data.get('before_id')
        limit = data.get('limit', 20)
        
        if not conversation_id:
            return
            
        # Fetch messages from the database
        messages = await self.get_messages(conversation_id, before_id, limit)
        
        # Send messages back to the client
        await self.send(text_data=json.dumps({
            'type': 'messages_fetched',
            'conversation_id': conversation_id,
            'messages': messages
        }))

    @database_sync_to_async
    def get_messages(self, conversation_id, before_id=None, limit=20):
        """Fetch messages from the database"""
        query = Message.objects.filter(conversation_id=conversation_id)
        
        if before_id:
            try:
                before_message = Message.objects.get(id=before_id)
                query = query.filter(sent_at__lt=before_message.sent_at)
            except Message.DoesNotExist:
                pass
                
        messages = list(query.order_by('-sent_at')[:limit].values(
            'id', 'sender_id', 'content', 'sent_at', 'is_edited', 'is_deleted'
        ))
        
        # Convert datetime objects to ISO format
        for message in messages:
            message['sent_at'] = message['sent_at'].isoformat()
            
        return messages

    async def handle_broadcast_status(self, data):
        """Handle broadcast_status action from the client"""
        conversation_id = data.get('conversation_id')
        status = data.get('status')
        timestamp = data.get('timestamp')

        if not conversation_id or not status or not timestamp:
            logger.error("Invalid broadcast_status data: Missing conversation_id, status, or timestamp")
            return

        try:
            # Broadcast the user's status to all participants in the conversation
            await self.channel_layer.group_send(
                f"conversation_{conversation_id}",
                {
                    'type': 'user_status',
                    'user_id': self.user.id,
                    'status': status,
                    'timestamp': timestamp
                }
            )
            logger.info(f"Broadcasted status {status} for user {self.user.id} in conversation {conversation_id}")
        except Exception as e:
            logger.error(f"Error broadcasting status for conversation {conversation_id}: {str(e)}")

    @database_sync_to_async
    def store_user_in_cache(self):
            """Store user's online status in cache"""
            from django.core.cache import cache
            # Store online status with 5 minute timeout (300 seconds)
            # This helps in case the connection is lost without proper disconnect
            cache.set(f"user_{self.user.id}_online", True, timeout=300)
            cache.set(f"user_{self.user.id}_last_status_update", timezone.now().isoformat(), timeout=300)
            logger.debug(f"User {self.user.id} marked as online in cache")

    @database_sync_to_async
    def remove_user_from_cache(self):
            """Remove user's online status from cache"""
            from django.core.cache import cache
            cache.delete(f"user_{self.user.id}_online")
            cache.delete(f"user_{self.user.id}_last_status_update")
            logger.debug(f"User {self.user.id} removed from online cache")

# Add a management command to get connection metrics
async def get_connection_metrics():
    """Return current WebSocket connection metrics"""
    return {
        'timestamp': timezone.now().isoformat(),
    }



