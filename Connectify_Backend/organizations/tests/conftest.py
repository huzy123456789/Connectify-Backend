import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from organizations.models import Organization

User = get_user_model()

@pytest.fixture
def api_client():
    """Return an API client for testing."""
    return APIClient()

@pytest.fixture
def admin_user():
    """Create an admin user for testing."""
    return User.objects.create_user(
        username='admin_test',
        email='admin@example.com',
        password='admin123',
        role='ADMIN',
        is_staff=True,
        is_superuser=True
    )

@pytest.fixture
def regular_user():
    """Create a regular user for testing."""
    return User.objects.create_user(
        username='user_test',
        email='user@example.com',
        password='user123',
        role='USER',
        is_staff=False,
        is_superuser=False
    )

@pytest.fixture
def admin_token(api_client, admin_user):
    """Get authentication token for admin user."""
    url = reverse('accounts:login')
    data = {
        'login': 'admin_test',
        'password': 'admin123'
    }
    response = api_client.post(url, data)
    return response.data['access']

@pytest.fixture
def user_token(api_client, regular_user):
    """Get authentication token for regular user."""
    url = reverse('accounts:login')
    data = {
        'login': 'user_test',
        'password': 'user123'
    }
    response = api_client.post(url, data)
    return response.data['access']

@pytest.fixture
def admin_organization(admin_user):
    """Create an organization owned by the admin user."""
    org = Organization.objects.create(
        name='Admin Organization',
        description='This is an organization created by an admin'
    )
    org.users.add(admin_user)
    return org

@pytest.fixture
def user_organization(regular_user):
    """Create an organization owned by the regular user."""
    org = Organization.objects.create(
        name='User Organization',
        description='This is an organization created by a regular user'
    )
    org.users.add(regular_user)
    return org 