import requests
import concurrent.futures
import time

BASE_URL = "http://localhost:8000"
LOGIN_ENDPOINT = f"{BASE_URL}/api/auth/login/"
POST_ENDPOINT = f"{BASE_URL}/api/posts/create/"

USERNAME = "admin_test"
PASSWORD = "admin123"

# 🔹 Test Case : Post Creation Load Test
def get_token():
    res = requests.post(LOGIN_ENDPOINT, data={"login": USERNAME, "password": PASSWORD})
    if res.status_code != 200:
        raise Exception(f"Login failed: {res.text}")
    return res.json()['access']

def send_post(token):
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    payload = {"content": "Load test post", "isPublic": True}
    start = time.time()
    response = requests.post(POST_ENDPOINT, json=payload, headers=headers)
    latency = time.time() - start
    return response.status_code, latency

def run_post_creation_test(total_requests=20):
    print("\n🚀 Running Post Creation Load Test...")
    token = get_token()
    latencies = []
    failures = 0

    with concurrent.futures.ThreadPoolExecutor(max_workers=100) as executor:
        futures = [executor.submit(send_post, token) for _ in range(total_requests)]
        for future in concurrent.futures.as_completed(futures):
            status, latency = future.result()
            latencies.append(latency)
            if status != 201:
                failures += 1

    latencies.sort()
    p95 = latencies[int(0.95 * len(latencies))]
    avg = sum(latencies) / len(latencies)

    print(f"📊 Total: {total_requests}, Failures: {failures}")
    print(f"✅ 95th Percentile: {p95:.3f}s")
    print(f"✅ Avg Time: {avg:.3f}s")

# 🔹 Test Case : Login API Stress Test
def login_user(index):
    start = time.time()
    response = requests.post(LOGIN_ENDPOINT, data={
        "login": USERNAME,
        "password": PASSWORD
    })
    latency = time.time() - start
    return response.status_code, latency

def run_login_stress_test(total_logins=200):
    print("\n🔐 Running Login API Stress Test...")
    latencies = []
    failures = 0

    with concurrent.futures.ThreadPoolExecutor(max_workers=200) as executor:
        futures = [executor.submit(login_user, i) for i in range(total_logins)]
        for future in concurrent.futures.as_completed(futures):
            status, latency = future.result()
            latencies.append(latency)
            if status != 200:
                failures += 1

    latencies.sort()
    p95 = latencies[int(0.95 * len(latencies))]
    avg = sum(latencies) / len(latencies)

    print(f"📊 Total: {total_logins}, Failures: {failures}")
    print(f"✅ 95th Percentile: {p95:.3f}s")
    print(f"✅ Avg Time: {avg:.3f}s")

def get_headers():
    token = get_token()
    return {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }


# 🔹 Test Case : Send a Message in a Conversation
def send_message(conversation_id, content="This is another test message!", attachments=None, attachment_types=None):
    print(f"\n💬 Sending a message to conversation {conversation_id}")

    message_payload = {
        "content": content,
        "reply_to": None
    }

    if attachments and attachment_types:
        message_payload["attachments"] = attachments
        message_payload["attachment_types"] = attachment_types

    response = requests.post(
        f"{BASE_URL}/api/messaging/conversations/{conversation_id}/send-message/",
        headers=get_headers(),
        json=message_payload
    )

    print(f"📨 Status: {response.status_code}")
    try:
        print(f"📨 Response: {response.json()}")
    except:
        print("⚠️ Failed to parse JSON response.")

    if response.status_code == 201:
        message_id = response.json().get("id")
        print(f"✅ Message sent successfully! ID: {message_id}")
    elif response.status_code == 403:
        print("❌ Forbidden: You may have been blocked by the recipient.")
    else:
        print("❌ Message sending failed.")

# 🔹 Test Case : Upload Media Post
def upload_media_instance(instance_id):
    try:
        with open("test_image_1.jpeg", "rb") as img:
            files = {
                "media": ("test_image_1.jpeg", img, "image/jpeg")
            }
            data = {
                "content": f"Performance test post #{instance_id}",
                "ispublic": True,
            }

            response = requests.post(
                f"{BASE_URL}/api/posts/create/",
                headers={"Authorization": f"Bearer {get_token()}"},
                files=files,
                data=data
            )

            if response.status_code == 201:
                return True
            else:
                return False
    except Exception as e:
        print(f"[{instance_id}] ❌ Exception: {e}")
        return False


def upload_media_post_stress_test(concurrent_users=10):
    print(f"\n🚀 Starting media upload stress test with {concurrent_users} concurrent uploads")
    start_time = time.time()

    success_count = 0
    with concurrent.futures.ThreadPoolExecutor(max_workers=concurrent_users) as executor:
        futures = [executor.submit(upload_media_instance, i + 1) for i in range(concurrent_users)]
        for future in concurrent.futures.as_completed(futures):
            if future.result():
                success_count += 1

    duration = time.time() - start_time
    print(f"\n📊 Stress Test Completed in {duration:.2f} seconds")
    print(f"✅ Success: {success_count}/{concurrent_users}")
    print(f"❌ Failures: {concurrent_users - success_count}")

example_conversation_id = "14"  
#send_message(example_conversation_id)
run_post_creation_test(total_requests=20)
run_login_stress_test(total_logins=20)
upload_media_post_stress_test(concurrent_users=10)  