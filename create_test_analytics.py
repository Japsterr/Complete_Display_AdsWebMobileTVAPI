#!/usr/bin/env python
import os
import sys
import django
from datetime import datetime, timedelta

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'signage_project.settings')
django.setup()

from api.models import DeviceHeartbeat, MediaImpression, Display, Campaign, Media

def create_test_analytics():
    print("Creating test analytics data...")
    
    # Get test display
    try:
        display = Display.objects.get(device_id='TEST-TV-001')
        print(f"Found display: {display.name}")
    except Display.DoesNotExist:
        print("Display TEST-TV-001 not found")
        return
    
    # Get test campaign and media
    try:
        campaign = Campaign.objects.first()
        media = Media.objects.first()
        if not campaign or not media:
            print("No campaign or media found")
            return
        print(f"Using campaign: {campaign.name}")
        print(f"Using media: {media.name}")
    except:
        print("Error getting campaign/media")
        return
    
    # Create test heartbeats
    for i in range(5):
        heartbeat_time = datetime.now() - timedelta(minutes=i*2)
        DeviceHeartbeat.objects.create(
            display=display,
            timestamp=heartbeat_time,
            device_status='online'  # Correct field name
        )
        print(f"Created heartbeat at {heartbeat_time}")
    
    # Create test impressions
    for i in range(3):
        impression_time = datetime.now() - timedelta(minutes=i*5)
        MediaImpression.objects.create(
            display=display,
            campaign=campaign,
            media=media,
            started_at=impression_time,
            duration_shown=10 + i*5,  # 10, 15, 20 seconds
            scheduled_duration=15,  # Required field
            completed=True,
            sequence_number=i,  # Required field
            total_media_in_campaign=3  # Required field
        )
        print(f"Created impression at {impression_time}")
    
    print("\n✅ Test analytics data created!")
    print(f"Total heartbeats: {DeviceHeartbeat.objects.count()}")
    print(f"Total impressions: {MediaImpression.objects.count()}")

if __name__ == "__main__":
    create_test_analytics()
