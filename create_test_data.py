#!/usr/bin/env python
import os
import sys
import django

# Add the project directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'signage_project.settings')
django.setup()

from api.models import User, Display, Campaign, Media, CampaignMedia

def create_test_data():
    print("Creating test data...")
    
    # Get the existing user and display
    try:
        user = User.objects.first()
        if not user:
            print("No users found. Please create a user first.")
            return
        
        display = Display.objects.filter(device_id='TEST-TV-001').first()
        if not display:
            print("Display TEST-TV-001 not found. Please register it first.")
            return
        
        print(f"Found user: {user.email}")
        print(f"Found display: {display.name}")
        
        # Create a test campaign
        campaign, created = Campaign.objects.get_or_create(
            name="Test Campaign",
            defaults={
                'description': 'Test campaign for TV app',
                'personal_user': user if user.account_type == 'personal' else None,
                'business': user.owned_business if hasattr(user, 'owned_business') else None,
                'created_by': user
            }
        )
        
        if created:
            print(f"Created campaign: {campaign.name}")
        else:
            print(f"Found existing campaign: {campaign.name}")
        
        # Create test media (we'll create a placeholder since we don't have actual files)
        media, created = Media.objects.get_or_create(
            name="Test Image",
            defaults={
                'description': 'Test image for campaign',
                'media_type': 'image',
                'personal_user': user if user.account_type == 'personal' else None,
                'business': user.owned_business if hasattr(user, 'owned_business') else None,
                'uploaded_by': user,
                'file': 'uploads/test-image.jpg'  # Placeholder path
            }
        )
        
        if created:
            print(f"Created media: {media.name}")
        else:
            print(f"Found existing media: {media.name}")
        
        # Link media to campaign
        campaign_media, created = CampaignMedia.objects.get_or_create(
            campaign=campaign,
            media=media,
            defaults={
                'display_duration_seconds': 5,  # 5 seconds
                'order': 1
            }
        )
        
        if created:
            print(f"Linked media to campaign")
        else:
            print(f"Media already linked to campaign")
        
        # Assign campaign to display
        display.default_campaign = campaign
        display.save()
        print(f"Assigned campaign to display: {display.name}")
        
        print("\n✅ Test data created successfully!")
        print(f"Display: {display.name}")
        print(f"Campaign: {campaign.name}")
        print(f"Media: {media.name}")
        print(f"Duration: {campaign_media.display_duration_seconds} seconds")
        
    except Exception as e:
        print(f"Error creating test data: {e}")

if __name__ == "__main__":
    create_test_data()
