from django.shortcuts import render
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.db.models import Q
from django.contrib.auth import get_user_model

from .models import Organization
from .serializers import (
    OrganizationSerializer, 
    OrganizationDetailSerializer,
    OrganizationCreateSerializer,
    OrganizationUpdateSerializer,
    OrganizationUserAddSerializer,
    OrganizationUserRemoveSerializer
)
from accounts.permissions import IsAdminUser

User = get_user_model()

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
    Get all organizations the user is a member of.
    """
    organizations = request.user.organizations.all()
    serializer = OrganizationSerializer(organizations, many=True)
    return Response(serializer.data)

# Get All Organizations (Admin Only)
@api_view(['GET'])
@permission_classes([IsAdminUser])
def get_all_organizations(request):
    """
    Get all organizations (admin only).
    """
    organizations = Organization.objects.all()
    serializer = OrganizationSerializer(organizations, many=True)
    return Response(serializer.data)

# Get Organization Detail
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_organization_detail(request, pk):
    """
    Get details of a specific organization.
    """
    # Check if user is admin or a member of the organization
    if request.user.role == 'ADMIN':
        organization = get_object_or_404(Organization, pk=pk)
    else:
        organization = get_object_or_404(Organization, pk=pk, users=request.user)
    
    serializer = OrganizationDetailSerializer(organization)
    return Response(serializer.data)

# Update Organization
@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_organization(request, pk):
    """
    Update an existing organization.
    """
    # Check if user is admin or a member of the organization
    if request.user.role == 'ADMIN':
        organization = get_object_or_404(Organization, pk=pk)
    else:
        organization = get_object_or_404(Organization, pk=pk, users=request.user)
    
    serializer = OrganizationUpdateSerializer(organization, data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(OrganizationSerializer(organization).data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# Delete Organization
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_organization(request, pk):
    """
    Delete an organization.
    """
    # Check if user is admin or a member of the organization
    if request.user.role == 'ADMIN':
        organization = get_object_or_404(Organization, pk=pk)
    else:
        organization = get_object_or_404(Organization, pk=pk, users=request.user)
    
    organization.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)

# Add Users to Organization
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_users_to_organization(request, pk):
    """
    Add users to an organization.
    """
    # Check if user is admin or a member of the organization
    if request.user.role == 'ADMIN':
        organization = get_object_or_404(Organization, pk=pk)
    else:
        organization = get_object_or_404(Organization, pk=pk, users=request.user)
    
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
    # Check if user is admin or a member of the organization
    if request.user.role == 'ADMIN':
        organization = get_object_or_404(Organization, pk=pk)
    else:
        organization = get_object_or_404(Organization, pk=pk, users=request.user)
    
    serializer = OrganizationUserRemoveSerializer(data=request.data)
    if serializer.is_valid():
        user_ids = serializer.validated_data['user_ids']
        
        # Don't allow removing the last user
        if organization.users.count() <= len(user_ids):
            return Response(
                {"error": "Cannot remove all users from an organization"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Remove users from the organization
        users = User.objects.filter(id__in=user_ids)
        for user in users:
            organization.users.remove(user)
        
        return Response(
            OrganizationDetailSerializer(organization).data,
            status=status.HTTP_200_OK
        )
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

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
    
    # If user is admin, search all organizations
    if request.user.role == 'ADMIN':
        organizations = Organization.objects.filter(
            Q(name__icontains=query) | Q(description__icontains=query)
        )
    else:
        # Otherwise, only search organizations the user is a member of
        organizations = request.user.organizations.filter(
            Q(name__icontains=query) | Q(description__icontains=query)
        )
    
    serializer = OrganizationSerializer(organizations, many=True)
    return Response(serializer.data)

# Get User's Organizations
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_organizations(request, user_id=None):
    """
    Get organizations for a specific user or the current user.
    """
    if user_id and request.user.role == 'ADMIN':
        # Admin can view any user's organizations
        user = get_object_or_404(User, pk=user_id)
        organizations = user.organizations.all()
    else:
        # Regular users can only view their own organizations
        organizations = request.user.organizations.all()
    
    serializer = OrganizationSerializer(organizations, many=True)
    return Response(serializer.data)
