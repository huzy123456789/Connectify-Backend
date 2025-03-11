import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from organizations.models import Organization
from organizations.serializers import OrganizationSerializer, OrganizationDetailSerializer

User = get_user_model()

@pytest.fixture
def api_client():
    return APIClient()

@pytest.fixture
def admin_user():
    """Create an admin user for testing"""
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
    """Create a regular user for testing"""
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
    """Get authentication token for admin user"""
    url = reverse('accounts:login')
    data = {
        'login': 'admin_test',
        'password': 'admin123'
    }
    response = api_client.post(url, data)
    return response.data['access']

@pytest.fixture
def user_token(api_client, regular_user):
    """Get authentication token for regular user"""
    url = reverse('accounts:login')
    data = {
        'login': 'user_test',
        'password': 'user123'
    }
    response = api_client.post(url, data)
    return response.data['access']

@pytest.fixture
def admin_organization(admin_user):
    """Create an organization owned by the admin user"""
    org = Organization.objects.create(
        name='Admin Organization',
        description='This is an organization created by an admin'
    )
    org.users.add(admin_user)
    return org

@pytest.fixture
def user_organization(regular_user):
    """Create an organization owned by the regular user"""
    org = Organization.objects.create(
        name='User Organization',
        description='This is an organization created by a regular user'
    )
    org.users.add(regular_user)
    return org

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

# Test Organization Detail
@pytest.mark.django_db
class TestOrganizationDetail:
    def test_get_organization_detail_as_admin(self, api_client, admin_token, admin_organization):
        """Test getting organization details as an admin user"""
        url = reverse('organizations:organization_detail', kwargs={'pk': admin_organization.id})
        api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {admin_token}')
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['name'] == 'Admin Organization'
        assert response.data['description'] == 'This is an organization created by an admin'
    
    def test_get_organization_detail_as_user(self, api_client, user_token, user_organization):
        """Test getting organization details as a regular user"""
        url = reverse('organizations:organization_detail', kwargs={'pk': user_organization.id})
        api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {user_token}')
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['name'] == 'User Organization'
        assert response.data['description'] == 'This is an organization created by a regular user'
    
    def test_get_organization_detail_as_admin_for_user_org(self, api_client, admin_token, user_organization):
        """Test admin accessing a user's organization"""
        url = reverse('organizations:organization_detail', kwargs={'pk': user_organization.id})
        api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {admin_token}')
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['name'] == 'User Organization'
    
    def test_get_organization_detail_as_user_for_admin_org(self, api_client, user_token, admin_organization):
        """Test user accessing an admin's organization (should fail)"""
        url = reverse('organizations:organization_detail', kwargs={'pk': admin_organization.id})
        api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {user_token}')
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_404_NOT_FOUND

# Test Organization Update
@pytest.mark.django_db
class TestUpdateOrganization:
    def test_update_organization_as_admin(self, api_client, admin_token, admin_organization):
        """Test updating an organization as an admin user"""
        url = reverse('organizations:organization_update', kwargs={'pk': admin_organization.id})
        data = {
            'name': 'Updated Admin Organization',
            'description': 'This organization was updated by an admin'
        }
        api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {admin_token}')
        response = api_client.put(url, data, format='json')
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['name'] == 'Updated Admin Organization'
        assert response.data['description'] == 'This organization was updated by an admin'
        
        # Verify the database was updated
        admin_organization.refresh_from_db()
        assert admin_organization.name == 'Updated Admin Organization'
    
    def test_update_organization_as_user(self, api_client, user_token, user_organization):
        """Test updating an organization as a regular user"""
        url = reverse('organizations:organization_update', kwargs={'pk': user_organization.id})
        data = {
            'name': 'Updated User Organization',
            'description': 'This organization was updated by a regular user'
        }
        api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {user_token}')
        response = api_client.put(url, data, format='json')
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['name'] == 'Updated User Organization'
        assert response.data['description'] == 'This organization was updated by a regular user'
        
        # Verify the database was updated
        user_organization.refresh_from_db()
        assert user_organization.name == 'Updated User Organization'
    
    def test_update_organization_as_user_for_admin_org(self, api_client, user_token, admin_organization):
        """Test user updating an admin's organization (should fail)"""
        url = reverse('organizations:organization_update', kwargs={'pk': admin_organization.id})
        data = {
            'name': 'Hacked Organization',
            'description': 'This should fail'
        }
        api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {user_token}')
        response = api_client.put(url, data, format='json')
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
        
        # Verify the database was not updated
        admin_organization.refresh_from_db()
        assert admin_organization.name == 'Admin Organization'

