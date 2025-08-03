import requests
import json

# Test device activation endpoints
BASE_URL = "http://127.0.0.1:8000/api/v1"

def test_request_activation():
    """Test requesting an activation code"""
    print("=== Testing Request Activation Code ===")
    
    data = {
        "device_id": "TEST-DEVICE-123",
        "device_info": {
            "brand": "Samsung",
            "model": "Smart TV",
            "systemVersion": "Android 11",
            "appVersion": "1.0.0",
            "buildNumber": "1"
        }
    }
    
    try:
        response = requests.post(f"{BASE_URL}/devices/request-activation/", 
                               json=data, 
                               headers={"Content-Type": "application/json"})
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
        
        if response.status_code == 200:
            return response.json().get('activation_code')
    except Exception as e:
        print(f"Error: {e}")
    
    return None

def test_check_activation(device_id):
    """Test checking activation status"""
    print("=== Testing Check Activation Status ===")
    
    data = {"device_id": device_id}
    
    try:
        response = requests.post(f"{BASE_URL}/devices/check-activation/", 
                               json=data,
                               headers={"Content-Type": "application/json"})
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.json()
    except Exception as e:
        print(f"Error: {e}")
    return None

if __name__ == "__main__":
    # Test device activation flow
    activation_code = test_request_activation()
    
    if activation_code:
        print(f"\n✅ Device activation code: {activation_code}")
        print("You can now use this code in the web interface to activate the device!")
    
    # Test checking status (should be pending)
    status = test_check_activation("TEST-DEVICE-123")
    
    if status and not status.get('activated'):
        print(f"\n✅ Device status: {status['status']} (as expected)")
        print("Device is waiting for web activation")
    
    print("\n=== Test Complete ===")
    print("Next steps:")
    print("1. Open the web app at http://localhost:5173/displays")
    print("2. Login with your account")
    print(f"3. Enter activation code: {activation_code}")
    print("4. Give the device a name and location")
    print("5. Click 'Activate Display'")
