import requests
import json
import time

# Base URL
BASE_URL = 'http://127.0.0.1:8000/api/'

def print_separator():
    print("=" * 80)
    print()

def get_auth_token(username, password):
    """Get authentication token"""
    print(f"Authenticating as {username}...")
    url = BASE_URL + 'auth/login/'
    data = {
        'login': username,
        'password': password
    }
    
    response = requests.post(url, data=data)
    if response.status_code == 200:
        print(f"Authentication successful for {username}")
        return response.json()
    else:
        print(f"Authentication failed: {response.text}")
        return None

def test_create_organization(token, name="Test Organization", description="This is a test organization created via API"):
    """Test creating an organization"""
    print("TESTING: Create Organization")
    url = BASE_URL + 'organizations/create/'
    headers = {
        'Authorization': f'Bearer {token}'
    }
    data = {
        'name': name,
        'description': description
    }
    
    response = requests.post(url, headers=headers, json=data)
    print(f"Status Code: {response.status_code}")
    if response.status_code in [200, 201]:
        print(f"Response: {json.dumps(response.json(), indent=4)}")
    else:
        print(f"Error: {response.text}")
    print_separator()
    
    return response.json() if response.status_code in [200, 201] else None

def test_get_organizations(token):
    """Test getting user's organizations"""
    print("TESTING: Get User's Organizations")
    url = BASE_URL + 'organizations/'
    headers = {
        'Authorization': f'Bearer {token}'
    }
    
    response = requests.get(url, headers=headers)
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        print(f"Response: {json.dumps(response.json(), indent=4)}")
    else:
        print(f"Error: {response.text}")
    print_separator()
    
    return response.json() if response.status_code == 200 else None

def test_get_all_organizations(token):
    """Test getting all organizations (admin only)"""
    print("TESTING: Get All Organizations (Admin Only)")
    url = BASE_URL + 'organizations/all/'
    headers = {
        'Authorization': f'Bearer {token}'
    }
    
    response = requests.get(url, headers=headers)
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        print(f"Response: {json.dumps(response.json(), indent=4)}")
    else:
        print(f"Error: {response.text}")
    print_separator()
    
    return response.json() if response.status_code == 200 else None

def test_get_organization_detail(token, org_id):
    """Test getting organization details"""
    print(f"TESTING: Get Organization Detail (ID: {org_id})")
    url = BASE_URL + f'organizations/{org_id}/'
    headers = {
        'Authorization': f'Bearer {token}'
    }
    
    response = requests.get(url, headers=headers)
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        print(f"Response: {json.dumps(response.json(), indent=4)}")
    else:
        print(f"Error: {response.text}")
    print_separator()
    
    return response.json() if response.status_code == 200 else None

def test_update_organization(token, org_id, name="Updated Organization Name", description="This organization was updated via API"):
    """Test updating an organization"""
    print(f"TESTING: Update Organization (ID: {org_id})")
    url = BASE_URL + f'organizations/{org_id}/update/'
    headers = {
        'Authorization': f'Bearer {token}'
    }
    data = {
        'name': name,
        'description': description
    }
    
    response = requests.put(url, headers=headers, json=data)
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        print(f"Response: {json.dumps(response.json(), indent=4)}")
    else:
        print(f"Error: {response.text}")
    print_separator()
    
    return response.json() if response.status_code == 200 else None

def test_add_users_to_organization(token, org_id, user_ids):
    """Test adding users to an organization"""
    print(f"TESTING: Add Users to Organization (ID: {org_id}, Users: {user_ids})")
    url = BASE_URL + f'organizations/{org_id}/add-users/'
    headers = {
        'Authorization': f'Bearer {token}'
    }
    data = {
        'user_ids': user_ids
    }
    
    response = requests.post(url, headers=headers, json=data)
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        print(f"Response: {json.dumps(response.json(), indent=4)}")
    else:
        print(f"Error: {response.text}")
    print_separator()
    
    return response.json() if response.status_code == 200 else None

def test_remove_users_from_organization(token, org_id, user_ids):
    """Test removing users from an organization"""
    print(f"TESTING: Remove Users from Organization (ID: {org_id}, Users: {user_ids})")
    url = BASE_URL + f'organizations/{org_id}/remove-users/'
    headers = {
        'Authorization': f'Bearer {token}'
    }
    data = {
        'user_ids': user_ids
    }
    
    response = requests.post(url, headers=headers, json=data)
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        print(f"Response: {json.dumps(response.json(), indent=4)}")
    else:
        print(f"Error: {response.text}")
    print_separator()
    
    return response.json() if response.status_code == 200 else None

def test_search_organizations(token, query):
    """Test searching organizations"""
    print(f"TESTING: Search Organizations (Query: '{query}')")
    url = BASE_URL + f'organizations/search/?q={query}'
    headers = {
        'Authorization': f'Bearer {token}'
    }
    
    response = requests.get(url, headers=headers)
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        print(f"Response: {json.dumps(response.json(), indent=4)}")
    else:
        print(f"Error: {response.text}")
    print_separator()
    
    return response.json() if response.status_code == 200 else None

