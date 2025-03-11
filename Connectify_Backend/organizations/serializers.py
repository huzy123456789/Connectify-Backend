from rest_framework import serializers
from .models import Organization
from accounts.serializers import UserSerializer

class OrganizationSerializer(serializers.ModelSerializer):
    """
    Serializer for the Organization model.
    """
    class Meta:
        model = Organization
        fields = ['id', 'name', 'description', 'users', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']

class OrganizationDetailSerializer(serializers.ModelSerializer):
    """
    Detailed serializer for the Organization model that includes user details.
    """
    users = UserSerializer(many=True, read_only=True)
    
    class Meta:
        model = Organization
        fields = ['id', 'name', 'description', 'users', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']

class OrganizationCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating an Organization.
    """
    class Meta:
        model = Organization
        fields = ['name', 'description']

class OrganizationUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for updating an Organization.
    """
    class Meta:
        model = Organization
        fields = ['name', 'description']

class OrganizationUserAddSerializer(serializers.Serializer):
    """
    Serializer for adding users to an Organization.
    """
    user_ids = serializers.ListField(
        child=serializers.IntegerField(),
        required=True,
        help_text="List of user IDs to add to the organization"
    )

class OrganizationUserRemoveSerializer(serializers.Serializer):
    """
    Serializer for removing users from an Organization.
    """
    user_ids = serializers.ListField(
        child=serializers.IntegerField(),
        required=True,
        help_text="List of user IDs to remove from the organization"
    ) 