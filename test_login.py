import urllib.request
import json

def test_login():
    print("🔍 Testing backend login for carol@example.com...")
    
    login_data = {
        'email': 'carol@example.com',
        'password': 'TestPass123'
    }
    
    url = 'http://127.0.0.1:8000/api/v1/login/'
    headers = {'Content-Type': 'application/json'}
    data = json.dumps(login_data).encode('utf-8')
    
    req = urllib.request.Request(url, data=data, headers=headers, method='POST')
    
    try:
        with urllib.request.urlopen(req) as response:
            result = json.loads(response.read().decode())
            print("🎉 LOGIN SUCCESSFUL!")
            print("✅ Status Code:", response.getcode())
            access_token = result.get('access', 'N/A')
            refresh_token = result.get('refresh', 'N/A')
            print("✅ Access Token:", access_token[:30] + "..." if len(access_token) > 30 else access_token)
            print("✅ Refresh Token:", refresh_token[:30] + "..." if len(refresh_token) > 30 else refresh_token)
            print("✅ Ready for frontend login!")
            return True
    except urllib.error.HTTPError as e:
        error_data = json.loads(e.read().decode())
        print("❌ Login failed:", e.code)
        print("❌ Error:", error_data)
        return False
    except Exception as e:
        print("❌ Connection error:", e)
        return False

if __name__ == "__main__":
    test_login()
