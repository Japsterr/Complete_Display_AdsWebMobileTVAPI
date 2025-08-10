#!/usr/bin/env python
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'signage_project.settings')
django.setup()

from api.models import Display, Campaign

def main():
    try:
        display = Display.objects.first()
        campaign = Campaign.objects.first()
        if not display or not campaign:
            print("No display or campaign found to demonstrate assignment.")
            return
        print("Before assignment:")
        print(f"Display: {display.name}")
        print(f"Current campaign: {display.default_campaign}")
        display.default_campaign = campaign
        display.save()
        print("\nAfter assignment:")
        print(f"Display: {display.name}")
        print(f"New campaign: {display.default_campaign}")
        print(f"Campaign name: {display.default_campaign.name}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
