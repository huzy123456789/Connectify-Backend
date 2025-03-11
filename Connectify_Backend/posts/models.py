from django.db import models
from accounts.models import User
from organizations.models import Organization


class Post(models.Model):
    """
    Model representing a user's post in the social media app.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts')
    organization = models.ForeignKey(
        Organization, 
        on_delete=models.CASCADE, 
        related_name='posts',
        null=True,
        blank=True
    )
    content = models.TextField(verbose_name="Post Content")
    ispublic = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Counters (for performance optimization)
    reaction_count = models.PositiveIntegerField(default=0)
    comment_count = models.PositiveIntegerField(default=0)
    share_count = models.PositiveIntegerField(default=0)
    
    def __str__(self):
        return f"Post by {self.user.username} at {self.created_at.strftime('%Y-%m-%d %H:%M')}"
    
    class Meta:
        ordering = ['-created_at']


class PostMedia(models.Model):
    """
    Model for storing media (images/videos) associated with posts.
    """
    MEDIA_TYPES = [
        ('image', 'Image'),
        ('video', 'Video'),
    ]
    
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='media')
    file = models.FileField(upload_to='post_media/')
    media_type = models.CharField(max_length=5, choices=MEDIA_TYPES)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.media_type} for post {self.post.id}"


class PostComment(models.Model):
    """
    Model representing comments on posts.
    """
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='post_comments')
    parent_comment = models.ForeignKey(
        'self', 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True, 
        related_name='replies'
    )
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Counter for nested comments and reactions
    reaction_count = models.PositiveIntegerField(default=0)
    reply_count = models.PositiveIntegerField(default=0)
    
    def __str__(self):
        return f"Comment by {self.user.username} on post {self.post.id}"
    
    class Meta:
        ordering = ['created_at']


class ReactionType(models.Model):
    """
    Model for defining different types of reactions (like, love, haha, etc.)
    """
    name = models.CharField(max_length=20, unique=True)
    emoji = models.CharField(max_length=10)
    
    def __str__(self):
        return f"{self.name} ({self.emoji})"


class PostReaction(models.Model):
    """
    Model representing reactions on posts.
    """
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='reactions')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='post_reactions')
    reaction_type = models.ForeignKey(ReactionType, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        # Ensure a user can only react once to a post
        unique_together = ['post', 'user']
    
    def __str__(self):
        return f"{self.user.username} reacted with {self.reaction_type.name} on post {self.post.id}"


class CommentReaction(models.Model):
    """
    Model representing reactions on comments.
    """
    comment = models.ForeignKey(PostComment, on_delete=models.CASCADE, related_name='reactions')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comment_reactions')
    reaction_type = models.ForeignKey(ReactionType, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        # Ensure a user can only react once to a comment
        unique_together = ['comment', 'user']
    
    def __str__(self):
        return f"{self.user.username} reacted with {self.reaction_type.name} on comment {self.comment.id}"


class PostShare(models.Model):
    """
    Model representing shares of posts.
    """
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='shares')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='shared_posts')
    created_at = models.DateTimeField(auto_now_add=True)
    
    # Optional additional content when sharing
    additional_content = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return f"Post {self.post.id} shared by {self.user.username}"


class PostTag(models.Model):
    """
    Model representing user tags in posts.
    """
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='tags')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='post_tags')
    created_at = models.DateTimeField(auto_now_add=True)
    
    # Position coordinates for tagging in media (optional)
    x_position = models.FloatField(null=True, blank=True)
    y_position = models.FloatField(null=True, blank=True)
    
    class Meta:
        unique_together = ['post', 'user']
    
    def __str__(self):
        return f"{self.user.username} tagged in post {self.post.id}"


class Hashtag(models.Model):
    """
    Model for storing hashtags.
    """
    name = models.CharField(max_length=100, unique=True)
    
    def __str__(self):
        return f"#{self.name}"


class PostHashtag(models.Model):
    """
    Model representing hashtags used in posts.
    """
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='hashtags')
    hashtag = models.ForeignKey(Hashtag, on_delete=models.CASCADE, related_name='posts')
    
    class Meta:
        unique_together = ['post', 'hashtag']
    
    def __str__(self):
        return f"#{self.hashtag.name} in post {self.post.id}"



    