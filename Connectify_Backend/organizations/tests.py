from rest_framework.test import APITestCase
from rest_framework import status
from .models import Organization
from accounts.models import User

class OrganizationUsersViewTest(APITestCase):
    def setUp(self):
        self.admin_user = User.objects.create_user(username="admin", email="admin@example.com", password="admin123", role=User.Role.ADMIN)
        self.regular_user = User.objects.create_user(username="user", email="user@example.com", password="user123", role=User.Role.USER)
        self.organization = Organization.objects.create(name="Test Organization", description="Test Description")
        self.organization.admins.add(self.admin_user)
        self.organization.users.add(self.admin_user, self.regular_user)

    def test_get_organization_users_as_admin(self):
        self.client.login(username="admin", password="admin123")
        response = self.client.get(f"/api/organizations/{self.organization.id}/users/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_get_organization_users_as_regular_user(self):
        self.client.login(username="user", password="user123")
        response = self.client.get(f"/api/organizations/{self.organization.id}/users/")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_get_organization_users_not_found(self):
        self.client.login(username="admin", password="admin123")
        response = self.client.get("/api/organizations/999/users/")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