def test_get_user_organizations(token, user_id=None):
    """Test getting user's organizations"""
    if user_id:
        print(f"TESTING: Get Organizations for User (ID: {user_id})")
        url = BASE_URL + f'organizations/user/{user_id}/'
    else:
        print("TESTING: Get Current User's Organizations")
        url = BASE_URL + 'organizations/user/'
    
    headers = {
        'Authorization': f'Bearer {token}'
    }
    
    response = requests.get(url, headers=headers)
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        print(f"Response: {json.dumps(response.json(), indent=4)}")
    else:
        print(f"Error: {response.text}")
    print_separator()
    
    return response.json() if response.status_code == 200 else None

def test_delete_organization(token, org_id):
    """Test deleting an organization"""
    print(f"TESTING: Delete Organization (ID: {org_id})")
    url = BASE_URL + f'organizations/{org_id}/delete/'
    headers = {
        'Authorization': f'Bearer {token}'
    }
    
    response = requests.delete(url, headers=headers)
    print(f"Status Code: {response.status_code}")
    if response.status_code != 204:
        print(f"Error: {response.text}")
    else:
        print("Organization deleted successfully")
    print_separator()
    
    return True if response.status_code == 204 else False

def test_access_control(admin_token, user_token, org_id):
    """Test access control for different user roles"""
    print("TESTING: Access Control - Admin accessing user's organization")
    # Admin should be able to access any organization
    test_get_organization_detail(admin_token, org_id)
    
    print("TESTING: Access Control - User accessing admin's organization")
    # Create an admin-only organization
    admin_org = test_create_organization(admin_token, "Admin-Only Org", "This org should only be accessible to admins")
    if admin_org and 'id' in admin_org:
        # User should not be able to access this organization
        test_get_organization_detail(user_token, admin_org['id'])
        # Clean up
        test_delete_organization(admin_token, admin_org['id'])

def run_all_tests():
    """Run all tests for the Organization APIs"""
    print("STARTING ORGANIZATION API TESTS")
    print("===============================")
    print()
    
    # Get authentication tokens
    admin_auth = get_auth_token('admin_test', 'admin123')
    user_auth = get_auth_token('user_test', 'user123')
    
    if not admin_auth or not user_auth:
        print("Authentication failed. Cannot proceed with tests.")
        return
    
    admin_token = admin_auth['access']
    user_token = user_auth['access']
    
    # Test with admin user
    print("\n\n")
    print("ADMIN USER TESTS")
    print("===============")
    print()
    
    # Test creating an organization
    admin_org = test_create_organization(admin_token)
    
    if admin_org and 'id' in admin_org:
        admin_org_id = admin_org['id']
        
        # Test getting organization details
        test_get_organization_detail(admin_token, admin_org_id)
        
        # Test updating organization
        test_update_organization(admin_token, admin_org_id)
        
        # Test getting all organizations (admin only)
        test_get_all_organizations(admin_token)
        
        # Test getting user's organizations
        test_get_organizations(admin_token)
        
        # Test getting current user's organizations
        test_get_user_organizations(admin_token)
        
        # Test getting another user's organizations (admin only)
        test_get_user_organizations(admin_token, 3)  # Assuming user_id 3 is the regular user
        
        # Test adding regular user to organization
        test_add_users_to_organization(admin_token, admin_org_id, [3])  # Assuming user_id 3 is the regular user
        
        # Test searching organizations
        test_search_organizations(admin_token, 'Updated')
        
        # Test removing users from organization
        test_remove_users_from_organization(admin_token, admin_org_id, [3])
        
        # Don't delete the organization yet, we'll use it for access control tests
    
    # Test with regular user
    print("\n\n")
    print("REGULAR USER TESTS")
    print("=================")
    print()
    
    # Test creating an organization
    user_org = test_create_organization(user_token, "User's Organization", "This is a user-created organization")
    
    if user_org and 'id' in user_org:
        user_org_id = user_org['id']
        
        # Test getting organization details
        test_get_organization_detail(user_token, user_org_id)
        
        # Test updating organization
        test_update_organization(user_token, user_org_id)
        
        # Test getting all organizations (should fail for regular user)
        test_get_all_organizations(user_token)
        
        # Test getting user's organizations
        test_get_organizations(user_token)
        
        # Test getting current user's organizations
        test_get_user_organizations(user_token)
        
        # Test getting another user's organizations (should fail for regular user)
        test_get_user_organizations(user_token, 2)  # Assuming user_id 2 is the admin user
        
        # Test searching organizations
        test_search_organizations(user_token, 'User')
        
        # Don't delete the organization yet, we'll use it for access control tests
    
    # Test access control
    print("\n\n")
    print("ACCESS CONTROL TESTS")
    print("===================")
    print()
    
    if admin_org and 'id' in admin_org and user_org and 'id' in user_org:
        test_access_control(admin_token, user_token, user_org_id)
    
    # Clean up
    print("\n\n")
    print("CLEANUP")
    print("=======")
    print()
    
    if admin_org and 'id' in admin_org:
        test_delete_organization(admin_token, admin_org_id)
    
    if user_org and 'id' in user_org:
        test_delete_organization(user_token, user_org_id)
    
    print("ORGANIZATION API TESTS COMPLETED")

if __name__ == '__main__':
    run_all_tests() 