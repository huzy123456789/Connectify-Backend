from rest_framework import serializers
from django.contrib.auth import get_user_model
from organizations.models import Organization
from .models import (
    Conversation, GroupChat, GroupChatMembership, Message, 
    MessageReaction, MessageAttachment, MessageReadStatus, UserBlock,
    MessageDeliveryStatus
)

User = get_user_model()


class UserMinimalSerializer(serializers.ModelSerializer):
    """Minimal user information for messaging context"""
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'profile_image']


class OrganizationMinimalSerializer(serializers.ModelSerializer):
    """Minimal organization information for messaging context"""
    class Meta:
        model = Organization
        fields = ['id', 'name']


class MessageAttachmentSerializer(serializers.ModelSerializer):
    """Serializer for message attachments"""
    file_url = serializers.SerializerMethodField()
    
    class Meta:
        model = MessageAttachment
        fields = ['id', 'file_url', 'attachment_type', 'file_name', 'file_size', 'uploaded_at']
        read_only_fields = ['id', 'uploaded_at']
    
    def get_file_url(self, obj):
        return obj.file.url if obj.file else None


class MessageReactionSerializer(serializers.ModelSerializer):
    """Serializer for message reactions"""
    user = UserMinimalSerializer(read_only=True)
    
    class Meta:
        model = MessageReaction
        fields = ['id', 'user', 'emoji', 'created_at']
        read_only_fields = ['id', 'created_at']


class MessageReadStatusSerializer(serializers.ModelSerializer):
    """Serializer for message read status"""
    user = UserMinimalSerializer(read_only=True)
    
    class Meta:
        model = MessageReadStatus
        fields = ['id', 'user', 'read_at']
        read_only_fields = ['id', 'read_at']


class MessageDeliveryStatusSerializer(serializers.ModelSerializer):
    """Serializer for message delivery status"""
    
    class Meta:
        model = MessageDeliveryStatus
        fields = ['status', 'timestamp']


class MessageSerializer(serializers.ModelSerializer):
    """Serializer for messages"""
    sender = UserMinimalSerializer(read_only=True)
    attachments = MessageAttachmentSerializer(many=True, read_only=True)
    reactions = serializers.SerializerMethodField()
    read_by = serializers.SerializerMethodField()
    delivery_status = serializers.SerializerMethodField()
    reply_to_preview = serializers.SerializerMethodField()
    
    class Meta:
        model = Message
        fields = [
            'id', 'sender', 'content', 'created_at', 'updated_at', 
            'is_edited', 'is_deleted', 'attachments', 'reactions', 
            'reaction_count', 'read_by', 'reply_to', 'reply_to_preview',
            'delivery_status'
        ]
        read_only_fields = ['id', 'sender', 'created_at', 'updated_at', 'reaction_count']
    
    def get_reactions(self, obj):
        # Return only the first few reactions to avoid large payloads
        reactions = obj.reactions.all()[:10]
        return MessageReactionSerializer(reactions, many=True).data
    
    def get_read_by(self, obj):
        # Return users who have read this message
        read_statuses = obj.read_status.all()
        return MessageReadStatusSerializer(read_statuses, many=True).data
    
    def get_delivery_status(self, obj):
        latest_status = MessageDeliveryStatus.objects.filter(
            message=obj
        ).order_by('-timestamp').first()
        if latest_status:
            return MessageDeliveryStatusSerializer(latest_status).data
        return None
    
    def get_reply_to_preview(self, obj):
        # If this message is a reply, provide a preview of the original message
        if obj.reply_to:
            return {
                'id': obj.reply_to.id,
                'sender': UserMinimalSerializer(obj.reply_to.sender).data,
                'content': obj.reply_to.content[:100],  # Truncate long messages
                'has_attachments': obj.reply_to.attachments.exists()
            }
        return None


class MessageCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating messages"""
    attachments = serializers.ListField(
        child=serializers.FileField(),
        required=False,
        write_only=True
    )
    attachment_types = serializers.ListField(
        child=serializers.ChoiceField(choices=MessageAttachment.ATTACHMENT_TYPES),
        required=False,
        write_only=True
    )
    
    class Meta:
        model = Message
        fields = ['content', 'reply_to', 'attachments', 'attachment_types']
    
    def validate(self, data):
        # Validate that if attachments are provided, attachment_types must be provided too
        attachments = data.get('attachments', [])
        attachment_types = data.get('attachment_types', [])
        
        if attachments and not attachment_types:
            raise serializers.ValidationError("attachment_types must be provided when attachments are uploaded")
        
        if attachment_types and not attachments:
            raise serializers.ValidationError("attachments must be provided when attachment_types are specified")
        
        if len(attachments) != len(attachment_types):
            raise serializers.ValidationError("Number of attachments and attachment_types must match")
        
        return data


class ConversationSerializer(serializers.ModelSerializer):
    """Serializer for conversations"""
    participants = UserMinimalSerializer(many=True, read_only=True)
    organization = OrganizationMinimalSerializer(read_only=True)
    last_message = serializers.SerializerMethodField()
    unread_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Conversation
        fields = [
            'id', 'participants', 'organization', 'created_at', 
            'updated_at', 'is_active', 'last_message', 'unread_count'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
        def get_last_message(self, obj):
            # Get the most recent message in the group chat
            last_message = obj.messages.order_by('-created_at').first()
            if last_message:
                return {
                    'id': last_message.id,
                    'sender': UserMinimalSerializer(last_message.sender).data,
                    'content': last_message.content[:100],  # Truncate long messages
                    'created_at': last_message.created_at,
                    'is_deleted': last_message.is_deleted,
                    'has_attachments': last_message.attachments.exists()
                }
            return None

        def get_unread_count(self, obj):
            request = self.context.get('request')
            if not request or not request.user:
                return 0
            
            return obj.messages.exclude(
                read_status__user=request.user
            ).count()

        def get_user_role(self, obj):
            request = self.context.get('request')
            if not request or not request.user:
                return None
            
            membership = obj.memberships.filter(user=request.user).first()
            if membership:
                return membership.role
            return None

        def get_avatar_url(self, obj):
            # Placeholder method: can be customized to return an actual group avatar
            return obj.avatar.url if obj.avatar else None

    def get_unread_count(self, obj):
        # Get count of unread messages for the current user
        request = self.context.get('request')
        if not request or not request.user:
            return 0
        
        # Count messages that don't have a read status for this user
        return obj.messages.exclude(
            read_status__user=request.user
        ).count()


class ConversationDetailSerializer(ConversationSerializer):
    """Detailed serializer for conversations including messages"""
    messages = serializers.SerializerMethodField()
    
    class Meta(ConversationSerializer.Meta):
        fields = ConversationSerializer.Meta.fields + ['messages']
    
    def get_messages(self, obj):
        # Get paginated messages for the conversation
        # The actual pagination is handled in the view
        messages = self.context.get('messages', obj.messages.all())
        return MessageSerializer(messages, many=True).data


class ConversationCreateSerializer(serializers.Serializer):
    participant_id = serializers.IntegerField(write_only=True)
    organization_id = serializers.IntegerField(write_only=True)
    initial_message = serializers.CharField(required=False, write_only=True, allow_blank=True)

    def validate(self, data):
        user = self.context['request'].user
        participant_id = data.get('participant_id')
        organization_id = data.get('organization_id')

        # Validate participant exists
        try:
            participant = User.objects.get(id=participant_id)
        except User.DoesNotExist:
            raise serializers.ValidationError("Participant not found")

        # Validate organization exists
        try:
            organization = Organization.objects.get(id=organization_id)
        except Organization.DoesNotExist:
            raise serializers.ValidationError("Organization not found")

        # Check if users are in the organization
        if not organization.users.filter(id__in=[user.id, participant_id]).count() == 2:
            raise serializers.ValidationError("Both users must be members of the organization")

        # Check if conversation already exists
        existing_conversation = Conversation.objects.filter(
            participants=user
        ).filter(
            participants=participant_id
        ).filter(
            organization=organization,
            is_active=True
        ).first()

        if existing_conversation:
            raise serializers.ValidationError("Conversation already exists")

        return data


class GroupChatMembershipSerializer(serializers.ModelSerializer):
    """Serializer for group chat membership"""
    user = UserMinimalSerializer(read_only=True)
    
    class Meta:
        model = GroupChatMembership
        fields = ['id', 'user', 'role', 'joined_at', 'is_muted']
        read_only_fields = ['id', 'joined_at']


class GroupChatSerializer(serializers.ModelSerializer):
    """Serializer for group chats"""
    organization = OrganizationMinimalSerializer(read_only=True)
    created_by = UserMinimalSerializer(read_only=True)
    members_count = serializers.SerializerMethodField()
    last_message = serializers.SerializerMethodField()
    unread_count = serializers.SerializerMethodField()
    user_role = serializers.SerializerMethodField()
    avatar_url = serializers.SerializerMethodField()
    
    class Meta:
        model = GroupChat
        fields = [
            'id', 'name', 'description', 'organization', 'created_by',
            'created_at', 'updated_at', 'is_active', 'members_count',
            'last_message', 'unread_count', 'user_role', 'avatar_url'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'created_by']
    
    def get_members_count(self, obj):
        return obj.members.count()
    
    def get_last_message(self, obj):
        # Get the most recent message in the group chat
        last_message = obj.messages.order_by('-created_at').first()
        if last_message:
            return {
                'id': last_message.id,
                'sender': UserMinimalSerializer(last_message.sender).data,
                'content': last_message.content[:100],  # Truncate long messages
                'created_at': last_message.created_at,
                'is_deleted': last_message.is_deleted,
                'has_attachments': last_message.attachments.exists()
            }
        return None
    
    def get_unread_count(self, obj):
        # Get count of unread messages for the current user
        user = self.context.get('request').user
        if not user:
            return 0
        
        # Count messages that don't have a read status for this user
        return obj.messages.exclude(
            read_status__user=user
        ).count()
    
    def get_user_role(self, obj):
        # Get the role of the current user in this group chat
        user = self.context.get('request').user
        if not user:
            return None
        
        try:
            membership = GroupChatMembership.objects.get(group_chat=obj, user=user)
            return membership.role
        except GroupChatMembership.DoesNotExist:
            return None
    
    def get_avatar_url(self, obj):
        return obj.avatar.url if obj.avatar else None


class GroupChatDetailSerializer(GroupChatSerializer):
    """Detailed serializer for group chats including messages and members"""
    messages = serializers.SerializerMethodField()
    members = serializers.SerializerMethodField()
    
    class Meta(GroupChatSerializer.Meta):
        fields = GroupChatSerializer.Meta.fields + ['messages', 'members']
    
    def get_messages(self, obj):
        # Get paginated messages for the group chat
        # The actual pagination is handled in the view
        messages = self.context.get('messages', obj.messages.all())
        return MessageSerializer(messages, many=True).data
    
    def get_members(self, obj):
        # Get all members with their roles
        memberships = GroupChatMembership.objects.filter(group_chat=obj)
        return GroupChatMembershipSerializer(memberships, many=True).data


class GroupChatCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating a new group chat"""
    organization_id = serializers.IntegerField(write_only=True)
    member_ids = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True
    )
    initial_message = serializers.CharField(write_only=True, required=False)
    
    class Meta:
        model = GroupChat
        fields = ['name', 'description', 'organization_id', 'member_ids', 'initial_message', 'avatar']
    
    def validate(self, data):
        user = self.context['request'].user
        organization_id = data.get('organization_id')
        member_ids = data.get('member_ids', [])
        
        # Check if organization exists
        try:
            organization = Organization.objects.get(id=organization_id)
        except Organization.DoesNotExist:
            raise serializers.ValidationError("Organization not found")
        
        # Check if creator belongs to the organization
        if not organization.members.filter(id=user.id).exists():
            raise serializers.ValidationError("You don't belong to this organization")
        
        # Check if all members belong to the organization
        for member_id in member_ids:
            if not organization.members.filter(id=member_id).exists():
                raise serializers.ValidationError(f"User with ID {member_id} doesn't belong to this organization")
        
        # Check if any member has blocked the creator
        blocked_by = UserBlock.objects.filter(
            blocker_id__in=member_ids,
            blocked=user,
            organization=organization
        )
        
        if blocked_by.exists():
            blocked_users = [block.blocker.username for block in blocked_by]
            raise serializers.ValidationError(f"You are blocked by: {', '.join(blocked_users)}")
        
        return data


