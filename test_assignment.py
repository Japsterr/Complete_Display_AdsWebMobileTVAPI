#!/usr/bin/env python
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'signage_project.settings')
django.setup()

from api.models import Display, Campaign

# Get the display and campaign
display = Display.objects.get(display_id=2)
campaign = Campaign.objects.get(campaign_id=5)  # Test Campaign

print(f"Before assignment:")
print(f"Display: {display.name}")
print(f"Current campaign: {display.default_campaign}")

# Assign campaign
display.default_campaign = campaign
display.save()

print(f"\nAfter assignment:")
print(f"Display: {display.name}")
print(f"New campaign: {display.default_campaign}")
print(f"Campaign name: {display.default_campaign.name}")
