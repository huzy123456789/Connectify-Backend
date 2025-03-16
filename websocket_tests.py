#!/usr/bin/env python
import asyncio
import json
import sys
import websockets
import requests
import signal
import time
from datetime import datetime

# Configuration
BASE_URL = 'http://localhost:8000/api'
WS_BASE_URL = 'ws://localhost:8000/ws/messaging'
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

def print_message(text, sender=None):
    if sender:
        print(f"{Colors.BOLD}{sender}:{Colors.ENDC} {text}")
    else:
        print(text)

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
        print(response.text)
        return False

def get_headers():
    return {
        "Authorization": f"Bearer {TOKEN}",
        "Content-Type": "application/json"
    }

def create_conversation(participant_id, organization_id):
    print_subheader("Creating a new conversation for WebSocket testing")
    
    response = requests.post(
        f"{BASE_URL}/messaging/conversations/create/",
        headers=get_headers(),
        json={
            "participant_id": participant_id,
            "organization_id": organization_id,
            "initial_message": f"Hello, this is a WebSocket test! {datetime.now()}"
        }
    )
    
    if response.status_code == 201:
        conversation_id = response.json().get('id')
        print_success(f"Conversation created with ID: {conversation_id}")
        return conversation_id
    else:
        print_error("Failed to create conversation")
        print(response.text)
        return None

def create_group_chat(organization_id, member_ids):
    print_subheader("Creating a new group chat for WebSocket testing")
    
    response = requests.post(
        f"{BASE_URL}/messaging/group-chats/create/",
        headers=get_headers(),
        json={
            "name": f"WebSocket Test Group {datetime.now()}",
            "description": "This is a test group chat for WebSocket testing",
            "organization_id": organization_id,
            "member_ids": member_ids,
            "initial_message": f"Welcome to the WebSocket test group! {datetime.now()}"
        }
    )
    
    if response.status_code == 201:
        group_chat_id = response.json().get('id')
        print_success(f"Group chat created with ID: {group_chat_id}")
        return group_chat_id
    else:
        print_error("Failed to create group chat")
        print(response.text)
        return None

async def conversation_websocket_test(conversation_id):
    print_header(f"Testing WebSocket for Conversation {conversation_id}")
    
    uri = f"{WS_BASE_URL}/conversations/{conversation_id}/?token={TOKEN}"
    
    try:
        async with websockets.connect(uri) as websocket:
            print_success("WebSocket connection established")
            
            # Set up a task to receive messages
            receive_task = asyncio.create_task(receive_messages(websocket, "Conversation"))
            
            # Send a message
            await send_message(websocket, "Hello, this is a WebSocket test message!")
            
            # Send typing indicator
            await send_typing_indicator(websocket, True)
            await asyncio.sleep(1)
            await send_typing_indicator(websocket, False)
            
            # Wait for a few seconds to receive any responses
            await asyncio.sleep(5)
            
            # Cancel the receive task
            receive_task.cancel()
            try:
                await receive_task
            except asyncio.CancelledError:
                pass
            
            print_success("Conversation WebSocket test completed")
    except Exception as e:
        print_error(f"WebSocket error: {str(e)}")

async def group_chat_websocket_test(group_chat_id):
    print_header(f"Testing WebSocket for Group Chat {group_chat_id}")
    
    uri = f"{WS_BASE_URL}/group-chats/{group_chat_id}/?token={TOKEN}"
    
    try:
        async with websockets.connect(uri) as websocket:
            print_success("WebSocket connection established")
            
            # Set up a task to receive messages
            receive_task = asyncio.create_task(receive_messages(websocket, "Group Chat"))
            
            # Send a message
            await send_message(websocket, "Hello everyone, this is a WebSocket test message in the group!")
            
            # Send typing indicator
            await send_typing_indicator(websocket, True)
            await asyncio.sleep(1)
            await send_typing_indicator(websocket, False)
            
            # Wait for a few seconds to receive any responses
            await asyncio.sleep(5)
            
            # Cancel the receive task
            receive_task.cancel()
            try:
                await receive_task
            except asyncio.CancelledError:
                pass
            
            print_success("Group Chat WebSocket test completed")
    except Exception as e:
        print_error(f"WebSocket error: {str(e)}")

async def send_message(websocket, content, reply_to=None):
    message = {
        "type": "message",
        "content": content,
        "reply_to": reply_to
    }
    
    print_subheader(f"Sending message: {content}")
    await websocket.send(json.dumps(message))
    print_success("Message sent")

async def send_typing_indicator(websocket, is_typing):
    message = {
        "type": "typing",
        "is_typing": is_typing
    }
    
    status = "started" if is_typing else "stopped"
    print_subheader(f"Sending typing indicator: {status} typing")
    await websocket.send(json.dumps(message))
    print_success(f"Typing indicator sent: {status} typing")

async def send_read_receipt(websocket, message_id):
    message = {
        "type": "read",
        "message_id": message_id
    }
    
    print_subheader(f"Sending read receipt for message: {message_id}")
    await websocket.send(json.dumps(message))
    print_success("Read receipt sent")

async def receive_messages(websocket, source):
    try:
        while True:
            message = await websocket.recv()
            data = json.loads(message)
            
            print_subheader(f"Received {data.get('type')} from {source}")
            print(json.dumps(data, indent=2))
            
            if data.get('type') == 'message':
                # Send read receipt for the message
                message_data = data.get('message', {})
                if message_data.get('id'):
                    await send_read_receipt(websocket, message_data.get('id'))
    except asyncio.CancelledError:
        raise
    except Exception as e:
        print_error(f"Error receiving messages: {str(e)}")

async def run_tests(participant_id, organization_id, member_ids):
    # Create a conversation and group chat for testing
    conversation_id = create_conversation(participant_id, organization_id)
    group_chat_id = create_group_chat(organization_id, member_ids)
    
    if conversation_id:
        await conversation_websocket_test(conversation_id)
    
    if group_chat_id:
        await group_chat_websocket_test(group_chat_id)

def signal_handler(sig, frame):
    print_warning("\nTest interrupted. Exiting...")
    sys.exit(0)

async def main():
    if len(sys.argv) < 5:
        print("Usage: python websocket_tests.py <username> <password> <participant_id> <organization_id> [member_id1 member_id2 ...]")
        sys.exit(1)
    
    username = sys.argv[1]
    password = sys.argv[2]
    participant_id = int(sys.argv[3])
    organization_id = int(sys.argv[4])
    member_ids = [int(id) for id in sys.argv[5:]] if len(sys.argv) > 5 else []
    
    # Add participant_id to member_ids if not already included
    if participant_id not in member_ids:
        member_ids.append(participant_id)
    
    if not login(username, password):
        sys.exit(1)
    
    await run_tests(participant_id, organization_id, member_ids)

if __name__ == "__main__":
    # Set up signal handler for graceful exit
    signal.signal(signal.SIGINT, signal_handler)
    
    # Run the async main function
    asyncio.run(main()) 