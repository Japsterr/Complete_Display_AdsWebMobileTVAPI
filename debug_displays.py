#!/usr/bin/env python
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'signage_project.settings')
django.setup()

from api.models import Display, Campaign

print("=== ALL DISPLAYS ===")
displays = Display.objects.all()
for display in displays:
    print(f"ID: {display.display_id}")
    print(f"Name: {display.name}")
    print(f"Device ID: {display.device_id}")
    print(f"Activation Status: {display.activation_status}")
    print(f"Default Campaign: {display.default_campaign}")
    if display.default_campaign:
        print(f"Default Campaign Name: {display.default_campaign.name}")
    print("---")

print("\n=== ALL CAMPAIGNS ===")
campaigns = Campaign.objects.all()
for campaign in campaigns:
    print(f"Campaign ID: {campaign.campaign_id}")
    print(f"PK: {campaign.pk}")
    print(f"Name: {campaign.name}")
    print(f"Description: {campaign.description}")
    print("---")