class UserBlockSerializer(serializers.ModelSerializer):
    """Serializer for user blocks"""
    blocker = UserMinimalSerializer(read_only=True)
    blocked = UserMinimalSerializer(read_only=True)
    organization = OrganizationMinimalSerializer(read_only=True)
    
    class Meta:
        model = UserBlock
        fields = ['id', 'blocker', 'blocked', 'organization', 'created_at']
        read_only_fields = ['id', 'blocker', 'created_at']


class UserBlockCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating a user block"""
    blocked_id = serializers.IntegerField(write_only=True)
    organization_id = serializers.IntegerField(write_only=True)
    
    class Meta:
        model = UserBlock
        fields = ['blocked_id', 'organization_id']
    
    def validate(self, data):
        user = self.context['request'].user
        blocked_id = data.get('blocked_id')
        organization_id = data.get('organization_id')
        
        # Check if blocked user exists
        try:
            blocked = User.objects.get(id=blocked_id)
        except User.DoesNotExist:
            raise serializers.ValidationError("User to block not found")
        
        # Check if organization exists
        try:
            organization = Organization.objects.get(id=organization_id)
        except Organization.DoesNotExist:
            raise serializers.ValidationError("Organization not found")
        
        # Check if both users belong to the organization
        if not organization.members.filter(id=user.id).exists():
            raise serializers.ValidationError("You don't belong to this organization")
        
        if not organization.members.filter(id=blocked_id).exists():
            raise serializers.ValidationError("The user to block doesn't belong to this organization")
        
        # Check if block already exists
        if UserBlock.objects.filter(
            blocker=user,
            blocked=blocked,
            organization=organization
        ).exists():
            raise serializers.ValidationError("You have already blocked this user")
        
        return data