from django.shortcuts import render, get_object_or_404
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.views import TokenRefreshView
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError

from .serializers import CustomTokenObtainPairSerializer, UserSerializer, UserCreateSerializer, UserRoleUpdateSerializer
from .permissions import IsAdminUser, IsRegularUser, IsUserOrAdmin
from cloudinary.uploader import upload as cloudinary_upload
from cloudinary.exceptions import Error as CloudinaryError
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from organizations.models import Organization
from .models import User

class LoginView(APIView):
    """
    API view for user login. Accepts either username or email with password.
    Returns access token, refresh token, and user details including role.
    """
    permission_classes = [AllowAny]
    serializer_class = CustomTokenObtainPairSerializer
    
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        
        try:
            serializer.is_valid(raise_exception=True)
        except TokenError as e:
            return Response(
                {'error': str(e)}, 
                status=status.HTTP_401_UNAUTHORIZED
            )
            
        return Response(serializer.validated_data, status=status.HTTP_200_OK)


class CustomTokenRefreshView(TokenRefreshView):
    """
    Custom token refresh view that handles token refresh errors gracefully.
    """
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        
        try:
            serializer.is_valid(raise_exception=True)
        except TokenError as e:
            return Response(
                {'error': str(e)}, 
                status=status.HTTP_401_UNAUTHORIZED
            )
            
        return Response(serializer.validated_data, status=status.HTTP_200_OK)


class AdminOnlyView(APIView):
    """
    Test API endpoint that only allows users with ADMIN role.
    """
    permission_classes = [IsAdminUser]
    
    def get(self, request, *args, **kwargs):
        return Response({
            'message': 'You have successfully accessed an admin-only endpoint!',
            'user': {
                'id': request.user.id,
                'username': request.user.username,
                'email': request.user.email,
                'role': request.user.role,
            }
        }, status=status.HTTP_200_OK)


class UserOnlyView(APIView):
    """
    Test API endpoint that only allows users with USER role.
    """
    permission_classes = [IsRegularUser]
    
    def get(self, request, *args, **kwargs):
        return Response({
            'message': 'You have successfully accessed a user-only endpoint!',
            'user': {
                'id': request.user.id,
                'username': request.user.username,
                'email': request.user.email,
                'role': request.user.role,
            }
        }, status=status.HTTP_200_OK)


class UpdateProfileView(APIView):
    """
    API view to update user profile information, including profile picture, DOB, first name, last name, and bio.
    """
    permission_classes = [IsUserOrAdmin]  # Changed from IsRegularUser to IsUserOrAdmin

    def put(self, request, *args, **kwargs):
        user = request.user
        data = request.data
        print('Request data:', data)
        print('Request files:', request.FILES)
        # Handle profile picture upload
        profile_image_url = None
        if 'media' in request.FILES:  # Changed from 'profile_image' to 'media'
            try:
                upload_result = cloudinary_upload(request.FILES['media'], folder='user_profiles')
                profile_image_url = upload_result.get('secure_url')
            except CloudinaryError as e:
                return Response(
                    {"error": f"Failed to upload profile image: {str(e)}"},
                    status=status.HTTP_400_BAD_REQUEST
                )

        # Update user fields
        user.first_name = data.get('first_name', user.first_name)
        user.last_name = data.get('last_name', user.last_name)
        user.bio = data.get('bio', user.bio)
        user.dob = data.get('dob', user.dob)
        if profile_image_url:
            user.profile_image = profile_image_url

        user.save()

        return Response(
            {
                "message": "Profile updated successfully",
                "user": {
                    "id": user.id,
                    "username": user.username,
                    "email": user.email,
                    "first_name": user.first_name,
                    "last_name": user.last_name,
                    "bio": user.bio,
                    "dob": user.dob,
                    "profile_image": user.profile_image,
                }
            },
            status=status.HTTP_200_OK
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_profile(request):
    """Get the authenticated user's profile"""
    user = request.user
    serializer = UserSerializer(user)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([AllowAny])
def create_user(request):
    """
    Endpoint to create a new user.
    """
    serializer = UserCreateSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        return Response(UserSerializer(user).data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_user_role(request, organization_id, user_id):
    """
    Update a user's role within an organization.
    Only superusers can update roles.
    """
    # Check if the requesting user is a superuser

    is_system_admin = getattr(request.user, "role", None) == "SUPERUSER"
    if not is_system_admin:
        return Response(
            {"error": "Only superusers can update user roles"},
            status=status.HTTP_403_FORBIDDEN
        )

    # Get the organization
    organization = get_object_or_404(Organization, pk=organization_id)
    
    # Get the user to update
    user = get_object_or_404(User, pk=user_id)
    
    # Check if user is part of the organization
    if not organization.users.filter(id=user.id).exists():
        return Response(
            {"error": "User is not a member of this organization"},
            status=status.HTTP_400_BAD_REQUEST
        )

    serializer = UserRoleUpdateSerializer(user, data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(UserSerializer(user).data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
