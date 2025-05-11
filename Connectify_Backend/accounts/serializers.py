from rest_framework import serializers
from django.contrib.auth import authenticate
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from django.utils.translation import gettext_lazy as _

from .models import User

class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for the custom User model.
    """
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name', 'role', 'bio', 'dob', 'profile_image')
        read_only_fields = ('id', 'role')


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    Custom token serializer that includes user role in the response.
    Also allows login with either username or email.
    """
    username_field = 'login'
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields[self.username_field] = serializers.CharField()
        self.fields.pop('username', None)  # Remove the username field
    
    def validate(self, attrs):
        # Check if login is email or username
        login = attrs.get(self.username_field)
        password = attrs.get('password')
        
        if not login or not password:
            raise serializers.ValidationError(_('Must include "login" and "password".'))
        
        # Try to authenticate with username
        user = authenticate(username=login, password=password)
        
        # If authentication with username fails, try with email
        if user is None:
            # Find user by email
            try:
                user_obj = User.objects.get(email=login)
                user = authenticate(username=user_obj.username, password=password)
            except User.DoesNotExist:
                user = None
        
        if user is None:
            raise serializers.ValidationError(_('Unable to log in with provided credentials.'))
        
        if not user.is_active:
            raise serializers.ValidationError(_('User account is disabled.'))
        
        refresh = RefreshToken.for_user(user)
        
        data = {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'role': user.role,
                'first_name': user.first_name,
                'last_name': user.last_name,
            }
        }
        
        return data