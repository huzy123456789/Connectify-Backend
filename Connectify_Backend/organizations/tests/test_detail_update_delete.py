import pytest
from django.urls import reverse
from rest_framework import status
from organizations.models import Organization

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