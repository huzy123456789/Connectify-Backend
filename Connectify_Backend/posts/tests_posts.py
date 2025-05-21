import unittest
import requests

BASE_URL = "http://localhost:8000/api"
LOGIN_ENDPOINT = f"{BASE_URL}/auth/login/"
POST_CREATE_ENDPOINT = f"{BASE_URL}/posts/create/"

USERNAME = "admin_test"
PASSWORD = "admin123"

class PostAPITestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Login to get token
        response = requests.post(LOGIN_ENDPOINT, data={
            "login": USERNAME,
            "password": PASSWORD
        })
        assert response.status_code == 200, "Login failed"
        cls.token = response.json()['access']
        cls.headers = {
            "Authorization": f"Bearer {cls.token}"
        }

    def create_post(self):
        payload = {
            "content": "Temporary post for testing #independent",
            "organization_id": 18,
            "ispublic": True,
            "tagged_user_ids": []
        }
        response = requests.post(POST_CREATE_ENDPOINT, headers=self.headers, json=payload)
        self.assertEqual(response.status_code, 201, "Post creation failed")
        return response.json()["id"]

    def delete_post(self, post_id):
        url = f"{BASE_URL}/posts/{post_id}/delete/"
        response = requests.delete(url, headers=self.headers)
        self.assertIn(response.status_code, [200, 204], "Post deletion failed")

    def test_create_post(self):
        post_id = self.create_post()
        print(f"✅ Post created with ID: {post_id}")
        self.delete_post(post_id)

    def test_get_post_detail(self):
        post_id = self.create_post()
        url = f"{BASE_URL}/posts/{post_id}/"
        response = requests.get(url, headers=self.headers)
        self.assertEqual(response.status_code, 200, "Fetching post detail failed")
        print("📄 Post detail:", response.json())
        self.delete_post(post_id)

    def test_update_post(self):
        post_id = self.create_post()
        url = f"{BASE_URL}/posts/{post_id}/update/"
        payload = {
            "content": "Updated content for test #refactor",
            "ispublic": False
        }
        response = requests.put(url, headers=self.headers, json=payload)
        self.assertEqual(response.status_code, 200, "Post update failed")
        print("✏️ Post updated:", response.json())
        self.delete_post(post_id)

    def test_delete_post(self):
        post_id = self.create_post()
        url = f"{BASE_URL}/posts/{post_id}/delete/"
        response = requests.delete(url, headers=self.headers)
        self.assertEqual(response.status_code, 204, "Post deletion failed")
        print("🗑️ Post deleted successfully")

if __name__ == "__main__":
    unittest.main(verbosity=2)
