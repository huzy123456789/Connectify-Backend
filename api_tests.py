import requests
import json
import os
from datetime import datetime

# Base URL for the API
BASE_URL = "http://localhost:8000/api"

# Test user credentials
ADMIN_CREDENTIALS = {
    "login": "admin_test",
    "password": "admin123"
}

USER_CREDENTIALS = {
    "login": "user_test",
    "password": "user123"
}

class APITester:
    def __init__(self):
        self.admin_token = None
        self.user_token = None
        self.test_post_id = None
        self.test_comment_id = None
        self.test_reaction_type_id = None

    def login(self, credentials):
        """Login and get access token"""
        response = requests.post(
            f"{BASE_URL}/auth/login/",
            json=credentials
        )
        if response.status_code == 200:
            return response.json()["access"]
        else:
            print(f"Login failed: {response.text}")
            return None

    def setup(self):
        """Initial setup - login and get tokens"""
        print("\n=== Setting up test environment ===")
        self.admin_token = self.login(ADMIN_CREDENTIALS)
        self.user_token = self.login(USER_CREDENTIALS)
        
        if not self.admin_token or not self.user_token:
            raise Exception("Failed to get authentication tokens")
        
        print("✓ Authentication successful")

    def get_auth_headers(self, token):
        """Get headers with authentication token only"""
        return {
            "Authorization": f"Bearer {token}"
        }

    def get_json_headers(self, token):
        """Get headers with authentication token and JSON content type"""
        return {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }

    def test_post_apis(self):
        """Test post-related APIs"""
        print("\n=== Testing Post APIs ===")

        # Test post with image
        post_data = {
            "content": f"Test post with image and #testing hashtag {datetime.now().timestamp()}",
            "ispublic": True
        }
        
        # For multipart form data with image
        files = None
        if os.path.exists('test_image.jpg'):
            files = {
                'media': ('test_image.jpg', open('test_image.jpg', 'rb'), 'image/jpeg')
            }
            response = requests.post(
                f"{BASE_URL}/posts/create/",
                headers=self.get_auth_headers(self.user_token),  # No Content-Type header
                data=post_data,  # Use data instead of json
                files=files
            )
            assert response.status_code == 201, f"Create post with image failed: {response.text}"
            self.test_post_id = response.json()["id"]
            print("✓ Create post with image")

        # Test post with video
        post_data_video = {
            "content": f"Test post with video and #testing hashtag {datetime.now().timestamp()}",
            "ispublic": True
        }
        
        # For multipart form data with video
        if os.path.exists('test_video.mp4'):
            files = {
                'media': ('test_video.mp4', open('test_video.mp4', 'rb'), 'video/mp4')
            }
            response = requests.post(
                f"{BASE_URL}/posts/create/",
                headers=self.get_auth_headers(self.user_token),  # No Content-Type header
                data=post_data_video,  # Use data instead of json
                files=files
            )
            assert response.status_code == 201, f"Create post with video failed: {response.text}"
            if not self.test_post_id:  # If no image post was created, use this as test post
                self.test_post_id = response.json()["id"]
            print("✓ Create post with video")

        # If no media files were available, create a text-only post
        if not self.test_post_id:
            response = requests.post(
                f"{BASE_URL}/posts/create/",
                headers=self.get_json_headers(self.user_token),  # Use JSON headers for text-only post
                json=post_data
            )
            assert response.status_code == 201, f"Create text post failed: {response.text}"
            self.test_post_id = response.json()["id"]
            print("✓ Create text-only post")

        # Get post detail
        response = requests.get(
            f"{BASE_URL}/posts/{self.test_post_id}/",
            headers=self.get_auth_headers(self.user_token)
        )
        assert response.status_code == 200, f"Get post detail failed: {response.text}"
        print("✓ Get post detail")

        # Get feed
        response = requests.get(
            f"{BASE_URL}/posts/feed/",
            headers=self.get_auth_headers(self.user_token)
        )
        assert response.status_code == 200, f"Get feed failed: {response.text}"
        print("✓ Get feed")

        # Create comment
        comment_data = {
            "content": f"Test comment {datetime.now().timestamp()}"
        }
        response = requests.post(
            f"{BASE_URL}/posts/{self.test_post_id}/comments/create/",
            headers=self.get_json_headers(self.user_token),
            json=comment_data
        )
        assert response.status_code == 201, f"Create comment failed: {response.text}"
        self.test_comment_id = response.json()["id"]
        print("✓ Create comment")

        # Get post comments
        response = requests.get(
            f"{BASE_URL}/posts/{self.test_post_id}/comments/",
            headers=self.get_auth_headers(self.user_token)
        )
        assert response.status_code == 200, f"Get post comments failed: {response.text}"
        print("✓ Get post comments")

        # Get reaction types
        response = requests.get(
            f"{BASE_URL}/posts/reaction-types/",
            headers=self.get_auth_headers(self.user_token)
        )
        assert response.status_code == 200, f"Get reaction types failed: {response.text}"
        reaction_types = response.json()
        if reaction_types:
            self.test_reaction_type_id = reaction_types[0]["id"]
            print("✓ Get reaction types")

            # React to post
            response = requests.post(
                f"{BASE_URL}/posts/{self.test_post_id}/react/",
                headers=self.get_json_headers(self.user_token),
                json={"reaction_type_id": self.test_reaction_type_id}
            )
            assert response.status_code == 200, f"React to post failed: {response.text}"
            print("✓ React to post")

            # Remove post reaction
            response = requests.delete(
                f"{BASE_URL}/posts/{self.test_post_id}/unreact/",
                headers=self.get_auth_headers(self.user_token)
            )
            assert response.status_code == 200, f"Remove post reaction failed: {response.text}"
            print("✓ Remove post reaction")

            # React to comment
            response = requests.post(
                f"{BASE_URL}/posts/comments/{self.test_comment_id}/react/",
                headers=self.get_json_headers(self.user_token),
                json={"reaction_type_id": self.test_reaction_type_id}
            )
            assert response.status_code == 200, f"React to comment failed: {response.text}"
            print("✓ React to comment")

            # Remove comment reaction
            response = requests.delete(
                f"{BASE_URL}/posts/comments/{self.test_comment_id}/unreact/",
                headers=self.get_auth_headers(self.user_token)
            )
            assert response.status_code == 200, f"Remove comment reaction failed: {response.text}"
            print("✓ Remove comment reaction")

        # Share post
        share_data = {
            "additional_content": f"Sharing this post! {datetime.now().timestamp()}"
        }
        response = requests.post(
            f"{BASE_URL}/posts/{self.test_post_id}/share/",
            headers=self.get_json_headers(self.user_token),
            json=share_data
        )
        assert response.status_code == 201, f"Share post failed: {response.text}"
        print("✓ Share post")

        # Search posts
        response = requests.get(
            f"{BASE_URL}/posts/search/?q=test",
            headers=self.get_auth_headers(self.user_token)
        )
        assert response.status_code == 200, f"Search posts failed: {response.text}"
        print("✓ Search posts")

        # Get trending hashtags
        response = requests.get(
            f"{BASE_URL}/posts/trending-hashtags/",
            headers=self.get_auth_headers(self.user_token)
        )
        assert response.status_code == 200, f"Get trending hashtags failed: {response.text}"
        print("✓ Get trending hashtags")

        # Update post
        update_data = {
            "content": f"Updated post content {datetime.now().timestamp()}",
            "ispublic": False
        }
        response = requests.put(
            f"{BASE_URL}/posts/{self.test_post_id}/update/",
            headers=self.get_json_headers(self.user_token),
            json=update_data
        )
        assert response.status_code == 200, f"Update post failed: {response.text}"
        print("✓ Update post")

        # Update comment
        update_comment_data = {
            "content": f"Updated comment content {datetime.now().timestamp()}"
        }
        response = requests.put(
            f"{BASE_URL}/posts/comments/{self.test_comment_id}/update/",
            headers=self.get_json_headers(self.user_token),
            json=update_comment_data
        )
        assert response.status_code == 200, f"Update comment failed: {response.text}"
        print("✓ Update comment")

        # Delete comment
        response = requests.delete(
            f"{BASE_URL}/posts/comments/{self.test_comment_id}/delete/",
            headers=self.get_auth_headers(self.user_token)
        )
        assert response.status_code == 204, f"Delete comment failed: {response.text}"
        print("✓ Delete comment")

        # Delete post
        response = requests.delete(
            f"{BASE_URL}/posts/{self.test_post_id}/delete/",
            headers=self.get_auth_headers(self.user_token)
        )
        assert response.status_code == 204, f"Delete post failed: {response.text}"
        print("✓ Delete post")

    def run_all_tests(self):
        """Run all API tests"""
        try:
            self.setup()
            self.test_post_apis()
            print("\n=== All tests completed successfully! ===")
        except AssertionError as e:
            print(f"\n❌ Test failed: {str(e)}")
        except Exception as e:
            print(f"\n❌ Unexpected error: {str(e)}")
        finally:
            print("\nTest run completed.")


if __name__ == "__main__":
    tester = APITester()
    tester.run_all_tests() 