import urllib.request
import json

print('Testing custom login view...')
url = 'http://127.0.0.1:8000/api/v1/login/'
data = json.dumps({'email': 'carol@example.com', 'password': 'testpass'}).encode()
req = urllib.request.Request(url, data=data, headers={'Content-Type': 'application/json'}, method='POST')

try:
    with urllib.request.urlopen(req, timeout=5) as response:
        result = json.loads(response.read().decode())
        print('✓ CUSTOM LOGIN SUCCESSFUL!')
        print('Access token:', result['access'][:30] + '...')
        print('User data:', result.get('user'))
        print()
        print('Try the frontend now!')
except Exception as e:
    print('Error:', e)
