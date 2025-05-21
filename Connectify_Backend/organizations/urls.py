from django.urls import path
from . import views

app_name = 'organizations'

urlpatterns = [
    # Create and list organizations
    path('create/', views.create_organization, name='organization_create'),
    path('', views.get_organizations, name='organization_list'),
    path('all/', views.get_all_organizations, name='organization_list_all'),
    
    # Retrieve, update, delete organization
    path('<int:pk>/', views.get_organization_detail, name='organization_detail'),
    path('<int:pk>/update/', views.update_organization, name='organization_update'),
    path('<int:pk>/delete/', views.delete_organization, name='organization_delete'),
    
    # User management in organizations
    path('<int:pk>/add-users/', views.add_users_to_organization, name='organization_add_users'),
    path('<int:pk>/remove-users/', views.remove_users_from_organization, name='organization_remove_users'),
    
    # Organization admin management
    path('<int:pk>/admins/', views.get_organization_admins, name='organization_admins'),
    path('<int:pk>/add-admins/', views.add_organization_admins, name='organization_add_admins'),
    path('<int:pk>/remove-admins/', views.remove_organization_admins, name='organization_remove_admins'),
    
    # Search organizations
    path('search/', views.search_organizations, name='organization_search'),
    
    # User's organizations
    path('user/', views.get_user_organizations, name='user_organizations'),
    path('user/<int:user_id>/', views.get_user_organizations, name='user_organizations_by_id'),
    
    # Organization users
    path('<int:id>/users/', views.get_organization_users, name='organization_users'),
    path('<int:id>/users/delete/', views.delete_organization_users, name='delete_organization_users'),
]
