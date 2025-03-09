from django.shortcuts import render
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.views import TokenRefreshView
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from .serializers import CustomTokenObtainPairSerializer, UserSerializer
from .permissions import IsAdminUser, IsRegularUser


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
