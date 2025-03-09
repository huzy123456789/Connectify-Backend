from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import User

class CustomUserCreationForm(UserCreationForm):
    """
    Custom form for creating new users with the custom User model.
    """
    class Meta:
        model = User
        fields = ('username', 'email', 'role')

class CustomUserChangeForm(UserChangeForm):
    """
    Custom form for updating users with the custom User model.
    """
    class Meta:
        model = User
        fields = ('username', 'email', 'role') 