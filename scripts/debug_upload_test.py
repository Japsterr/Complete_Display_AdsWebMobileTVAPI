import os
import django
import sys

# Ensure running from project root
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
print('BASE_DIR=', BASE_DIR)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'signage_project.settings')
sys.path.insert(0, BASE_DIR)

django.setup()

from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from django.core.files.uploadedfile import SimpleUploadedFile
from api.models import Media

User = get_user_model()

# Try to get existing user by email; create one if not present
email = 'test@example.com'
user = User.objects.filter(email=email).first()
if not user:
    print('User not found; creating test user...')
    user = User.objects.create_user(email=email, password='testpass123')
else:
    print('Found user:', user.email)

client = APIClient()
client.force_authenticate(user=user)

png_bytes = b"\x89PNG\r\n\x1a\nPNGDATA"
file = SimpleUploadedFile('test.png', png_bytes, content_type='image/png')

print('Posting multipart to /api/v1/media/ ...')
resp = client.post('/api/v1/media/', {'file': file, 'name': 'test.png'}, format='multipart')
print('Response status:', resp.status_code)
try:
    print('Response data:', resp.data)
except Exception as e:
    print('Could not decode resp.data:', e)

print('Media count now:', Media.objects.count())
if Media.objects.exists():
    m = Media.objects.latest('uploaded_at')
    print('Last media:', m.media_id, m.name, m.file.name)
else:
    print('No media objects found')
