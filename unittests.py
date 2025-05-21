import unittest
import requests
import json

BASE_URL = 'http://localhost:8000/api'
LOGIN_ENDPOINT = f"{BASE_URL}/auth/login/"
POST_CREATE_ENDPOINT = f"{BASE_URL}/posts/create/"

# Replace with valid credentials
USERNAME = "admin_test"
PASSWORD = "admin123"

class APITestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Authenticate once before all tests and store the token."""
        response = requests.post(LOGIN_ENDPOINT, data={
            "login": USERNAME,
            "password": PASSWORD
        })
        print("🔐 Login Status Code:", response.status_code)
       
        assert response.status_code == 200, "❌ Login failed"
        cls.token = response.json().get('access')

        cls.headers = {
            "Authorization": f"Bearer {cls.token}",
            "Content-Type": "application/json"
        }
    def test_00_user_login(self):
        """UT4: User Login Logic - check if login returns tokens"""
        response = requests.post(LOGIN_ENDPOINT, data={
            "login": USERNAME,
            "password": PASSWORD
        })
        self.assertEqual(response.status_code, 200, "Login failed")

        data = response.json()
        self.assertIn("access", data, "Access token missing in login response")
        self.assertIn("refresh", data, "Refresh token missing in login response")
        self.assertTrue(data.get("access"), "Access token is empty")
        self.assertTrue(data.get("refresh"), "Refresh token is empty")
        print("✅ Login test passed - tokens returned successfully.")

    def test_01_post_creation(self):
        """UT1: Create a post (posts:create)"""
        payload = {
            "content": "Welcome to Connectify!",
            "ispublic": True,
        }
        response = requests.post(POST_CREATE_ENDPOINT, headers=self.headers, data=json.dumps(payload))
        
        if response.status_code != 201:
            print(f"❌ Post creation failed with status code {response.status_code}")
            try:
                error_data = response.json()
                print("Response JSON:", error_data)
            except Exception:
                print("Response content:", response.text)
        
        self.assertEqual(response.status_code, 201, "❌ Post creation failed")
        data = response.json()

        self.assertIn("id", data, "❌ Response missing 'id'")
        self.assertEqual(data["content"], payload["content"])
        self.assertEqual(data["ispublic"], payload["ispublic"])
        print(f"✅ Post created successfully with ID: {data['id']}")
    
    def test_02_send_message_in_existing_conversation(self):
        """UT2: Send message in an existing conversation"""

        conversation_id = 19  # Make sure this conversation exists and the user is a participant
        send_message_url = f"{BASE_URL}/messaging/conversations/{conversation_id}/send-message/"

        payload = {
            "content": "Hello, how are you?",
            "reply_to": None ,
            "attachments": [],
            "attachment_types": []
        }

        print(f"\n[TEST] Sending message to conversation ID {conversation_id}...")

        response = requests.post(
            url=send_message_url,
            headers=self.headers,
            data=json.dumps(payload)
        )

        if response.status_code != 201:
            print(f"❌ Message sending failed with status code {response.status_code}")
            try:
                print("Response JSON:", response.json())
            except Exception:
                print("Response content:", response.text)
            self.fail("❌ Failed to send message")

        data = response.json()
        self.assertIn("id", data, "❌ Response missing 'id'")
        self.assertEqual(data["content"], payload["content"], "❌ Message content mismatch")
        print(f"✅ Message sent successfully. Message ID: {data['id']}")

if __name__ == '__main__':
    unittest.main(verbosity=2)
