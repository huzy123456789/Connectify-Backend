from rest_framework import permissions
from .models import User

class IsAdminUser(permissions.BasePermission):
    """
    Custom permission to only allow users with ADMIN role to access.
    """
    message = "Only users with admin role are allowed to perform this action."

    def has_permission(self, request, view):
        return bool(
            request.user and 
            request.user.is_authenticated and 
            request.user.role == User.Role.ADMIN
        )

class IsRegularUser(permissions.BasePermission):
    """
    Custom permission to only allow users with USER role to access.
    """
    message = "Only regular users are allowed to perform this action."

    def has_permission(self, request, view):
        return bool(
            request.user and 
            request.user.is_authenticated and 
            request.user.role == User.Role.USER
        ) 