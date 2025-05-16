from datetime import timezone
from django.shortcuts import render
from rest_framework import viewsets, mixins, status, filters
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import PageNumberPagination
from django.db.models import Q, Prefetch, Count
from django.shortcuts import get_object_or_404
from organizations.models import Organization
from accounts.models import User


from .models import (
    Conversation, GroupChat, GroupChatMembership, Message, 
    MessageReaction, MessageAttachment, MessageReadStatus, UserBlock, MessageDeliveryStatus
)
from .serializers import (
    ConversationSerializer, ConversationDetailSerializer, ConversationCreateSerializer,
    GroupChatSerializer, GroupChatDetailSerializer, GroupChatCreateSerializer,
    MessageSerializer, MessageCreateSerializer,
    MessageReactionSerializer, MessageAttachmentSerializer,
    UserBlockSerializer, UserBlockCreateSerializer,
    GroupChatMembershipSerializer
)




class MessagePagination(PageNumberPagination):
    """Custom pagination for messages with reverse ordering"""
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100
    
    def get_paginated_response(self, data):
        return Response({
            'next': self.get_next_link(),
            'previous': self.get_previous_link(),
            'count': self.page.paginator.count,
            'results': data
        })


# Conversation views
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def conversation_list(request):
    """Get all conversations for the current user"""
    user = request.user
    conversations = Conversation.objects.filter(
        participants=user,
        is_active=True
    ).prefetch_related(
        'participants',
        'organization'
    ).distinct()
    
    serializer = ConversationSerializer(conversations, many=True, context={'request': request})
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def conversation_create(request):
    """Create a new conversation"""
    print("Creating conversation")
    print(request.data)
    
    if request.data.get('initial_message') == "":
        request.data['initial_message'] = "No initial message"
    
    # Add context to serializer
    serializer = ConversationCreateSerializer(
        data=request.data,
        context={'request': request}  # Add this line
    )
    
    if not serializer.is_valid():
        print("Serializer is not valid")
        print(serializer.errors)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    user = request.user
    participant_id = serializer.validated_data.get('participant_id')
    organization_id = serializer.validated_data.get('organization_id')
    initial_message = serializer.validated_data.get('initial_message')
    
    # Get participant and organization
    participant = get_object_or_404(User, id=participant_id)
    organization = get_object_or_404(Organization, id=organization_id)
    
    # Create conversation
    conversation = Conversation.objects.create(organization=organization)
    conversation.participants.add(user, participant)
    
    # Create initial message if provided
    if initial_message:
        message = Message.objects.create(
            conversation=conversation,
            sender=user,
            content=initial_message
        )
    
    return Response(
        ConversationDetailSerializer(conversation, context={'request': request}).data,
        status=status.HTTP_201_CREATED
    )


@api_view(['GET', 'DELETE'])
@permission_classes([IsAuthenticated])
def conversation_detail(request, pk):
    """Get conversation details or delete a conversation"""
    user = request.user
    conversation = get_object_or_404(
        Conversation.objects.filter(participants=user, is_active=True),
        pk=pk
    )
    
    if request.method == 'DELETE':
        # Soft delete conversation
        conversation.is_active = False
        conversation.save()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    # GET method - return conversation details
    serializer = ConversationDetailSerializer(conversation, context={'request': request})
    return Response(serializer.data)


