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
        json={"username": username, "password": password}
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
    print_header("Testing Conversation APIs")
    
    # Get all conversations
    print_subheader("Getting all conversations")
    response = requests.get(
        f"{BASE_URL}/messaging/conversations/",
        headers=get_headers()
    )
    print_response(response)
    
    # Create a new conversation
    print_subheader("Creating a new conversation")
    response = requests.post(
        f"{BASE_URL}/messaging/conversations/create/",
        headers=get_headers(),
        json={
            "participant_id": 2,  # Assuming user with ID 2 exists
            "organization_id": 1,  # Assuming organization with ID 1 exists
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
            
            # Edit the message
            print_subheader(f"Editing message {message_id}")
            response = requests.put(
                f"{BASE_URL}/messaging/messages/{message_id}/edit/",
                headers=get_headers(),
                json={
                    "content": "This is an edited message!"
                }
            )
            print_response(response)
            
            # React to the message
            print_subheader(f"Reacting to message {message_id}")
            response = requests.post(
                f"{BASE_URL}/messaging/messages/{message_id}/react/",
                headers=get_headers(),
                json={
                    "emoji": "👍"
                }
            )
            print_response(response)
            
            # Remove reaction
            print_subheader(f"Removing reaction from message {message_id}")
            response = requests.delete(
                f"{BASE_URL}/messaging/messages/{message_id}/unreact/?emoji=👍",
                headers=get_headers()
            )
            print_response(response)
            
            # Delete the message
            print_subheader(f"Deleting message {message_id}")
            response = requests.delete(
                f"{BASE_URL}/messaging/messages/{message_id}/delete/",
                headers=get_headers()
            )
            print_response(response)
    
    # Delete the conversation (soft delete)
    if 'conversation_id' in locals():
        print_subheader(f"Deleting conversation {conversation_id}")
        response = requests.delete(
            f"{BASE_URL}/messaging/conversations/{conversation_id}/delete/",
            headers=get_headers()
        )
        print_response(response)

def test_group_chat_apis():
    print_header("Testing Group Chat APIs")
    
    # Get all group chats
    print_subheader("Getting all group chats")
    response = requests.get(
        f"{BASE_URL}/messaging/group-chats/",
        headers=get_headers()
    )
    print_response(response)
    
    # Create a new group chat
    print_subheader("Creating a new group chat")
    response = requests.post(
        f"{BASE_URL}/messaging/group-chats/create/",
        headers=get_headers(),
        json={
            "name": "Test Group Chat",
            "description": "This is a test group chat",
            "organization_id": 1,  # Assuming organization with ID 1 exists
            "member_ids": [2, 3],  # Assuming users with IDs 2 and 3 exist
            "initial_message": "Welcome to the test group chat!"
        }
    )
    print_response(response)
    
    if response.status_code == 201:
        group_chat_id = response.json().get('id')
        print_success(f"Group chat created with ID: {group_chat_id}")
        
        # Get group chat details
        print_subheader(f"Getting details for group chat {group_chat_id}")
        response = requests.get(
            f"{BASE_URL}/messaging/group-chats/{group_chat_id}/",
            headers=get_headers()
        )
        print_response(response)
        
        # Get group chat messages
        print_subheader(f"Getting messages for group chat {group_chat_id}")
        response = requests.get(
            f"{BASE_URL}/messaging/group-chats/{group_chat_id}/messages/",
            headers=get_headers()
        )
        print_response(response)
        
        # Send a message
        print_subheader(f"Sending a message to group chat {group_chat_id}")
        response = requests.post(
            f"{BASE_URL}/messaging/group-chats/{group_chat_id}/send-message/",
            headers=get_headers(),
            json={
                "content": "This is a test message in the group chat!"
            }
        )
        print_response(response)
        
        # Add members
        print_subheader(f"Adding members to group chat {group_chat_id}")
        response = requests.post(
            f"{BASE_URL}/messaging/group-chats/{group_chat_id}/add-members/",
            headers=get_headers(),
            json={
                "member_ids": [4]  # Assuming user with ID 4 exists
            }
        )
        print_response(response)
        
        # Change member role
        print_subheader(f"Changing member role in group chat {group_chat_id}")
        response = requests.post(
            f"{BASE_URL}/messaging/group-chats/{group_chat_id}/change-role/",
            headers=get_headers(),
            json={
                "member_id": 2,  # Assuming user with ID 2 exists
                "role": "admin"
            }
        )
        print_response(response)
        
        # Remove member
        print_subheader(f"Removing member from group chat {group_chat_id}")
        response = requests.post(
            f"{BASE_URL}/messaging/group-chats/{group_chat_id}/remove-member/",
            headers=get_headers(),
            json={
                "member_id": 3  # Assuming user with ID 3 exists
            }
        )
        print_response(response)
        
        # Delete the group chat (soft delete)
        print_subheader(f"Deleting group chat {group_chat_id}")
        response = requests.delete(
            f"{BASE_URL}/messaging/group-chats/{group_chat_id}/delete/",
            headers=get_headers()
        )
        print_response(response)

def test_user_block_apis():
    print_header("Testing User Block APIs")
    
    # Get all blocks
    print_subheader("Getting all blocks")
    response = requests.get(
        f"{BASE_URL}/messaging/blocks/",
        headers=get_headers()
    )
    print_response(response)
    
    # Create a new block
    print_subheader("Creating a new block")
    response = requests.post(
        f"{BASE_URL}/messaging/blocks/create/",
        headers=get_headers(),
        json={
            "blocked_id": 2,  # Assuming user with ID 2 exists
            "organization_id": 1  # Assuming organization with ID 1 exists
        }
    )
    print_response(response)
    
    if response.status_code == 201:
        block_id = response.json().get('id')
        print_success(f"Block created with ID: {block_id}")
        
        # Get block details
        print_subheader(f"Getting details for block {block_id}")
        response = requests.get(
            f"{BASE_URL}/messaging/blocks/{block_id}/",
            headers=get_headers()
        )
        print_response(response)
        
        # Delete the block
        print_subheader(f"Deleting block {block_id}")
        response = requests.delete(
            f"{BASE_URL}/messaging/blocks/{block_id}/delete/",
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
    test_user_block_apis()

if __name__ == "__main__":
    main() 