from django.contrib import admin
from .models import (
    Post, PostMedia, PostComment, ReactionType, 
    PostReaction, CommentReaction, PostShare, 
    PostTag, Hashtag, PostHashtag
)

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'organization', 'ispublic', 'reaction_count', 'comment_count', 'share_count', 'created_at')
    list_filter = ('ispublic', 'created_at')
    search_fields = ('content', 'user__username', 'organization__name')
    date_hierarchy = 'created_at'

@admin.register(PostMedia)
class PostMediaAdmin(admin.ModelAdmin):
    list_display = ('id', 'post', 'media_type', 'uploaded_at')
    list_filter = ('media_type', 'uploaded_at')

@admin.register(PostComment)
class PostCommentAdmin(admin.ModelAdmin):
    list_display = ('id', 'post', 'user', 'parent_comment', 'reaction_count', 'reply_count', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('content', 'user__username')
    date_hierarchy = 'created_at'

@admin.register(ReactionType)
class ReactionTypeAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'emoji')
    search_fields = ('name',)

@admin.register(PostReaction)
class PostReactionAdmin(admin.ModelAdmin):
    list_display = ('id', 'post', 'user', 'reaction_type', 'created_at')
    list_filter = ('reaction_type', 'created_at')
    search_fields = ('user__username',)
    date_hierarchy = 'created_at'

@admin.register(CommentReaction)
class CommentReactionAdmin(admin.ModelAdmin):
    list_display = ('id', 'comment', 'user', 'reaction_type', 'created_at')
    list_filter = ('reaction_type', 'created_at')
    search_fields = ('user__username',)
    date_hierarchy = 'created_at'

@admin.register(PostShare)
class PostShareAdmin(admin.ModelAdmin):
    list_display = ('id', 'post', 'user', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('user__username', 'additional_content')
    date_hierarchy = 'created_at'

@admin.register(PostTag)
class PostTagAdmin(admin.ModelAdmin):
    list_display = ('id', 'post', 'user', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('user__username',)
    date_hierarchy = 'created_at'

@admin.register(Hashtag)
class HashtagAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    search_fields = ('name',)

@admin.register(PostHashtag)
class PostHashtagAdmin(admin.ModelAdmin):
    list_display = ('id', 'post', 'hashtag')
    search_fields = ('hashtag__name',)
