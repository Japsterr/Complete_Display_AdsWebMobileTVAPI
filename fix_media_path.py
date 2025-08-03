#!/usr/bin/env python
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'signage_project.settings')
django.setup()

from api.models import Media

# Update the media record to use the correct path
try:
    media = Media.objects.get(media_id=1)
    print(f"Current file path: {media.file}")
    
    # Update the file path
    media.file = 'uploads/Screenshot_2025-08-01_211242.png'
    media.save()
    
    print(f"Updated file path: {media.file}")
    print("Media record updated successfully!")
    
except Media.DoesNotExist:
    print("Media record not found")
except Exception as e:
    print(f"Error: {e}")
