#!/usr/bin/env python
import requests
import json
import sys
from pprint import pprint

# Configuration
BASE_URL = 'http://localhost:8000/api'
TOKEN = None  # Will be set after login

# Colors for terminal output
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def print_header(text):
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'=' * 50}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{text.center(50)}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'=' * 50}{Colors.ENDC}\n")

def print_subheader(text):
    print(f"\n{Colors.OKBLUE}{Colors.BOLD}{text}{Colors.ENDC}")
    print(f"{Colors.OKBLUE}{'-' * 50}{Colors.ENDC}\n")

def print_success(text):
    print(f"{Colors.OKGREEN}✓ {text}{Colors.ENDC}")

def print_error(text):
    print(f"{Colors.FAIL}✗ {text}{Colors.ENDC}")

def print_warning(text):
    print(f"{Colors.WARNING}! {text}{Colors.ENDC}")

def print_response(response):
    try:
        print(f"Status: {response.status_code}")
        if response.status_code != 204:  # No content
            pprint(response.json())
    except json.JSONDecodeError:
        print("Response is not JSON")
        print(response.text)

def login(username, password):
    global TOKEN
    print_subheader(f"Logging in as {username}")
    
    response = requests.post(
        f"{BASE_URL}/auth/login/",
        json={"login": username, "password": password}  # <-- changed 'username' to 'login'
    )
    
    if response.status_code == 200:
        TOKEN = response.json().get('access')
        print_success(f"Login successful. Token: {TOKEN[:10]}...")
        return True
    else:
        print_error("Login failed")
        print_response(response)
        return False

def get_headers():
    return {
        "Authorization": f"Bearer {TOKEN}",
        "Content-Type": "application/json"
    }

def test_conversation_apis():
    
    # Create a new conversation
    print_subheader("Creating a new conversation")
    response = requests.post(
        f"{BASE_URL}/messaging/conversations/create/",
        headers=get_headers(),
        json={
            "participant_id": 5,  
            "organization_id": 18,  
            "initial_message": "Hello, this is a test message!"
        }
    )
    print_response(response)
    
    if response.status_code == 201:
        conversation_id = response.json().get('id')
        print_success(f"Conversation created with ID: {conversation_id}")
        
        # Get conversation details
        print_subheader(f"Getting details for conversation {conversation_id}")
        response = requests.get(
            f"{BASE_URL}/messaging/conversations/{conversation_id}/",
            headers=get_headers()
        )
        print_response(response)
        
        # Get conversation messages
        print_subheader(f"Getting messages for conversation {conversation_id}")
        response = requests.get(
            f"{BASE_URL}/messaging/conversations/{conversation_id}/messages/",
            headers=get_headers()
        )
        print_response(response)
        
        # Send a message
        print_subheader(f"Sending a message to conversation {conversation_id}")
        response = requests.post(
            f"{BASE_URL}/messaging/conversations/{conversation_id}/send-message/",
            headers=get_headers(),
            json={
                "content": "This is another test message!"
            }
        )
        print_response(response)
        
        if response.status_code == 201:
            message_id = response.json().get('id')
            print_success(f"Message sent with ID: {message_id}")
            
           
def test_group_chat_apis():
    print_header("Testing Group Chat APIs")
    
    # Get all group chats
    print_subheader("Getting all group chats")
    response = requests.get(
        f"{BASE_URL}/messaging/group-chats/",
        headers=get_headers()
    )
    print_response(response)
    
        

def main():
    if len(sys.argv) < 3:
        print("Usage: python api_tests.py <username> <password>")
        sys.exit(1)
    
    username = sys.argv[1]
    password = sys.argv[2]
    
    if not login(username, password):
        sys.exit(1)
    
    test_conversation_apis()
    test_group_chat_apis()
   
if __name__ == "__main__":
    main() 