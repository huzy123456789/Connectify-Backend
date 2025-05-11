from django.urls import path
from . import views

app_name = 'posts'

urlpatterns = [
    # Post CRUD operations
    path('create/', views.create_post, name='post_create'),
    path('<int:pk>/', views.get_post_detail, name='post_detail'),
    path('<int:pk>/update/', views.update_post, name='post_update'),
    path('<int:pk>/delete/', views.delete_post, name='post_delete'),
    
    # Feed and timeline
    path('feed/', views.get_feed, name='feed'),
    path('user/', views.get_user_posts, name='user_posts'),
    path('user/<int:user_id>/', views.get_user_posts, name='user_posts_by_id'),
    path('organization/<int:org_id>/', views.get_organization_posts, name='organization_posts'),
    
    # Comment operations
    path('<int:post_id>/comments/', views.get_post_comments, name='post_comments'),
    path('<int:post_id>/comments/create/', views.create_comment, name='create_comment'),
    path('comments/<int:comment_id>/replies/', views.get_comment_replies, name='comment_replies'),
    path('comments/<int:comment_id>/update/', views.update_comment, name='update_comment'),
    path('comments/<int:comment_id>/delete/', views.delete_comment, name='delete_comment'),
    
    # Reaction operations
    path('reaction-types/', views.get_reaction_types, name='reaction_types'),
    path('<int:post_id>/react/', views.react_to_post, name='react_to_post'),
    path('<int:post_id>/unreact/', views.remove_post_reaction, name='remove_post_reaction'),
    path('comments/<int:comment_id>/react/', views.react_to_comment, name='react_to_comment'),
    path('comments/<int:comment_id>/unreact/', views.remove_comment_reaction, name='remove_comment_reaction'),
    
    # Share operations
    path('<int:post_id>/share/', views.share_post, name='share_post'),
    
    # Search operations
    path('search/', views.search_posts, name='search_posts'),
    path('hashtag/<str:hashtag_name>/', views.get_posts_by_hashtag, name='posts_by_hashtag'),
    path('trending-hashtags/', views.get_trending_hashtags, name='trending_hashtags'),
    path('trends/', views.get_trends, name='trends'),
    path('trend/<str:hashtag_name>/', views.get_trend_posts, name='trend_posts'),
    
    # Tag operations
    path('<int:post_id>/tag-user/', views.tag_user_in_post, name='tag_user'),
    path('<int:post_id>/untag-user/<int:user_id>/', views.remove_user_tag, name='untag_user'),
    
    # Announcements
    path('announcements/', views.get_announcements, name='announcements'),
]