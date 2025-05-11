from django.shortcuts import render, get_object_or_404
from django.db.models import Q, Count
from accounts.models import User
from django.utils import timezone

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination

from organizations.models import Organization, OrganizationAdmins
from .models import (
    Post, PostMedia, PostComment, ReactionType, 
    PostReaction, CommentReaction, PostShare, 
    PostTag, Hashtag, PostHashtag, Trend
)
from .serializers import (
    PostSerializer, PostDetailSerializer, PostCreateSerializer,
    PostUpdateSerializer, PostCommentSerializer, PostCommentCreateSerializer,
    ReactionTypeSerializer, PostReactionSerializer, CommentReactionSerializer,
    PostShareSerializer, PostTagSerializer, HashtagSerializer
)
from .utils import upload_to_cloudinary, delete_from_cloudinary


# Helper function to check if user is an organization admin
def is_organization_admin(user, organization):
    """Check if a user is an admin of the organization"""
    return OrganizationAdmins.objects.filter(organization=organization, admin=user).exists()

# Helper function to check if user can access a post
def can_access_post(user, post):
    """
    Check if a user can access a post based on:
    - If the post is public
    - If the user is the post creator
    - If the user is an admin of the organization the post belongs to
    - If the user is a system admin
    """
    # Public posts are accessible to all authenticated users
    if post.ispublic:
        return True
    
    # Post creator can access their own posts
    if post.user == user:
        return True
    
    # Check if post belongs to an organization
    if post.organization:
        # Organization admins can access all posts in their organization
        if is_organization_admin(user, post.organization):
            return True
        
        # Organization members can access non-public posts in their organization
        if user in post.organization.users.all():
            return True
    
    # System admins can access all posts
    if user.role == 'ADMIN':
        return True
    
    return False