# Test User Management in Organizations
@pytest.mark.django_db
class TestUserManagement:
    def test_add_users_to_organization(self, api_client, admin_token, admin_organization, regular_user):
        """Test adding users to an organization"""
        url = reverse('organizations:organization_add_users', kwargs={'pk': admin_organization.id})
        data = {
            'user_ids': [regular_user.id]
        }
        api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {admin_token}')
        response = api_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_200_OK
        
        # Verify the user was added to the organization
        admin_organization.refresh_from_db()
        assert admin_organization.users.filter(id=regular_user.id).exists()
    
    def test_remove_users_from_organization(self, api_client, admin_token, admin_organization, regular_user):
        """Test removing users from an organization"""
        # First add the user to the organization
        admin_organization.users.add(regular_user)
        
        url = reverse('organizations:organization_remove_users', kwargs={'pk': admin_organization.id})
        data = {
            'user_ids': [regular_user.id]
        }
        api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {admin_token}')
        response = api_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_200_OK
        
        # Verify the user was removed from the organization
        admin_organization.refresh_from_db()
        assert not admin_organization.users.filter(id=regular_user.id).exists()
    
    def test_remove_all_users_from_organization(self, api_client, admin_token, admin_organization, admin_user):
        """Test removing all users from an organization (should fail)"""
        url = reverse('organizations:organization_remove_users', kwargs={'pk': admin_organization.id})
        data = {
            'user_ids': [admin_user.id]  # This is the only user in the organization
        }
        api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {admin_token}')
        response = api_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'Cannot remove all users' in response.data['error']
        
        # Verify the user was not removed from the organization
        admin_organization.refresh_from_db()
        assert admin_organization.users.filter(id=admin_user.id).exists()

# Test Organization Search
@pytest.mark.django_db
class TestSearchOrganizations:
    def test_search_organizations_as_admin(self, api_client, admin_token, admin_organization, user_organization):
        """Test searching organizations as an admin user"""
        url = reverse('organizations:organization_search') + '?q=Admin'
        api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {admin_token}')
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) >= 1
        assert any(org['name'] == 'Admin Organization' for org in response.data)
        
        # Admin should also be able to search for user organizations
        url = reverse('organizations:organization_search') + '?q=User'
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) >= 1
        assert any(org['name'] == 'User Organization' for org in response.data)
    
    def test_search_organizations_as_user(self, api_client, user_token, user_organization, admin_organization):
        """Test searching organizations as a regular user"""
        # User should be able to search for their own organizations
        url = reverse('organizations:organization_search') + '?q=User'
        api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {user_token}')
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) >= 1
        assert any(org['name'] == 'User Organization' for org in response.data)
        
        # User should not be able to search for admin organizations
        url = reverse('organizations:organization_search') + '?q=Admin'
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 0
    
    def test_search_organizations_without_query(self, api_client, admin_token):
        """Test searching organizations without a query (should fail)"""
        url = reverse('organizations:organization_search')
        api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {admin_token}')
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'query parameter' in response.data['error']

# Test Organization Deletion
@pytest.mark.django_db
class TestDeleteOrganization:
    def test_delete_organization_as_admin(self, api_client, admin_token, admin_organization):
        """Test deleting an organization as an admin user"""
        url = reverse('organizations:organization_delete', kwargs={'pk': admin_organization.id})
        api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {admin_token}')
        response = api_client.delete(url)
        
        assert response.status_code == status.HTTP_204_NO_CONTENT
        
        # Verify the organization was deleted
        assert not Organization.objects.filter(id=admin_organization.id).exists()
    
    def test_delete_organization_as_user(self, api_client, user_token, user_organization):
        """Test deleting an organization as a regular user"""
        url = reverse('organizations:organization_delete', kwargs={'pk': user_organization.id})
        api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {user_token}')
        response = api_client.delete(url)
        
        assert response.status_code == status.HTTP_204_NO_CONTENT
        
        # Verify the organization was deleted
        assert not Organization.objects.filter(id=user_organization.id).exists()
    
    def test_delete_organization_as_user_for_admin_org(self, api_client, user_token, admin_organization):
        """Test user deleting an admin's organization (should fail)"""
        url = reverse('organizations:organization_delete', kwargs={'pk': admin_organization.id})
        api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {user_token}')
        response = api_client.delete(url)
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
        
        # Verify the organization was not deleted
        assert Organization.objects.filter(id=admin_organization.id).exists()

# Test User-Specific Organization Endpoints
@pytest.mark.django_db
class TestUserOrganizations:
    def test_get_user_organizations_as_admin(self, api_client, admin_token, admin_organization):
        """Test getting current user's organizations as an admin"""
        url = reverse('organizations:user_organizations')
        api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {admin_token}')
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) >= 1
        assert any(org['name'] == 'Admin Organization' for org in response.data)
    
    def test_get_user_organizations_as_user(self, api_client, user_token, user_organization):
        """Test getting current user's organizations as a regular user"""
        url = reverse('organizations:user_organizations')
        api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {user_token}')
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) >= 1
        assert any(org['name'] == 'User Organization' for org in response.data)
    
    def test_get_other_user_organizations_as_admin(self, api_client, admin_token, regular_user, user_organization):
        """Test admin getting another user's organizations"""
        url = reverse('organizations:user_organizations_by_id', kwargs={'user_id': regular_user.id})
        api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {admin_token}')
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) >= 1
        assert any(org['name'] == 'User Organization' for org in response.data)
    
    def test_get_other_user_organizations_as_user(self, api_client, user_token, admin_user):
        """Test user getting another user's organizations (should fail)"""
        url = reverse('organizations:user_organizations_by_id', kwargs={'user_id': admin_user.id})
        api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {user_token}')
        response = api_client.get(url)
        
        # The view should just return the current user's organizations instead
        assert response.status_code == status.HTTP_200_OK
        assert not any(org['name'] == 'Admin Organization' for org in response.data) 