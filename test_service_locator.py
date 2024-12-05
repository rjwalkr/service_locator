import requests

BASE_URL = "http://127.0.0.1:4000"

def test_service_locator(service_name):
    try:
        response = requests.get(f"{BASE_URL}/service/{service_name}")
        if response.status_code == 200:
            print(f"{service_name} resolved to:", response.json())
        else:
            print(f"Error: {response.json()}")
    except Exception as e:
        print(f"Error communicating with service locator: {e}")

# Test cases
test_service_locator("auth_devs")
test_service_locator("nonexistent_service")
