from rest_framework import serializers
from accounts.models import User
from .models import (
    Post, PostMedia, PostComment, ReactionType, 
    PostReaction, CommentReaction, PostShare, 
    PostTag, Hashtag, PostHashtag
)
from accounts.serializers import UserSerializer


class HashtagSerializer(serializers.ModelSerializer):
    """
    Serializer for Hashtag model.
    """
    post_count = serializers.IntegerField(read_only=True, required=False)
    
    class Meta:
        model = Hashtag
        fields = ['id', 'name', 'post_count']


class PostMediaSerializer(serializers.ModelSerializer):
    """
    Serializer for PostMedia model.
    """
    class Meta:
        model = PostMedia
        fields = ['id', 'file', 'media_type', 'uploaded_at']


class ReactionTypeSerializer(serializers.ModelSerializer):
    """
    Serializer for ReactionType model.
    """
    class Meta:
        model = ReactionType
        fields = ['id', 'name', 'emoji']


class PostReactionSerializer(serializers.ModelSerializer):
    """
    Serializer for PostReaction model.
    """
    user = UserSerializer(read_only=True)
    reaction_type = ReactionTypeSerializer(read_only=True)
    
    class Meta:
        model = PostReaction
        fields = ['id', 'user', 'reaction_type', 'created_at']


class CommentReactionSerializer(serializers.ModelSerializer):
    """
    Serializer for CommentReaction model.
    """
    user = UserSerializer(read_only=True)
    reaction_type = ReactionTypeSerializer(read_only=True)
    
    class Meta:
        model = CommentReaction
        fields = ['id', 'user', 'reaction_type', 'created_at']


class PostTagSerializer(serializers.ModelSerializer):
    """
    Serializer for PostTag model.
    """
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = PostTag
        fields = ['id', 'user', 'x_position', 'y_position', 'created_at']


class PostShareSerializer(serializers.ModelSerializer):
    """
    Serializer for PostShare model.
    """
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = PostShare
        fields = ['id', 'user', 'additional_content', 'created_at']


class PostCommentSerializer(serializers.ModelSerializer):
    """
    Serializer for PostComment model.
    """
    user = UserSerializer(read_only=True)
    reactions = serializers.SerializerMethodField()
    
    class Meta:
        model = PostComment
        fields = [
            'id', 'user', 'content', 'parent_comment', 
            'reaction_count', 'reply_count', 'reactions',
            'created_at', 'updated_at'
        ]
    
    def get_reactions(self, obj):
        # Get the most recent reactions (limit to 5)
        reactions = CommentReaction.objects.filter(comment=obj).order_by('-created_at')[:5]
        return CommentReactionSerializer(reactions, many=True).data


class PostCommentCreateSerializer(serializers.Serializer):
    """
    Serializer for creating a PostComment.
    """
    content = serializers.CharField(required=True)
    parent_comment_id = serializers.IntegerField(required=False, allow_null=True)


class PostSerializer(serializers.ModelSerializer):
    """
    Serializer for Post model (list view).
    """
    user = serializers.SerializerMethodField()
    media = PostMediaSerializer(many=True, read_only=True)
    hashtags = serializers.SerializerMethodField()
    reactions_summary = serializers.SerializerMethodField()
    
    class Meta:
        model = Post
        fields = [
            'id', 'user', 'organization', 'content', 'ispublic',
            'reaction_count', 'comment_count', 'share_count',
            'media', 'hashtags', 'reactions_summary', 'type',
            'created_at', 'updated_at'
        ]
    
    def get_user(self, obj):
        return {
            "id": obj.user.id,
            "username": obj.user.username,
            "first_name": obj.user.first_name,
            "last_name": obj.user.last_name,
            "profile_image": obj.user.profile_image
        }
    
    def get_hashtags(self, obj):
        hashtags = Hashtag.objects.filter(posts__post=obj)
        return HashtagSerializer(hashtags, many=True).data
    
    def get_reactions_summary(self, obj):
        # Get counts of each reaction type
        reaction_counts = {}
        reactions = PostReaction.objects.filter(post=obj)
        
        for reaction in reactions:
            reaction_type = reaction.reaction_type.name
            if reaction_type in reaction_counts:
                reaction_counts[reaction_type] += 1
            else:
                reaction_counts[reaction_type] = 1
        
        return reaction_counts


class PostDetailSerializer(PostSerializer):
    """
    Detailed serializer for Post model (detail view).
    """
    comments = serializers.SerializerMethodField()
    tags = PostTagSerializer(many=True, read_only=True)
    reactions = serializers.SerializerMethodField()
    shares = serializers.SerializerMethodField()
    
    class Meta(PostSerializer.Meta):
        fields = PostSerializer.Meta.fields + ['comments', 'tags', 'reactions', 'shares']
    
    def get_comments(self, obj):
        # Get only top-level comments (limit to 5)
        comments = PostComment.objects.filter(post=obj, parent_comment=None).order_by('-created_at')[:5]
        return PostCommentSerializer(comments, many=True).data
    
    def get_reactions(self, obj):
        # Get the most recent reactions (limit to 10)
        reactions = PostReaction.objects.filter(post=obj).order_by('-created_at')[:10]
        return PostReactionSerializer(reactions, many=True).data
    
    def get_shares(self, obj):
        # Get the most recent shares (limit to 5)
        shares = PostShare.objects.filter(post=obj).order_by('-created_at')[:5]
        return PostShareSerializer(shares, many=True).data


class PostCreateSerializer(serializers.Serializer):
    """
    Serializer for creating a Post.
    """
    content = serializers.CharField(required=True)
    organization_id = serializers.IntegerField(required=False, allow_null=True)
    ispublic = serializers.BooleanField(default=True)
    type = serializers.ChoiceField(choices=['post', 'announcement'], default='post')
    tagged_user_ids = serializers.ListField(
        child=serializers.IntegerField(),
        required=False,
        default=[]
    )


class PostUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for updating a Post.
    """
    class Meta:
        model = Post
        fields = ['content', 'ispublic']