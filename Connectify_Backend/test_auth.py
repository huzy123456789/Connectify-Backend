import requests
import json

# Base URL
BASE_URL = 'http://127.0.0.1:8000/api/auth/'

def test_login_admin_with_username():
    """Test login with admin username"""
    url = BASE_URL + 'login/'
    data = {
        'login': 'admin_test',
        'password': 'admin123'
    }
    
    response = requests.post(url, data=data)
    print("Login with admin username:")
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        print(f"Response: {json.dumps(response.json(), indent=4)}")
    else:
        print(f"Error: {response.text}")
    print("\n")
    
    return response.json() if response.status_code == 200 else None

def test_login_admin_with_email():
    """Test login with admin email"""
    url = BASE_URL + 'login/'
    data = {
        'login': 'admin@example.com',
        'password': 'admin123'
    }
    
    response = requests.post(url, data=data)
    print("Login with admin email:")
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        print(f"Response: {json.dumps(response.json(), indent=4)}")
    else:
        print(f"Error: {response.text}")
    print("\n")
    
    return response.json() if response.status_code == 200 else None

def test_login_user_with_username():
    """Test login with regular user username"""
    url = BASE_URL + 'login/'
    data = {
        'login': 'user_test',
        'password': 'user123'
    }
    
    response = requests.post(url, data=data)
    print("Login with regular user username:")
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        print(f"Response: {json.dumps(response.json(), indent=4)}")
    else:
        print(f"Error: {response.text}")
    print("\n")
    
    return response.json() if response.status_code == 200 else None

def test_login_user_with_email():
    """Test login with regular user email"""
    url = BASE_URL + 'login/'
    data = {
        'login': 'user@example.com',
        'password': 'user123'
    }
    
    response = requests.post(url, data=data)
    print("Login with regular user email:")
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        print(f"Response: {json.dumps(response.json(), indent=4)}")
    else:
        print(f"Error: {response.text}")
    print("\n")
    
    return response.json() if response.status_code == 200 else None

def test_token_refresh(refresh_token):
    """Test token refresh"""
    url = BASE_URL + 'token/refresh/'
    data = {
        'refresh': refresh_token
    }
    
    response = requests.post(url, data=data)
    print("Token Refresh:")
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        print(f"Response: {json.dumps(response.json(), indent=4)}")
    else:
        print(f"Error: {response.text}")
    print("\n")
    
    return response.json() if response.status_code == 200 else None

def test_admin_only_endpoint(access_token):
    """Test admin-only endpoint"""
    url = BASE_URL + 'admin-only/'
    headers = {
        'Authorization': f'Bearer {access_token}'
    }
    
    response = requests.get(url, headers=headers)
    print("Admin-Only Endpoint:")
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        print(f"Response: {json.dumps(response.json(), indent=4)}")
    else:
        print(f"Error: {response.text}")
    print("\n")
    
    return response.json() if response.status_code == 200 else None

def test_user_only_endpoint(access_token):
    """Test user-only endpoint"""
    url = BASE_URL + 'user-only/'
    headers = {
        'Authorization': f'Bearer {access_token}'
    }
    
    response = requests.get(url, headers=headers)
    print("User-Only Endpoint:")
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        print(f"Response: {json.dumps(response.json(), indent=4)}")
    else:
        print(f"Error: {response.text}")
    print("\n")
    
    return response.json() if response.status_code == 200 else None

if __name__ == '__main__':
    print("=== Testing Admin User Authentication and Permissions ===")
    # Test login with admin username
    admin_login_response = test_login_admin_with_username()
    
    if admin_login_response and 'access' in admin_login_response:
        # Test admin-only endpoint with admin token
        test_admin_only_endpoint(admin_login_response['access'])
        
        # Test user-only endpoint with admin token (should fail)
        test_user_only_endpoint(admin_login_response['access'])
    
    print("=== Testing Regular User Authentication and Permissions ===")
    # Test login with regular user username
    user_login_response = test_login_user_with_username()
    
    if user_login_response and 'access' in user_login_response:
        # Test admin-only endpoint with user token (should fail)
        test_admin_only_endpoint(user_login_response['access'])
        
        # Test user-only endpoint with user token
        test_user_only_endpoint(user_login_response['access']) 