@api_view(['PUT', 'PATCH'])
@permission_classes([IsAuthenticated])
def conversation_update(request, pk):
    """Update conversation"""
    user = request.user
    conversation = get_object_or_404(
        Conversation.objects.filter(participants=user, is_active=True),
        pk=pk
    )
    
    # Only allow updating is_active field
    if 'is_active' in request.data:
        conversation.is_active = request.data.get('is_active')
        conversation.save()
    
    serializer = ConversationDetailSerializer(conversation, context={'request': request})
    return Response(serializer.data)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def conversation_delete(request, pk):
    """Delete conversation (soft delete)"""
    user = request.user
    conversation = get_object_or_404(
        Conversation.objects.filter(participants=user, is_active=True),
        pk=pk
    )
    
    conversation.is_active = False
    conversation.save()
    
    return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def conversation_messages(request, pk):
    """Get messages for a conversation"""
    user = request.user
    conversation = get_object_or_404(
        Conversation.objects.filter(participants=user, is_active=True),
        pk=pk
    )
    
    messages = conversation.messages.all().order_by('-created_at')
    
    # Mark messages as read
    unread_messages = messages.exclude(
        read_status__user=request.user
    )
    
    for message in unread_messages:
        if message.sender != request.user:
            MessageReadStatus.objects.get_or_create(
                message=message,
                user=request.user
            )
    
    # Paginate messages
    paginator = MessagePagination()
    page = paginator.paginate_queryset(messages, request)
    
    if page is not None:
        serializer = MessageSerializer(page, many=True)
        return paginator.get_paginated_response(serializer.data)
    
    serializer = MessageSerializer(messages, many=True)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def conversation_send_message(request, pk):
    """Send a message in a conversation"""
    user = request.user
    conversation = get_object_or_404(
        Conversation.objects.filter(participants=user, is_active=True),
        pk=pk
    )
    
    serializer = MessageCreateSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    
    # Check if user is blocked
    other_participant = conversation.participants.exclude(id=request.user.id).first()
    if UserBlock.objects.filter(
        blocker=other_participant,
        blocked=request.user,
        organization=conversation.organization
    ).exists():
        return Response(
            {"detail": "You have been blocked by this user"},
            status=status.HTTP_403_FORBIDDEN
        )
    
    # Create message
    message = Message.objects.create(
        conversation=conversation,
        sender=request.user,
        content=serializer.validated_data.get('content'),
        reply_to=serializer.validated_data.get('reply_to')
    )
    
    # Handle attachments
    attachments = serializer.validated_data.get('attachments', [])
    attachment_types = serializer.validated_data.get('attachment_types', [])
    
    for i, attachment in enumerate(attachments):
        MessageAttachment.objects.create(
            message=message,
            file=attachment,
            attachment_type=attachment_types[i],
            file_name=attachment.name,
            file_size=attachment.size
        )
    
    return Response(
        MessageSerializer(message).data,
        status=status.HTTP_201_CREATED
    )


# Group Chat views
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def group_chat_list(request):
    """Get all group chats for the current user"""
    user = request.user
    group_chats = GroupChat.objects.filter(
        members=user,
        is_active=True
    ).prefetch_related(
        'members',
        'organization'
    ).distinct()
    
    serializer = GroupChatSerializer(group_chats, many=True)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def group_chat_create(request):
    """Create a new group chat"""
    serializer = GroupChatCreateSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    
    user = request.user
    organization_id = serializer.validated_data.get('organization_id')
    member_ids = serializer.validated_data.get('member_ids', [])
    initial_message = serializer.validated_data.get('initial_message')
    
    # Get organization
    organization = get_object_or_404(Organization, id=organization_id)
    
    # Create group chat
    group_chat = GroupChat.objects.create(
        name=serializer.validated_data.get('name'),
        description=serializer.validated_data.get('description', ''),
        organization=organization,
        created_by=user,
        avatar=serializer.validated_data.get('avatar')
    )
    
    # Add creator as admin
    GroupChatMembership.objects.create(
        group_chat=group_chat,
        user=user,
        role='admin'
    )
    
    # Add members
    for member_id in member_ids:
        if member_id != user.id:  # Skip creator as they're already added as admin
            member = get_object_or_404(User, id=member_id)
            GroupChatMembership.objects.create(
                group_chat=group_chat,
                user=member,
                role='member'
            )
    
    # Create initial message if provided
    if initial_message:
        message = Message.objects.create(
            group_chat=group_chat,
            sender=user,
            content=initial_message
        )
    
    return Response(
        GroupChatDetailSerializer(group_chat, context={'request': request}).data,
        status=status.HTTP_201_CREATED
    )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def group_chat_detail(request, pk):
    """Get group chat details"""
    user = request.user
    group_chat = get_object_or_404(
        GroupChat.objects.filter(members=user, is_active=True),
        pk=pk
    )
    
    serializer = GroupChatDetailSerializer(group_chat, context={'request': request})
    return Response(serializer.data)


