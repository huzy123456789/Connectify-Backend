from django.shortcuts import render
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.db.models import Q
from django.contrib.auth import get_user_model

from .models import Organization, OrganizationAdmins
from .serializers import (
    OrganizationSerializer, 
    OrganizationDetailSerializer,
    OrganizationCreateSerializer,
    OrganizationUpdateSerializer,
    OrganizationUserAddSerializer,
    OrganizationUserRemoveSerializer,
    UserSerializer
)
from accounts.permissions import IsAdminUser

User = get_user_model()

def is_organization_admin(user, organization):
    """Check if a user is an admin of the organization"""
    return OrganizationAdmins.objects.filter(organization=organization, admin=user).exists()

# Create Organization
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_organization(request):
    """
    Create a new organization.
    """
    serializer = OrganizationCreateSerializer(data=request.data)
    if serializer.is_valid():
        organization = serializer.save()
        # Add the creator as a user of the organization
        organization.users.add(request.user)
        # Make the creator an admin of the organization
        OrganizationAdmins.objects.create(organization=organization, admin=request.user)
        return Response(
            OrganizationSerializer(organization).data, 
            status=status.HTTP_201_CREATED
        )
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# Get All Organizations
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_organizations(request):
    """
    Get all organizations the user is a member of or an admin of.
    """
    # Get organizations where user is a member
    member_organizations = request.user.organizations.all()
    # Get organizations where user is an admin
    admin_organizations = Organization.objects.filter(organization_admins__admin=request.user)
    # Combine and remove duplicates
    organizations = (member_organizations | admin_organizations).distinct()
    serializer = OrganizationSerializer(organizations, many=True)
    return Response(serializer.data)

# Get All Organizations (System Admin Only - if needed)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_all_organizations(request):
    """
    Get all organizations (system admin only).
    """
    # Check if user is a system admin (role='ADMIN')
    if request.user.role == 'ADMIN':
        organizations = Organization.objects.all()
        serializer = OrganizationSerializer(organizations, many=True)
        return Response(serializer.data)
    else:
        return Response(
            {"error": "Only system administrators can access this endpoint"},
            status=status.HTTP_403_FORBIDDEN
        )

# Get Organization Detail
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_organization_detail(request, pk):
    """
    Get details of a specific organization.
    """
    # Get the organization
    organization = get_object_or_404(Organization, pk=pk)
    
    # Check if user is a member or an admin of the organization
    is_member = organization.users.filter(id=request.user.id).exists()
    is_admin = is_organization_admin(request.user, organization)
    is_system_admin = request.user.role == 'ADMIN'
    
    if not (is_member or is_admin or is_system_admin):
        return Response(
            {"error": "You do not have permission to view this organization"},
            status=status.HTTP_403_FORBIDDEN
        )
    
    serializer = OrganizationDetailSerializer(organization)
    return Response(serializer.data)

# Update Organization
@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_organization(request, pk):
    """
    Update an existing organization.
    """
    # Get the organization
    organization = get_object_or_404(Organization, pk=pk)
    
    # Check if user is an admin of the organization or a system admin
    is_org_admin = is_organization_admin(request.user, organization)
    is_system_admin = request.user.role == 'ADMIN'
    
    if not (is_org_admin or is_system_admin):
        return Response(
            {"error": "Only organization administrators can update the organization"},
            status=status.HTTP_403_FORBIDDEN
        )
    
    serializer = OrganizationUpdateSerializer(organization, data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(
            OrganizationDetailSerializer(organization).data,
            status=status.HTTP_200_OK
        )
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# Delete Organization
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_organization(request, pk):
    """
    Delete an organization.
    """
    # Get the organization
    organization = get_object_or_404(Organization, pk=pk)
    
    # Check if user is an admin of the organization or a system admin
    is_org_admin = is_organization_admin(request.user, organization)
    is_system_admin = request.user.role == 'ADMIN'
    
    if not (is_org_admin or is_system_admin):
        return Response(
            {"error": "Only organization administrators can delete the organization"},
            status=status.HTTP_403_FORBIDDEN
        )
    
    organization.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)

