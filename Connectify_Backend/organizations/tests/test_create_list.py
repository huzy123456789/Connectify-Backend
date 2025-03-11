import pytest
from django.urls import reverse
from rest_framework import status
from organizations.models import Organization

# Test Organization Creation
@pytest.mark.django_db
class TestCreateOrganization:
    def test_create_organization_as_admin(self, api_client, admin_token):
        """Test creating an organization as an admin user"""
        url = reverse('organizations:organization_create')
        data = {
            'name': 'Test Admin Organization',
            'description': 'This is a test organization created by an admin'
        }
        api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {admin_token}')
        response = api_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['name'] == data['name']
        assert response.data['description'] == data['description']
        
        # Verify the admin user is added to the organization
        org_id = response.data['id']
        org = Organization.objects.get(id=org_id)
        assert org.users.filter(username='admin_test').exists()
    
    def test_create_organization_as_user(self, api_client, user_token):
        """Test creating an organization as a regular user"""
        url = reverse('organizations:organization_create')
        data = {
            'name': 'Test User Organization',
            'description': 'This is a test organization created by a regular user'
        }
        api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {user_token}')
        response = api_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['name'] == data['name']
        assert response.data['description'] == data['description']
        
        # Verify the user is added to the organization
        org_id = response.data['id']
        org = Organization.objects.get(id=org_id)
        assert org.users.filter(username='user_test').exists()
    
    def test_create_organization_unauthenticated(self, api_client):
        """Test creating an organization without authentication (should fail)"""
        url = reverse('organizations:organization_create')
        data = {
            'name': 'Test Unauthenticated Organization',
            'description': 'This should fail'
        }
        response = api_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

# Test Getting Organizations
@pytest.mark.django_db
class TestGetOrganizations:
    def test_get_organizations_as_admin(self, api_client, admin_token, admin_organization):
        """Test getting organizations as an admin user"""
        url = reverse('organizations:organization_list')
        api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {admin_token}')
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) >= 1
        assert any(org['name'] == 'Admin Organization' for org in response.data)
    
    def test_get_organizations_as_user(self, api_client, user_token, user_organization):
        """Test getting organizations as a regular user"""
        url = reverse('organizations:organization_list')
        api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {user_token}')
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) >= 1
        assert any(org['name'] == 'User Organization' for org in response.data)
    
    def test_get_all_organizations_as_admin(self, api_client, admin_token, admin_organization, user_organization):
        """Test getting all organizations as an admin user"""
        url = reverse('organizations:organization_list_all')
        api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {admin_token}')
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) >= 2
        assert any(org['name'] == 'Admin Organization' for org in response.data)
        assert any(org['name'] == 'User Organization' for org in response.data)
    
    def test_get_all_organizations_as_user(self, api_client, user_token):
        """Test getting all organizations as a regular user (should fail)"""
        url = reverse('organizations:organization_list_all')
        api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {user_token}')
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_403_FORBIDDEN 