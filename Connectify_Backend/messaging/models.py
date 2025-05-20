from django.db import models
from django.conf import settings
from django.utils import timezone
from organizations.models import Organization

class Conversation(models.Model):
    """
    Model representing a one-to-one conversation between two users.
    """
    participants = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='conversations')
    organization = models.ForeignKey(
        Organization, 
        on_delete=models.CASCADE, 
        related_name='conversations',
        help_text="Both users must belong to this organization"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['-updated_at']
    
    def __str__(self):
        return f"Conversation in {self.organization.name} ({self.id})"


class GroupChat(models.Model):
    """
    Model representing a group chat with multiple participants.
    """
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    organization = models.ForeignKey(
        Organization, 
        on_delete=models.CASCADE, 
        related_name='group_chats',
        help_text="All members must belong to this organization"
    )
    members = models.ManyToManyField(
        settings.AUTH_USER_MODEL, 
        related_name='group_chats',
        through='GroupChatMembership'
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        related_name='created_group_chats',
        null=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    avatar = models.ImageField(upload_to='group_chat_avatars/', blank=True, null=True)
    
    class Meta:
        ordering = ['-updated_at']
    
    def __str__(self):
        return f"{self.name} ({self.id})"


class GroupChatMembership(models.Model):
    """
    Model representing a user's membership in a group chat.
    """
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('member', 'Member'),
    ]
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    group_chat = models.ForeignKey(GroupChat, on_delete=models.CASCADE)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='member')
    joined_at = models.DateTimeField(auto_now_add=True)
    is_muted = models.BooleanField(default=False)
    
    class Meta:
        unique_together = ['user', 'group_chat']
    
    def __str__(self):
        return f"{self.user.username} in {self.group_chat.name} as {self.role}"


class Message(models.Model):
    """
    Model representing a message in a conversation or group chat.
    """
    conversation = models.ForeignKey(
        Conversation, 
        on_delete=models.CASCADE, 
        related_name='messages',
        null=True, 
        blank=True
    )
    group_chat = models.ForeignKey(
        GroupChat, 
        on_delete=models.CASCADE, 
        related_name='messages',
        null=True, 
        blank=True
    )
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='sent_messages'
    )
    content = models.TextField()
    sent_at = models.DateTimeField(default=timezone.now)
    delivered_at = models.DateTimeField(null=True, blank=True)
    read_at = models.DateTimeField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_edited = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)
    reply_to = models.ForeignKey(
        'self', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='replies'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    # Counters for performance optimization
    reaction_count = models.PositiveIntegerField(default=0)
    
    class Meta:
        ordering = ['-sent_at']  # Changed from created_at to sent_at and reversed order
    
    def __str__(self):
        chat_type = "conversation" if self.conversation else "group"
        chat_id = self.conversation.id if self.conversation else self.group_chat.id
        return f"Message by {self.sender.username} in {chat_type} {chat_id}"
    
    def save(self, *args, **kwargs):
        # Ensure message belongs to either a conversation or a group chat, not both
        if self.conversation and self.group_chat:
            raise ValueError("Message cannot belong to both a conversation and a group chat")
        if not self.conversation and not self.group_chat:
            raise ValueError("Message must belong to either a conversation or a group chat")
        
        # Update the parent's updated_at timestamp
        if self.conversation:
            self.conversation.updated_at = self.created_at
            self.conversation.save(update_fields=['updated_at'])
        elif self.group_chat:
            self.group_chat.updated_at = self.created_at
            self.group_chat.save(update_fields=['updated_at'])
            
        super().save(*args, **kwargs)


class MessageReaction(models.Model):
    """
    Model representing a reaction to a message.
    """
    message = models.ForeignKey(Message, on_delete=models.CASCADE, related_name='reactions')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='message_reactions')
    emoji = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['message', 'user', 'emoji']
    
    def __str__(self):
        return f"{self.user.username} reacted with {self.emoji} to message {self.message.id}"
    
    def save(self, *args, **kwargs):
        created = not self.pk
        super().save(*args, **kwargs)
        
        # Update reaction count on message
        if created:
            self.message.reaction_count = MessageReaction.objects.filter(message=self.message).count()
            self.message.save(update_fields=['reaction_count'])


class MessageAttachment(models.Model):
    """
    Model for storing attachments (images/videos/documents) associated with messages.
    """
    ATTACHMENT_TYPES = [
        ('image', 'Image'),
        ('video', 'Video'),
        ('document', 'Document'),
        ('audio', 'Audio'),
    ]
    
    message = models.ForeignKey(Message, on_delete=models.CASCADE, related_name='attachments')
    file = models.FileField(upload_to='message_attachments/')
    attachment_type = models.CharField(max_length=10, choices=ATTACHMENT_TYPES)
    file_name = models.CharField(max_length=255)
    file_size = models.PositiveIntegerField(help_text="File size in bytes")
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.attachment_type} attachment for message {self.message.id}"


class MessageReadStatus(models.Model):
    """
    Model to track which users have read which messages.
    """
    message = models.ForeignKey(Message, on_delete=models.CASCADE, related_name='read_status')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='read_messages')
    read_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['message', 'user']
    
    def __str__(self):
        return f"Message {self.message.id} read by {self.user.username}"


class UserBlock(models.Model):
    """
    Model representing a user blocking another user from messaging.
    """
    blocker = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='blocked_users'
    )
    blocked = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='blocked_by'
    )
    organization = models.ForeignKey(
        Organization, 
        on_delete=models.CASCADE, 
        related_name='user_blocks',
        help_text="Organization context for this block"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['blocker', 'blocked', 'organization']
    
    def __str__(self):
        return f"{self.blocker.username} blocked {self.blocked.username} in {self.organization.name}"


class MessageDeliveryStatus(models.Model):
    STATUS_CHOICES = [
        ('sending', 'Sending'),
        ('sent', 'Sent'),
        ('delivered', 'Delivered'),
        ('read', 'Read'),
        ('failed', 'Failed')
    ]
    
    message = models.ForeignKey(Message, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    timestamp = models.DateTimeField(default=timezone.now)
    
    class Meta:
        ordering = ['-timestamp']