@api_view(['PUT', 'PATCH'])
@permission_classes([IsAuthenticated])
def group_chat_update(request, pk):
    """Update group chat"""
    user = request.user
    group_chat = get_object_or_404(
        GroupChat.objects.filter(members=user, is_active=True),
        pk=pk
    )
    
    # Check if user is an admin
    try:
        membership = GroupChatMembership.objects.get(
            group_chat=group_chat,
            user=user
        )
        if membership.role != 'admin':
            return Response(
                {"detail": "Only admins can update the group chat"},
                status=status.HTTP_403_FORBIDDEN
            )
    except GroupChatMembership.DoesNotExist:
        return Response(
            {"detail": "You are not a member of this group chat"},
            status=status.HTTP_403_FORBIDDEN
        )
    
    # Update fields
    if 'name' in request.data:
        group_chat.name = request.data.get('name')
    
    if 'description' in request.data:
        group_chat.description = request.data.get('description')
    
    if 'avatar' in request.data and request.data.get('avatar'):
        group_chat.avatar = request.data.get('avatar')
    
    group_chat.save()
    
    serializer = GroupChatDetailSerializer(group_chat, context={'request': request})
    return Response(serializer.data)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def group_chat_delete(request, pk):
    """Delete group chat (soft delete)"""
    user = request.user
    group_chat = get_object_or_404(
        GroupChat.objects.filter(members=user, is_active=True),
        pk=pk
    )
    
    # Check if user is an admin
    try:
        membership = GroupChatMembership.objects.get(
            group_chat=group_chat,
            user=user
        )
        if membership.role != 'admin':
            return Response(
                {"detail": "Only admins can delete the group chat"},
                status=status.HTTP_403_FORBIDDEN
            )
    except GroupChatMembership.DoesNotExist:
        return Response(
            {"detail": "You are not a member of this group chat"},
            status=status.HTTP_403_FORBIDDEN
        )
    
    group_chat.is_active = False
    group_chat.save()
    
    return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def group_chat_messages(request, pk):
    """Get messages for a group chat"""
    user = request.user
    group_chat = get_object_or_404(
        GroupChat.objects.filter(members=user, is_active=True),
        pk=pk
    )
    
    messages = group_chat.messages.all().order_by('-created_at')
    
    # Mark messages as read
    unread_messages = messages.exclude(
        read_status__user=request.user
    )
    
    for message in unread_messages:
        if message.sender != request.user:
            MessageReadStatus.objects.get_or_create(
                message=message,
                user=request.user
            )
    
    # Paginate messages
    paginator = MessagePagination()
    page = paginator.paginate_queryset(messages, request)
    
    if page is not None:
        serializer = MessageSerializer(page, many=True)
        return paginator.get_paginated_response(serializer.data)
    
    serializer = MessageSerializer(messages, many=True)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def group_chat_send_message(request, pk):
    """Send a message in a group chat"""
    user = request.user
    group_chat = get_object_or_404(
        GroupChat.objects.filter(members=user, is_active=True),
        pk=pk
    )
    
    serializer = MessageCreateSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    
    # Check if user is a member
    try:
        membership = GroupChatMembership.objects.get(
            group_chat=group_chat,
            user=user
        )
    except GroupChatMembership.DoesNotExist:
        return Response(
            {"detail": "You are not a member of this group chat"},
            status=status.HTTP_403_FORBIDDEN
        )
    
    # Create message
    message = Message.objects.create(
        group_chat=group_chat,
        sender=user,
        content=serializer.validated_data.get('content'),
        reply_to=serializer.validated_data.get('reply_to')
    )
    
    # Handle attachments
    attachments = serializer.validated_data.get('attachments', [])
    attachment_types = serializer.validated_data.get('attachment_types', [])
    
    for i, attachment in enumerate(attachments):
        MessageAttachment.objects.create(
            message=message,
            file=attachment,
            attachment_type=attachment_types[i],
            file_name=attachment.name,
            file_size=attachment.size
        )
    
    return Response(
        MessageSerializer(message).data,
        status=status.HTTP_201_CREATED
    )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def group_chat_add_members(request, pk):
    """Add members to a group chat"""
    user = request.user
    group_chat = get_object_or_404(
        GroupChat.objects.filter(members=user, is_active=True),
        pk=pk
    )
    
    # Check if user is an admin
    try:
        membership = GroupChatMembership.objects.get(
            group_chat=group_chat,
            user=user
        )
        if membership.role != 'admin':
            return Response(
                {"detail": "Only admins can add members"},
                status=status.HTTP_403_FORBIDDEN
            )
    except GroupChatMembership.DoesNotExist:
        return Response(
            {"detail": "You are not a member of this group chat"},
            status=status.HTTP_403_FORBIDDEN
        )
    
    # Validate member_ids
    member_ids = request.data.get('member_ids', [])
    if not member_ids:
        return Response(
            {"detail": "No member IDs provided"},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Check if all users belong to the organization
    organization = group_chat.organization
    for member_id in member_ids:
        if not organization.members.filter(id=member_id).exists():
            return Response(
                {"detail": f"User with ID {member_id} doesn't belong to this organization"},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    # Add members
    added_members = []
    for member_id in member_ids:
        member = get_object_or_404(User, id=member_id)
        
        # Skip if already a member
        if GroupChatMembership.objects.filter(group_chat=group_chat, user=member).exists():
            continue
        
        GroupChatMembership.objects.create(
            group_chat=group_chat,
            user=member,
            role='member'
        )
        added_members.append(member)
    
    # Create system message about new members
    if added_members:
        member_names = ", ".join([member.username for member in added_members])
        Message.objects.create(
            group_chat=group_chat,
            sender=user,
            content=f"Added {member_names} to the group"
        )
    
    return Response(
        GroupChatDetailSerializer(group_chat, context={'request': request}).data,
        status=status.HTTP_200_OK
    )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def group_chat_remove_member(request, pk):
    """Remove a member from a group chat"""
    user = request.user
    group_chat = get_object_or_404(
        GroupChat.objects.filter(members=user, is_active=True),
        pk=pk
    )
    
    member_id = request.data.get('member_id')
    if not member_id:
        return Response(
            {"detail": "No member ID provided"},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Check if user is an admin or removing themselves
    try:
        membership = GroupChatMembership.objects.get(
            group_chat=group_chat,
            user=user
        )
        is_admin = membership.role == 'admin'
        is_self_removal = str(member_id) == str(user.id)
        
        if not (is_admin or is_self_removal):
            return Response(
                {"detail": "Only admins can remove other members"},
                status=status.HTTP_403_FORBIDDEN
            )
    except GroupChatMembership.DoesNotExist:
        return Response(
            {"detail": "You are not a member of this group chat"},
            status=status.HTTP_403_FORBIDDEN
        )
    
    # Get member to remove
    member = get_object_or_404(User, id=member_id)
    
    # Check if member is in the group
    try:
        member_membership = GroupChatMembership.objects.get(
            group_chat=group_chat,
            user=member
        )
    except GroupChatMembership.DoesNotExist:
        return Response(
            {"detail": "User is not a member of this group chat"},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Prevent removing the last admin
    if member_membership.role == 'admin':
        admin_count = GroupChatMembership.objects.filter(
            group_chat=group_chat,
            role='admin'
        ).count()
        
        if admin_count <= 1:
            return Response(
                {"detail": "Cannot remove the last admin. Promote another member to admin first."},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    # Remove member
    member_membership.delete()
    
    # Create system message about removed member
    Message.objects.create(
        group_chat=group_chat,
        sender=user,
        content=f"{member.username} {'left' if is_self_removal else 'was removed from'} the group"
    )
    
    return Response(
        GroupChatDetailSerializer(group_chat, context={'request': request}).data,
        status=status.HTTP_200_OK
    )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def group_chat_change_role(request, pk):
    """Change a member's role in a group chat"""
    user = request.user
    group_chat = get_object_or_404(
        GroupChat.objects.filter(members=user, is_active=True),
        pk=pk
    )
    
    member_id = request.data.get('member_id')
    new_role = request.data.get('role')
    
    if not member_id or not new_role:
        return Response(
            {"detail": "Member ID and role are required"},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    if new_role not in ['admin', 'member']:
        return Response(
            {"detail": "Invalid role. Must be 'admin' or 'member'"},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Check if user is an admin
    try:
        membership = GroupChatMembership.objects.get(
            group_chat=group_chat,
            user=user
        )
        if membership.role != 'admin':
            return Response(
                {"detail": "Only admins can change roles"},
                status=status.HTTP_403_FORBIDDEN
            )
    except GroupChatMembership.DoesNotExist:
        return Response(
            {"detail": "You are not a member of this group chat"},
            status=status.HTTP_403_FORBIDDEN
        )
    
    # Get member to update
    member = get_object_or_404(User, id=member_id)
    
    # Check if member is in the group
    try:
        member_membership = GroupChatMembership.objects.get(
            group_chat=group_chat,
            user=member
        )
    except GroupChatMembership.DoesNotExist:
        return Response(
            {"detail": "User is not a member of this group chat"},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Prevent demoting the last admin
    if member_membership.role == 'admin' and new_role == 'member':
        admin_count = GroupChatMembership.objects.filter(
            group_chat=group_chat,
            role='admin'
        ).count()
        
        if admin_count <= 1:
            return Response(
                {"detail": "Cannot demote the last admin. Promote another member to admin first."},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    # Update role
    member_membership.role = new_role
    member_membership.save()
    
    # Create system message about role change
    Message.objects.create(
        group_chat=group_chat,
        sender=user,
        content=f"{member.username} is now a {new_role}"
    )
    
    return Response(
        GroupChatMembershipSerializer(member_membership).data,
        status=status.HTTP_200_OK
    )


# Message views
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def message_detail(request, pk):
    """Get message details"""
    user = request.user
    message = get_object_or_404(
        Message.objects.filter(
            Q(conversation__participants=user) | 
            Q(group_chat__members=user)
        ).distinct(),
        pk=pk
    )
    
    # Mark message as read if not sender
    if message.sender != user:
        MessageReadStatus.objects.get_or_create(
            message=message,
            user=user
        )
    
    serializer = MessageSerializer(message)
    return Response(serializer.data)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def message_delete(request, pk):
    """Delete a message (soft delete)"""
    user = request.user
    message = get_object_or_404(
        Message.objects.filter(
            Q(conversation__participants=user) | 
            Q(group_chat__members=user)
        ).distinct(),
        pk=pk
    )
    
    # Check if user is the sender
    if message.sender != user:
        return Response(
            {"detail": "You can only delete your own messages"},
            status=status.HTTP_403_FORBIDDEN
        )
    
    # Soft delete
    message.is_deleted = True
    message.content = "[This message was deleted]"
    message.save()
    
    return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def message_edit(request, pk):
    """Edit a message"""
    user = request.user
    message = get_object_or_404(
        Message.objects.filter(
            Q(conversation__participants=user) | 
            Q(group_chat__members=user)
        ).distinct(),
        pk=pk
    )
    
    # Check if user is the sender
    if message.sender != user:
        return Response(
            {"detail": "You can only edit your own messages"},
            status=status.HTTP_403_FORBIDDEN
        )
    
    # Check if message is deleted
    if message.is_deleted:
        return Response(
            {"detail": "Cannot edit a deleted message"},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Update content
    content = request.data.get('content')
    if not content:
        return Response(
            {"detail": "Content is required"},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    message.content = content
    message.is_edited = True
    message.save()
    
    return Response(
        MessageSerializer(message).data,
        status=status.HTTP_200_OK
    )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def message_react(request, pk):
    """React to a message"""
    user = request.user
    message = get_object_or_404(
        Message.objects.filter(
            Q(conversation__participants=user) | 
            Q(group_chat__members=user)
        ).distinct(),
        pk=pk
    )
    
    emoji = request.data.get('emoji')
    if not emoji:
        return Response(
            {"detail": "Emoji is required"},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Create or update reaction
    reaction, created = MessageReaction.objects.get_or_create(
        message=message,
        user=user,
        emoji=emoji
    )
    
    return Response(
        MessageReactionSerializer(reaction).data,
        status=status.HTTP_201_CREATED if created else status.HTTP_200_OK
    )


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def message_unreact(request, pk):
    """Remove a reaction from a message"""
    user = request.user
    message = get_object_or_404(
        Message.objects.filter(
            Q(conversation__participants=user) | 
            Q(group_chat__members=user)
        ).distinct(),
        pk=pk
    )
    
    emoji = request.query_params.get('emoji')
    
    # Delete reaction
    if emoji:
        # Delete specific reaction
        MessageReaction.objects.filter(
            message=message,
            user=user,
            emoji=emoji
        ).delete()
    else:
        # Delete all reactions
        MessageReaction.objects.filter(
            message=message,
            user=user
        ).delete()
    
    # Update reaction count
    message.reaction_count = MessageReaction.objects.filter(message=message).count()
    message.save(update_fields=['reaction_count'])
    
    return Response(status=status.HTTP_204_NO_CONTENT)


# User Block views
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_block_list(request):
    """Get all blocks for the current user"""
    user = request.user
    blocks = UserBlock.objects.filter(blocker=user)
    
    serializer = UserBlockSerializer(blocks, many=True)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def user_block_create(request):
    """Block a user"""
    user = request.user
    serializer = UserBlockCreateSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    
    blocked_id = serializer.validated_data.get('blocked_id')
    organization_id = serializer.validated_data.get('organization_id')
    
    # Get blocked user and organization
    blocked = get_object_or_404(User, id=blocked_id)
    organization = get_object_or_404(Organization, id=organization_id)
    
    # Create block
    block = UserBlock.objects.create(
        blocker=user,
        blocked=blocked,
        organization=organization
    )
    
    return Response(
        UserBlockSerializer(block).data,
        status=status.HTTP_201_CREATED
    )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_block_detail(request, pk):
    """Get block details"""
    user = request.user
    block = get_object_or_404(UserBlock, pk=pk, blocker=user)
    
    serializer = UserBlockSerializer(block)
    return Response(serializer.data)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def user_block_delete(request, pk):
    """Unblock a user"""
    user = request.user
    block = get_object_or_404(UserBlock, pk=pk, blocker=user)
    
    block.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)


class MessageViewSet(viewsets.ModelViewSet):
    serializer_class = MessageSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if conversation_id := self.request.query_params.get('conversation'):
            return Message.objects.filter(conversation_id=conversation_id)
        elif group_chat_id := self.request.query_params.get('group_chat'):
            return Message.objects.filter(group_chat_id=group_chat_id)
        return Message.objects.none()

    def perform_create(self, serializer):
        serializer.save(sender=self.request.user)
        
        # Create initial delivery status
        MessageDeliveryStatus.objects.create(
            message=serializer.instance,
            status='sent',
            timestamp=timezone.now()
        )

    @action(detail=True, methods=['post'])
    def mark_delivered(self, request, pk=None):
        message = self.get_object()
        MessageDeliveryStatus.objects.create(
            message=message,
            status='delivered',
            timestamp=timezone.now()
        )
        return Response(status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'])
    def mark_read(self, request, pk=None):
        message = self.get_object()
        MessageReadStatus.objects.get_or_create(
            message=message,
            user=request.user,
            defaults={'read_at': timezone.now()}
        )
        MessageDeliveryStatus.objects.create(
            message=message,
            status='read',
            timestamp=timezone.now()
        )
        return Response(status=status.HTTP_200_OK)
