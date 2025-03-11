from django.urls import path
from . import views

app_name = 'organizations'

urlpatterns = [
    # Create and list organizations
    path('', views.get_organizations, name='organization_list'),
    path('create/', views.create_organization, name='organization_create'),
    path('all/', views.get_all_organizations, name='organization_list_all'),
    
    # Retrieve, update, delete organization
    path('<int:pk>/', views.get_organization_detail, name='organization_detail'),
    path('<int:pk>/update/', views.update_organization, name='organization_update'),
    path('<int:pk>/delete/', views.delete_organization, name='organization_delete'),
    
    # User management in organizations
    path('<int:pk>/add-users/', views.add_users_to_organization, name='organization_add_users'),
    path('<int:pk>/remove-users/', views.remove_users_from_organization, name='organization_remove_users'),
    
    # Search organizations
    path('search/', views.search_organizations, name='organization_search'),
    
    # User's organizations
    path('user/', views.get_user_organizations, name='user_organizations'),
    path('user/<int:user_id>/', views.get_user_organizations, name='user_organizations_by_id'),
]
