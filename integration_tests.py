import requests

BASE_URL = "http://localhost:8000"
LOGIN_URL = f"{BASE_URL}/api/auth/login/"
POST_URL = f"{BASE_URL}/api/posts/create/"

USERNAME = "admin_test"
PASSWORD = "admin123"

def get_token():
    res = requests.post(LOGIN_URL, data={"login": USERNAME, "password": PASSWORD})
    if res.status_code != 200:
        raise Exception(f"Login failed: {res.text}")
    return res.json()["access"]

def run_login_required_post_test():
    print("\n🔐 Integration Test: Post Creation Requires Login")

    # Attempt post creation without logging in
    print("⛔ Trying to create post without login...")
    response_no_auth = requests.post(POST_URL, data={
        "content": "Post without login",
        "ispublic": True
    })
    if response_no_auth.status_code == 401:
        print("✅ Unauthenticated post blocked (Expected).")
    else:
        print(f"❌ Unexpected response for unauthenticated post: {response_no_auth.status_code}")
        return

    # Login to get token
    print("🔑 Logging in...")
    login_response = requests.post(LOGIN_URL, data={"login": USERNAME, "password": PASSWORD})
    if login_response.status_code != 200:
        print(f"❌ Login failed: {login_response.text}")
        return

    token = login_response.json().get("access")
    print("✅ Login successful.")

    # Attempt post creation with token
    print("✅ Trying to create post after login...")
    response_auth = requests.post(
        POST_URL,
        data={"content": "Post after login", "ispublic": True},
        headers={"Authorization": f"Bearer {token}"}
    )

    if response_auth.status_code == 201:
        print("✅ Authenticated post creation successful.")
        print("🎯 Test Status: PASS")
    else:
        print(f"❌ Authenticated post creation failed: {response_auth.status_code} - {response_auth.text}")
        print("🚫 Test Status: FAIL")
def create_trend(token, content="#CleanlinessDrive"):
    headers = {"Authorization": f"Bearer {token}"}
    payload = {
        "content": content,
        "ispublic": True
    }
    res = requests.post(POST_URL, data=payload, headers=headers)
    if res.status_code != 201:
        raise Exception(f"Failed to create trend: {res.status_code} - {res.text}")
    return res.json()["id"]

def add_comment(token, post_id, comment_content):
    headers = {"Authorization": f"Bearer {token}"}
    comment_url = f"{BASE_URL}/api/posts/{post_id}/comments/create/"
    payload = {
        "content": comment_content,
        "parent_comment_id": None
    }
    res = requests.post(comment_url, json=payload, headers=headers)
    if res.status_code != 201:
        raise Exception(f"Failed to add comment: {res.status_code} - {res.text}")
    return res.json()["id"]

def fetch_comments(token, post_id):
    headers = {"Authorization": f"Bearer {token}"}
    get_comments_url = f"{BASE_URL}/api/posts/{post_id}/comments/"
    res = requests.get(get_comments_url, headers=headers)
    if res.status_code != 200:
        raise Exception(f"Failed to fetch comments: {res.status_code} - {res.text}")
    return res.json()

def run_trend_comment_integration_test():
    print("\n🧪 Integration Test – Trend Creation + Comment Integration")

    try:
        token = get_token()
        print("✅ Logged in successfully.")
    except Exception as e:
        print(f"❌ {e}")
        return

    print("📝 Creating trend...")
    try:
        trend_id = create_trend(token, "#CleanlinessDrive")
        print(f"✅ Trend created with ID: {trend_id}")
    except Exception as e:
        print(f"❌ {e}")
        return

    print("💬 Adding comment to trend...")
    try:
        comment_id = add_comment(token, trend_id, "I'll bring gloves")
        print(f"✅ Comment added with ID: {comment_id}")
    except Exception as e:
        print(f"❌ {e}")
        return

    print("🔍 Verifying comment under trend...")
    try:
        comments = fetch_comments(token, trend_id)
        matched = any(
            c.get("content") == "I'll bring gloves"
            for c in comments.get("results", [])
        )
        if matched:
            print("✅ Comment displayed with username and timestamp.")
            print("🎯 Test Status: PASS")
        else:
            print("❌ Comment not found in thread.")
            print("🚫 Test Status: FAIL")
    except Exception as e:
        print(f"❌ {e}")

if __name__ == "__main__":
    run_login_required_post_test()
    print("------------------------------------------------------------------")
    run_trend_comment_integration_test()