# Post CRUD Operations

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_post(request):
    """
    Create a new post with optional media files.
    """
    print("Request data:", request.data)
    serializer = PostCreateSerializer(data=request.data)
    if serializer.is_valid():
        # Check if trying to create announcement without being admin
        post_type = serializer.validated_data.get('type', 'post')
        if post_type == 'announcement' and request.user.role != 'ADMIN':
            return Response(
                {"error": "Only admins can create announcements"},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Get organization if specified
        organization_id = serializer.validated_data.get('organization_id')
        organization = None
        
        if organization_id:
            organization = get_object_or_404(Organization, id=organization_id)
            # Check if user is a member of the organization
            if not organization.users.filter(id=request.user.id).exists():
                return Response(
                    {"error": "You must be a member of the organization to post"},
                    status=status.HTTP_403_FORBIDDEN
                )
        
        # Create post
        post = Post.objects.create(
            user=request.user,
            organization=organization,
            content=serializer.validated_data.get('content', ''),
            ispublic=serializer.validated_data.get('ispublic', True),
            type=post_type  # Set post type
        )
        
        # Handle media file from mobile app format
        media_data = request.data.get('media')
        if media_data:
            try:
                # Get the file from request.FILES
                media_file = request.FILES.get('media')
                if media_file:
                    # Upload to Cloudinary
                    upload_result = upload_to_cloudinary(media_file)
                    print("Upload result:", upload_result)
                    
                    if not upload_result['success']:
                        post.delete()
                        return Response(
                            {"error": f"Failed to upload media: {upload_result['error']}"},
                            status=status.HTTP_400_BAD_REQUEST
                        )
                    
                    # Get media type from file content_type
                    media_type = media_file.content_type.split('/')[0]  # 'image' or 'video'
                    PostMedia.objects.create(
                        post=post,
                        file=upload_result['url'],
                        media_type=media_type
                    )
            except Exception as e:
                post.delete()
                return Response(
                    {"error": f"Error processing media: {str(e)}"},
                    status=status.HTTP_400_BAD_REQUEST
                )

        # Process hashtags
        content = post.content
        hashtag_list = []
        words = content.split()
        for word in words:
            if word.startswith('#'):
                # Get original hashtag name for display
                hashtag_name = word[1:]
                if hashtag_name:
                    # Convert to uppercase for storage and lookup
                    uppercase_hashtag = hashtag_name.upper()
                    hashtag, created = Hashtag.objects.get_or_create(name=uppercase_hashtag)
                    PostHashtag.objects.create(post=post, hashtag=hashtag)
                    hashtag_list.append(hashtag.name)
        
        # Process user tags
        user_ids = serializer.validated_data.get('tagged_user_ids', [])
        for user_id in user_ids:
            try:
                tagged_user = User.objects.get(id=user_id)
                PostTag.objects.create(post=post, user=tagged_user)
            except User.DoesNotExist:
                pass
        
        return Response(
            PostDetailSerializer(post).data,
            status=status.HTTP_201_CREATED
        )
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_post_detail(request, pk):
    """
    Get detailed information about a specific post.
    """
    post = get_object_or_404(Post, pk=pk)
    
    # Check if user can access this post
    if not can_access_post(request.user, post):
        return Response(
            {"error": "You do not have permission to view this post"},
            status=status.HTTP_403_FORBIDDEN
        )
    
    serializer = PostDetailSerializer(post)
    return Response(serializer.data)

@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_post(request, pk):
    """
    Update an existing post.
    """
    post = get_object_or_404(Post, pk=pk)
    
    # Only post creator, organization admin, or system admin can update
    if post.user != request.user and not (
        post.organization and is_organization_admin(request.user, post.organization)
    ) and request.user.role != 'ADMIN':
        return Response(
            {"error": "You do not have permission to update this post"},
            status=status.HTTP_403_FORBIDDEN
        )
    
    serializer = PostUpdateSerializer(post, data=request.data, partial=True)
    if serializer.is_valid():
        updated_post = serializer.save()
        
        # Update hashtags if content was changed
        if 'content' in serializer.validated_data:
            # Remove existing hashtags
            PostHashtag.objects.filter(post=post).delete()
            
            # Add new hashtags
            content = updated_post.content
            words = content.split()
            for word in words:
                if word.startswith('#'):
                    # Get original hashtag name for display
                    hashtag_name = word[1:]
                    if hashtag_name:
                        # Convert to uppercase for storage and lookup
                        uppercase_hashtag = hashtag_name.upper()
                        hashtag, created = Hashtag.objects.get_or_create(name=uppercase_hashtag)
                        PostHashtag.objects.create(post=updated_post, hashtag=hashtag)
        
        return Response(
            PostDetailSerializer(updated_post).data,
            status=status.HTTP_200_OK
        )
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_post(request, pk):
    """
    Delete a post.
    """
    post = get_object_or_404(Post, pk=pk)
    
    # Only post creator, organization admin, or system admin can delete
    if post.user != request.user and not (
        post.organization and is_organization_admin(request.user, post.organization)
    ) and request.user.role != 'ADMIN':
        return Response(
            {"error": "You do not have permission to delete this post"},
            status=status.HTTP_403_FORBIDDEN
        )
    
    post.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)

# Feed and Timeline

class PostPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 50

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_feed(request):
    """
    Get a feed of regular posts for the current user.
    """
    paginator = PostPagination()
    
    # Get user's organizations
    user_orgs = request.user.organizations.all()
    
    # Query for posts
    posts = Post.objects.filter(
        type='post'  # Only get regular posts
    ).filter(
        Q(ispublic=True) | 
        Q(organization__in=user_orgs) |
        Q(user=request.user)
    ).distinct().order_by('-created_at')
    
    result_page = paginator.paginate_queryset(posts, request)
    serializer = PostSerializer(result_page, many=True)
    
    return paginator.get_paginated_response(serializer.data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_announcements(request):
    """
    Get announcements with pagination.
    """
    paginator = PostPagination()
    
    # Get user's organizations
    user_orgs = request.user.organizations.all()
    
    # Query for announcements
    announcements = Post.objects.filter(
        type='announcement'
    ).filter(
        Q(ispublic=True) | 
        Q(organization__in=user_orgs) |
        Q(user=request.user)
    ).distinct().order_by('-created_at')
    
    result_page = paginator.paginate_queryset(announcements, request)
    serializer = PostSerializer(result_page, many=True)
    
    return paginator.get_paginated_response(serializer.data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_posts(request, user_id=None):
    """
    Get posts created by a specific user or the current user.
    """
    paginator = PostPagination()
    
    if user_id:
        target_user = get_object_or_404(User, pk=user_id)
        
        # If viewing another user's posts, only show public posts
        if request.user.id != target_user.id and request.user.role != 'ADMIN':
            posts = Post.objects.filter(
                user=target_user, 
                ispublic=True
            ).order_by('-created_at')
        else:
            # If viewing own posts or is admin, show all posts
            posts = Post.objects.filter(
                user=target_user
            ).order_by('-created_at')
    else:
        # Get current user's posts
        posts = Post.objects.filter(
            user=request.user
        ).order_by('-created_at')
    
    # Apply pagination
    result_page = paginator.paginate_queryset(posts, request)
    serializer = PostSerializer(result_page, many=True)
    
    return paginator.get_paginated_response(serializer.data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_organization_posts(request, org_id):
    """
    Get posts from a specific organization.
    """
    paginator = PostPagination()
    organization = get_object_or_404(Organization, pk=org_id)
    
    # Check if user is a member of the organization
    is_member = organization.users.filter(id=request.user.id).exists()
    is_admin = is_organization_admin(request.user, organization)
    is_system_admin = request.user.role == 'ADMIN'
    
    if not (is_member or is_admin or is_system_admin):
        # If not a member, only show public posts
        posts = Post.objects.filter(
            organization=organization,
            ispublic=True
        ).order_by('-created_at')
    else:
        # If a member, show all posts
        posts = Post.objects.filter(
            organization=organization
        ).order_by('-created_at')
    
    # Apply pagination
    result_page = paginator.paginate_queryset(posts, request)
    serializer = PostSerializer(result_page, many=True)
    
    return paginator.get_paginated_response(serializer.data)

# Comment Operations

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_comment(request, post_id):
    """
    Create a comment on a post.
    """
    post = get_object_or_404(Post, pk=post_id)
    
    # Check if user can access this post to comment
    if not can_access_post(request.user, post):
        return Response(
            {"error": "You do not have permission to comment on this post"},
            status=status.HTTP_403_FORBIDDEN
        )
    
    serializer = PostCommentCreateSerializer(data=request.data)
    if serializer.is_valid():
        # Get parent comment if replying to a comment
        parent_comment_id = serializer.validated_data.get('parent_comment_id')
        parent_comment = None
        
        if parent_comment_id:
            parent_comment = get_object_or_404(PostComment, pk=parent_comment_id, post=post)
        
        # Create comment
        comment = PostComment.objects.create(
            post=post,
            user=request.user,
            parent_comment=parent_comment,
            content=serializer.validated_data.get('content')
        )
        
        # Update post comment count
        post.comment_count = PostComment.objects.filter(post=post, parent_comment=None).count()
        post.save()
        
        # Update parent comment reply count if applicable
        if parent_comment:
            parent_comment.reply_count = PostComment.objects.filter(parent_comment=parent_comment).count()
            parent_comment.save()
        
        return Response(
            PostCommentSerializer(comment).data,
            status=status.HTTP_201_CREATED
        )
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_post_comments(request, post_id):
    """
    Get all top-level comments for a post.
    """
    post = get_object_or_404(Post, pk=post_id)
    
    # Check if user can access this post to view comments
    if not can_access_post(request.user, post):
        return Response(
            {"error": "You do not have permission to view comments on this post"},
            status=status.HTTP_403_FORBIDDEN
        )
    
    paginator = PostPagination()
    comments = PostComment.objects.filter(
        post=post,
        parent_comment=None
    ).order_by('created_at')
    
    # Apply pagination
    result_page = paginator.paginate_queryset(comments, request)
    serializer = PostCommentSerializer(result_page, many=True)
    
    return paginator.get_paginated_response(serializer.data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_comment_replies(request, comment_id):
    """
    Get all replies to a specific comment.
    """
    comment = get_object_or_404(PostComment, pk=comment_id)
    
    # Check if user can access the post this comment belongs to
    if not can_access_post(request.user, comment.post):
        return Response(
            {"error": "You do not have permission to view replies to this comment"},
            status=status.HTTP_403_FORBIDDEN
        )
    
    paginator = PostPagination()
    replies = PostComment.objects.filter(
        parent_comment=comment
    ).order_by('created_at')
    
    # Apply pagination
    result_page = paginator.paginate_queryset(replies, request)
    serializer = PostCommentSerializer(result_page, many=True)
    
    return paginator.get_paginated_response(serializer.data)

@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_comment(request, comment_id):
    """
    Update a comment.
    """
    comment = get_object_or_404(PostComment, pk=comment_id)
    
    # Only comment creator can update
    if comment.user != request.user and request.user.role != 'ADMIN':
        return Response(
            {"error": "You do not have permission to update this comment"},
            status=status.HTTP_403_FORBIDDEN
        )
    
    serializer = PostCommentCreateSerializer(data=request.data, partial=True)
    if serializer.is_valid():
        comment.content = serializer.validated_data.get('content', comment.content)
        comment.save()
        
        return Response(
            PostCommentSerializer(comment).data,
            status=status.HTTP_200_OK
        )
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_comment(request, comment_id):
    """
    Delete a comment.
    """
    comment = get_object_or_404(PostComment, pk=comment_id)
    
    # Only comment creator, post creator, or admin can delete
    if comment.user != request.user and comment.post.user != request.user and request.user.role != 'ADMIN':
        return Response(
            {"error": "You do not have permission to delete this comment"},
            status=status.HTTP_403_FORBIDDEN
        )
    
    post = comment.post
    parent_comment = comment.parent_comment
    
    # Delete the comment
    comment.delete()
    
    # Update post comment count if it was a top-level comment
    if not parent_comment:
        post.comment_count = PostComment.objects.filter(post=post, parent_comment=None).count()
        post.save()
    else:
        # Update parent comment reply count
        parent_comment.reply_count = PostComment.objects.filter(parent_comment=parent_comment).count()
        parent_comment.save()
    
    return Response(status=status.HTTP_204_NO_CONTENT)

# Reaction Operations

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_reaction_types(request):
    """
    Get all available reaction types.
    If no reaction types exist, create default ones.
    """
    reaction_types = ReactionType.objects.all()
    
    # If no reaction types exist, create defaults
    if not reaction_types.exists():
        default_reactions = [
            {'name': 'LIKE', 'emoji': '👍'},
            {'name': 'LOVE', 'emoji': '❤️'},
            {'name': 'HAHA', 'emoji': '😂'},
            {'name': 'WOW', 'emoji': '😮'},
            {'name': 'SAD', 'emoji': '😢'},
            {'name': 'ANGRY', 'emoji': '😠'},
        ]
        
        for reaction in default_reactions:
            ReactionType.objects.get_or_create(
                name=reaction['name'],
                emoji=reaction['emoji']
            )
        reaction_types = ReactionType.objects.all()
    
    serializer = ReactionTypeSerializer(reaction_types, many=True)
    return Response(serializer.data)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def react_to_post(request, post_id):
    """
    React to a post or change an existing reaction.
    """
    post = get_object_or_404(Post, pk=post_id)
    
    # Check if user can access this post to react
    if not can_access_post(request.user, post):
        return Response(
            {"error": "You do not have permission to react to this post"},
            status=status.HTTP_403_FORBIDDEN
        )
    
    # Get reaction type
    reaction_type_id = request.data.get('reaction_type_id')
    if not reaction_type_id:
        return Response(
            {"error": "Reaction type is required"},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    reaction_type = get_object_or_404(ReactionType, pk=reaction_type_id)
    
    # Check if user already reacted to this post
    existing_reaction = PostReaction.objects.filter(post=post, user=request.user).first()
    
    if existing_reaction:
        # Update existing reaction
        existing_reaction.reaction_type = reaction_type
        existing_reaction.save()
        message = "Reaction updated"
    else:
        # Create new reaction
        PostReaction.objects.create(
            post=post,
            user=request.user,
            reaction_type=reaction_type
        )
        
        # Update post reaction count
        post.reaction_count = PostReaction.objects.filter(post=post).count()
        post.save()
        message = "Reaction added"
    
    return Response(
        {"message": message, "reaction_type": reaction_type.name},
        status=status.HTTP_200_OK
    )

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def remove_post_reaction(request, post_id):
    """
    Remove a reaction from a post.
    """
    post = get_object_or_404(Post, pk=post_id)
    
    # Check if user has reacted to this post
    reaction = PostReaction.objects.filter(post=post, user=request.user).first()
    
    if not reaction:
        return Response(
            {"error": "You have not reacted to this post"},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Delete the reaction
    reaction.delete()
    
    # Update post reaction count
    post.reaction_count = PostReaction.objects.filter(post=post).count()
    post.save()
    
    return Response(
        {"message": "Reaction removed"},
        status=status.HTTP_200_OK
    )

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def react_to_comment(request, comment_id):
    """
    React to a comment or change an existing reaction.
    """
    comment = get_object_or_404(PostComment, pk=comment_id)
    
    # Check if user can access the post this comment belongs to
    if not can_access_post(request.user, comment.post):
        return Response(
            {"error": "You do not have permission to react to this comment"},
            status=status.HTTP_403_FORBIDDEN
        )
    
    # Get reaction type
    reaction_type_id = request.data.get('reaction_type_id')
    if not reaction_type_id:
        return Response(
            {"error": "Reaction type is required"},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    reaction_type = get_object_or_404(ReactionType, pk=reaction_type_id)
    
    # Check if user already reacted to this comment
    existing_reaction = CommentReaction.objects.filter(comment=comment, user=request.user).first()
    
    if existing_reaction:
        # Update existing reaction
        existing_reaction.reaction_type = reaction_type
        existing_reaction.save()
        message = "Reaction updated"
    else:
        # Create new reaction
        CommentReaction.objects.create(
            comment=comment,
            user=request.user,
            reaction_type=reaction_type
        )
        
        # Update comment reaction count
        comment.reaction_count = CommentReaction.objects.filter(comment=comment).count()
        comment.save()
        message = "Reaction added"
    
    return Response(
        {"message": message, "reaction_type": reaction_type.name},
        status=status.HTTP_200_OK
    )

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def remove_comment_reaction(request, comment_id):
    """
    Remove a reaction from a comment.
    """
    comment = get_object_or_404(PostComment, pk=comment_id)
    
    # Check if user has reacted to this comment
    reaction = CommentReaction.objects.filter(comment=comment, user=request.user).first()
    
    if not reaction:
        return Response(
            {"error": "You have not reacted to this comment"},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Delete the reaction
    reaction.delete()
    
    # Update comment reaction count
    comment.reaction_count = CommentReaction.objects.filter(comment=comment).count()
    comment.save()
    
    return Response(
        {"message": "Reaction removed"},
        status=status.HTTP_200_OK
    )

# Share Operations

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def share_post(request, post_id):
    """
    Share a post.
    """
    post = get_object_or_404(Post, pk=post_id)
    
    # Check if user can access this post to share
    if not can_access_post(request.user, post):
        return Response(
            {"error": "You do not have permission to share this post"},
            status=status.HTTP_403_FORBIDDEN
        )
    
    # Create share
    additional_content = request.data.get('additional_content', '')
    
    share = PostShare.objects.create(
        post=post,
        user=request.user,
        additional_content=additional_content
    )
    
    # Update post share count
    post.share_count = PostShare.objects.filter(post=post).count()
    post.save()
    
    return Response(
        PostShareSerializer(share).data,
        status=status.HTTP_201_CREATED
    )

# Search Operations

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def search_posts(request):
    """
    Search for posts by content, hashtags, or user.
    """
    query = request.query_params.get('q', '')
    if not query:
        return Response(
            {"error": "Search query parameter 'q' is required"},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    paginator = PostPagination()
    
    # Get user's organizations
    user_orgs = request.user.organizations.all()
    
    # Search for posts
    posts = Post.objects.filter(
        # Content search
        (Q(content__icontains=query) |
        # Hashtag search
        Q(hashtags__hashtag__name__icontains=query) |
        # User search
        Q(user__username__icontains=query) |
        Q(user__first_name__icontains=query) |
        Q(user__last_name__icontains=query)) &
        # Visibility filter
        (Q(ispublic=True) | 
        Q(organization__in=user_orgs) |
        Q(user=request.user))
    ).distinct().order_by('-created_at')
    
    # Apply pagination
    result_page = paginator.paginate_queryset(posts, request)
    serializer = PostSerializer(result_page, many=True)
    
    return paginator.get_paginated_response(serializer.data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_posts_by_hashtag(request, hashtag_name):
    """
    Get posts with a specific hashtag.
    """
    paginator = PostPagination()
    
    # Get user's organizations
    user_orgs = request.user.organizations.all()
    
    # Get posts with the hashtag
    posts = Post.objects.filter(
        hashtags__hashtag__name=hashtag_name
    ).filter(
        # Visibility filter
        Q(ispublic=True) | 
        Q(organization__in=user_orgs) |
        Q(user=request.user)
    ).distinct().order_by('-created_at')
    
    # Apply pagination
    result_page = paginator.paginate_queryset(posts, request)
    serializer = PostSerializer(result_page, many=True)
    
    return paginator.get_paginated_response(serializer.data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_trending_hashtags(request):
    """
    Get trending hashtags based on recent post activity.
    """
    # Get hashtags from recent posts (last 7 days)
    trending_hashtags = Hashtag.objects.filter(
        posts__post__created_at__gte=timezone.now() - timezone.timedelta(days=7)
    ).annotate(
        post_count=Count('posts')
    ).order_by('-post_count')[:10]
    
    serializer = HashtagSerializer(trending_hashtags, many=True)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_trends(request):
    """
    Get trending hashtags and their associated posts.
    """
    trends = Trend.objects.order_by('-post_count')[:10]
    data = []
    for trend in trends:
        posts = trend.posts.order_by('-created_at')[:5]  # Limit to 5 recent posts per trend
        posts_data = PostSerializer(posts, many=True, context={'request': request}).data
        data.append({
            "hashtag": trend.hashtag.name,
            "post_count": trend.post_count,
            "posts": posts_data,
        })
    return Response(data, status=status.HTTP_200_OK)

# User Tag Operations

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def tag_user_in_post(request, post_id):
    """
    Tag a user in a post.
    """
    post = get_object_or_404(Post, pk=post_id)
    
    # Only post creator, organization admin, or system admin can tag users
    if post.user != request.user and not (
        post.organization and is_organization_admin(request.user, post.organization)
    ) and request.user.role != 'ADMIN':
        return Response(
            {"error": "You do not have permission to tag users in this post"},
            status=status.HTTP_403_FORBIDDEN
        )
    
    # Get user to tag
    user_id = request.data.get('user_id')
    if not user_id:
        return Response(
            {"error": "User ID is required"},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    tagged_user = get_object_or_404(User, pk=user_id)
    
    # Check if user is already tagged
    if PostTag.objects.filter(post=post, user=tagged_user).exists():
        return Response(
            {"error": "User is already tagged in this post"},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Create tag
    x_position = request.data.get('x_position')
    y_position = request.data.get('y_position')
    
    tag = PostTag.objects.create(
        post=post,
        user=tagged_user,
        x_position=x_position,
        y_position=y_position
    )
    
    return Response(
        PostTagSerializer(tag).data,
        status=status.HTTP_201_CREATED
    )

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def remove_user_tag(request, post_id, user_id):
    """
    Remove a user tag from a post.
    """
    post = get_object_or_404(Post, pk=post_id)
    tagged_user = get_object_or_404(User, pk=user_id)
    
    # Only post creator, tagged user, organization admin, or system admin can remove tags
    if post.user != request.user and tagged_user != request.user and not (
        post.organization and is_organization_admin(request.user, post.organization)
    ) and request.user.role != 'ADMIN':
        return Response(
            {"error": "You do not have permission to remove this tag"},
            status=status.HTTP_403_FORBIDDEN
        )
    
    # Get the tag
    tag = get_object_or_404(PostTag, post=post, user=tagged_user)
    
    # Delete the tag
    tag.delete()
    
    return Response(
        {"message": "Tag removed"},
        status=status.HTTP_200_OK
    )

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_trend_posts(request, hashtag_name):
    """
    Get all posts for a specific trend/hashtag with pagination.
    """
    # Case insensitive hashtag lookup
    try:
        trend = Trend.objects.get(hashtag__name__iexact=hashtag_name)
    except Trend.DoesNotExist:
        return Response(
            {"error": "Trend not found"},
            status=status.HTTP_404_NOT_FOUND
        )

    # Get and paginate posts
    paginator = PageNumberPagination()
    paginator.page_size = 10
    posts = trend.posts.all().order_by('-created_at')
    
    page = paginator.paginate_queryset(posts, request)
    serializer = PostSerializer(page, many=True, context={'request': request})
    
    return paginator.get_paginated_response(serializer.data)
