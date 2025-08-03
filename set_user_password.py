#!/usr/bin/env python
import os
import sys
import django

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'signage_project.settings')
django.setup()

from api.models import User

def set_password():
    print("Setting password for test users...")
    
    # Update carol@example.com password to be consistent
    try:
        carol = User.objects.get(email='carol@example.com')
        carol.set_password('testpass123')
        carol.save()
        print("✅ Set password for carol@example.com: testpass123")
    except User.DoesNotExist:
        print("❌ User carol@example.com not found")
    
    # Update bosman.japie@gmail.com password
    try:
        bosman = User.objects.get(email='bosman.japie@gmail.com')
        bosman.set_password('testpass123')
        bosman.save()
        print("✅ Set password for bosman.japie@gmail.com: testpass123")
    except User.DoesNotExist:
        print("❌ User bosman.japie@gmail.com not found")
    
    print("\n🎉 You can now login with:")
    print("Email: carol@example.com")
    print("Password: testpass123")
    print("\nOR")
    print("Email: bosman.japie@gmail.com") 
    print("Password: testpass123")

if __name__ == "__main__":
    set_password()
