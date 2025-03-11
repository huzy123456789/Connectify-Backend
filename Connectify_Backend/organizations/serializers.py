from rest_framework import serializers
from .models import Organization, OrganizationAdmins
from accounts.serializers import UserSerializer

class OrganizationSerializer(serializers.ModelSerializer):
    """
    Serializer for the Organization model.
    """
    users = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
    
    class Meta:
        model = Organization
        fields = ['id', 'name', 'description', 'users', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        # Add a field to indicate organization admins
        representation['admins'] = list(
            OrganizationAdmins.objects.filter(organization=instance)
            .values_list('admin_id', flat=True)
        )
        return representation

class OrganizationDetailSerializer(serializers.ModelSerializer):
    """
    Detailed serializer for the Organization model that includes user details.
    """
    users = UserSerializer(many=True, read_only=True)
    
    class Meta:
        model = Organization
        fields = ['id', 'name', 'description', 'users', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        # Add admin users with full details
        admin_ids = OrganizationAdmins.objects.filter(organization=instance).values_list('admin_id', flat=True)
        admin_users = [user for user in representation['users'] if user['id'] in admin_ids]
        representation['admins'] = admin_users
        return representation

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
        min_length=1
    )

class OrganizationUserRemoveSerializer(serializers.Serializer):
    """
    Serializer for removing users from an Organization.
    """
    user_ids = serializers.ListField(
        child=serializers.IntegerField(),
        min_length=1
    ) 