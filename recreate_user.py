import os
import sys
import django

# Add project root to Python path
sys.path.append(r'C:\DisplayAdsAPI')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'signage_project.settings')
django.setup()

from api.models import User

# Delete existing carol user if exists
try:
    existing_user = User.objects.get(email='carol@example.com')
    existing_user.delete()
    print("Deleted existing carol user")
except User.DoesNotExist:
    print("No existing carol user found")

# Create new user
user = User.objects.create_user(
    email='carol@example.com',
    password='testpass',
    account_type='personal'
)
print(f"Created user: {user.email} with password: testpass")
print("User can now log in!")