# Add Users to Organization
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_users_to_organization(request, pk):
    """
    Add users to an organization.
    """
    # Get the organization
    organization = get_object_or_404(Organization, pk=pk)
    
    # Check if user is an admin of the organization or a system admin
    is_org_admin = is_organization_admin(request.user, organization)
    is_system_admin = request.user.role == 'ADMIN' or request.user.role == 'SUPERUSER'
    
    if not (is_org_admin or is_system_admin):
        return Response(
            {"error": "Only organization administrators can add users to the organization"},
            status=status.HTTP_403_FORBIDDEN
        )
    
    serializer = OrganizationUserAddSerializer(data=request.data)
    if serializer.is_valid():
        user_ids = serializer.validated_data['user_ids']
        users = User.objects.filter(id__in=user_ids)
        
        # Add users to the organization
        for user in users:
            organization.users.add(user)
        
        return Response(
            OrganizationDetailSerializer(organization).data,
            status=status.HTTP_200_OK
        )
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# Remove Users from Organization
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def remove_users_from_organization(request, pk):
    """
    Remove users from an organization.
    """
    # Get the organization
    organization = get_object_or_404(Organization, pk=pk)
    
    # Check if user is an admin of the organization or a system admin
    is_org_admin = is_organization_admin(request.user, organization)
    is_system_admin = request.user.role == 'ADMIN'
    
    if not (is_org_admin or is_system_admin):
        return Response(
            {"error": "Only organization administrators can remove users from the organization"},
            status=status.HTTP_403_FORBIDDEN
        )
    
    serializer = OrganizationUserRemoveSerializer(data=request.data)
    if serializer.is_valid():
        user_ids = serializer.validated_data['user_ids']
        
        # Don't allow removing organization admins (except by system admin)
        if not is_system_admin:
            admin_ids = list(OrganizationAdmins.objects.filter(
                organization=organization
            ).values_list('admin_id', flat=True))
            
            if any(user_id in admin_ids for user_id in user_ids):
                return Response(
                    {"error": "Cannot remove organization administrators"},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        # Don't allow removing the last user
        if organization.users.count() <= len(user_ids):
            return Response(
                {"error": "Cannot remove all users from an organization"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Remove users from the organization
        for user_id in user_ids:
            try:
                user = User.objects.get(id=user_id)
                organization.users.remove(user)
            except User.DoesNotExist:
                pass
        
        return Response(
            OrganizationDetailSerializer(organization).data,
            status=status.HTTP_200_OK
        )
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# Add Organization Admins
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_organization_admins(request, pk):
    """
    Add administrators to an organization.
    """
    # Get the organization
    organization = get_object_or_404(Organization, pk=pk)
    
    # Check if user is an admin of the organization or a system admin
    is_org_admin = is_organization_admin(request.user, organization)
    is_system_admin = request.user.role == 'ADMIN'
    
    if not (is_org_admin or is_system_admin):
        return Response(
            {"error": "Only organization administrators can add new administrators"},
            status=status.HTTP_403_FORBIDDEN
        )
    
    serializer = OrganizationUserAddSerializer(data=request.data)
    if serializer.is_valid():
        user_ids = serializer.validated_data['user_ids']
        users = User.objects.filter(id__in=user_ids)
        
        # Add users as organization admins
        for user in users:
            # First ensure the user is a member of the organization
            if not organization.users.filter(id=user.id).exists():
                organization.users.add(user)
            
            # Then make them an admin if they aren't already
            if not OrganizationAdmins.objects.filter(organization=organization, admin=user).exists():
                OrganizationAdmins.objects.create(organization=organization, admin=user)
        
        return Response(
            OrganizationDetailSerializer(organization).data,
            status=status.HTTP_200_OK
        )
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# Remove Organization Admins
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def remove_organization_admins(request, pk):
    """
    Remove administrators from an organization.
    """
    # Get the organization
    organization = get_object_or_404(Organization, pk=pk)
    
    # Check if user is an admin of the organization or a system admin
    is_org_admin = is_organization_admin(request.user, organization)
    is_system_admin = request.user.role == 'ADMIN'
    
    if not (is_org_admin or is_system_admin):
        return Response(
            {"error": "Only organization administrators can remove administrators"},
            status=status.HTTP_403_FORBIDDEN
        )
    
    serializer = OrganizationUserRemoveSerializer(data=request.data)
    if serializer.is_valid():
        user_ids = serializer.validated_data['user_ids']
        
        # Don't allow removing yourself as an admin (except for system admin)
        if not is_system_admin and request.user.id in user_ids:
            return Response(
                {"error": "You cannot remove yourself as an administrator"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Don't allow removing the last admin
        admin_count = OrganizationAdmins.objects.filter(organization=organization).count()
        if admin_count <= len(user_ids):
            return Response(
                {"error": "Cannot remove all administrators from an organization"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Remove users as organization admins
        OrganizationAdmins.objects.filter(
            organization=organization,
            admin_id__in=user_ids
        ).delete()
        
        return Response(
            OrganizationDetailSerializer(organization).data,
            status=status.HTTP_200_OK
        )
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# Get Organization Admins
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_organization_admins(request, pk):
    """
    Get all administrators of an organization.
    """
    # Get the organization
    organization = get_object_or_404(Organization, pk=pk)
    
    # Check if user is a member or an admin of the organization or a system admin
    is_member = organization.users.filter(id=request.user.id).exists()
    is_org_admin = is_organization_admin(request.user, organization)
    is_system_admin = request.user.role == 'ADMIN'
    
    if not (is_member or is_org_admin or is_system_admin):
        return Response(
            {"error": "You do not have permission to view this organization's administrators"},
            status=status.HTTP_403_FORBIDDEN
        )
    
    # Get all admin users for this organization
    admin_users = User.objects.filter(admin_organizations__organization=organization)
    serializer = UserSerializer(admin_users, many=True)
    
    return Response(serializer.data)

# Search Organizations
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def search_organizations(request):
    """
    Search for organizations by name or description.
    """
    query = request.query_params.get('q', '')
    if not query:
        return Response(
            {"error": "Search query parameter 'q' is required"},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # If user is system admin, search all organizations
    if request.user.role == 'ADMIN':
        organizations = Organization.objects.filter(
            Q(name__icontains=query) | Q(description__icontains=query)
        )
    else:
        # Otherwise, only search organizations the user is a member of or admin of
        member_orgs = request.user.organizations.filter(
            Q(name__icontains=query) | Q(description__icontains=query)
        )
        admin_orgs = Organization.objects.filter(
            organization_admins__admin=request.user
        ).filter(
            Q(name__icontains=query) | Q(description__icontains=query)
        )
        organizations = (member_orgs | admin_orgs).distinct()
    
    serializer = OrganizationSerializer(organizations, many=True)
    return Response(serializer.data)

# Get User's Organizations
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_organizations(request, user_id=None):
    """
    Get organizations for a specific user or the current user.
    """
    if user_id:
        # Check if the requesting user has permission to view this user's organizations
        user = get_object_or_404(User, pk=user_id)
        
        # System admin can view any user's organizations
        if request.user.role == 'ADMIN':
            organizations = user.organizations.all()
        else:
            # For regular users, check if they share any organizations with the target user
            # Get organizations where both users are members
            shared_orgs = Organization.objects.filter(
                users=request.user
            ).filter(
                users=user
            )
            
            # Get organizations where requesting user is an admin and target user is a member
            admin_orgs = Organization.objects.filter(
                organization_admins__admin=request.user,
                users=user
            )
            
            organizations = (shared_orgs | admin_orgs).distinct()
            
            # If no shared organizations, return an error
            if not organizations.exists():
                return Response(
                    {"error": "You do not have permission to view this user's organizations"},
                    status=status.HTTP_403_FORBIDDEN
                )
    else:
        # Get current user's organizations (both member and admin)
        member_orgs = request.user.organizations.all()
        admin_orgs = Organization.objects.filter(organization_admins__admin=request.user)
        organizations = (member_orgs | admin_orgs).distinct()
    
    serializer = OrganizationSerializer(organizations, many=True)
    return Response(serializer.data)

# Get Organization Users
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_organization_users(request, id):
    """
    Get all users in an organization.
    """
    # Ensure the user is authenticated
    if not request.user.is_authenticated:
        return Response(
            {"error": "Authentication credentials were not provided."},
            status=status.HTTP_401_UNAUTHORIZED
        )

    # Get the organization
    organization = get_object_or_404(Organization, pk=id)

    print(request)

    is_system_admin = getattr(request.user, "role", None) == "SUPERUSER"

    if not (is_system_admin):
        return Response(
            {"error": "You do not have permission to view this organization's users."},
            status=status.HTTP_403_FORBIDDEN
        )

    # Get all users for this organization
    users = organization.users.all()
    serializer = UserSerializer(users, many=True)

    return Response(serializer.data, status=status.HTTP_200_OK)

# Delete Users from Organization
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def delete_organization_users(request, id):
    """
    Delete users from an organization.
    """
    # Ensure the user is authenticated
    if not request.user.is_authenticated:
        return Response(
            {"error": "Authentication credentials were not provided."},
            status=status.HTTP_401_UNAUTHORIZED
        )

    # Get the organization
    organization = get_object_or_404(Organization, pk=id)

    is_system_admin = getattr(request.user, "role", None) == "SUPERUSER"

    # Check if the user is a superuser
    if not is_system_admin:
        return Response(
            {"error": "You do not have permission to delete users from this organization."},
            status=status.HTTP_403_FORBIDDEN
        )

    # Validate the request data
    user_ids = request.data.get("user_ids", [])
    if not isinstance(user_ids, list) or not user_ids:
        return Response(
            {"error": "A list of user IDs is required."},
            status=status.HTTP_400_BAD_REQUEST
        )

    # Remove users from the organization
    users_to_remove = User.objects.filter(id__in=user_ids, organizations=organization)
    if not users_to_remove.exists():
        return Response(
            {"error": "No valid users found to remove."},
            status=status.HTTP_400_BAD_REQUEST
        )

    for user in users_to_remove:
        organization.users.remove(user)

    return Response(
        {"message": "Users removed successfully."},
        status=status.HTTP_200_OK
    )