from django.core.management.base import BaseCommand
from api.models import Campaign

class Command(BaseCommand):
    help = 'Update status for all existing campaigns'

    def handle(self, *args, **options):
        campaigns = Campaign.objects.all()
        updated_count = 0
        
        self.stdout.write('🔄 Updating campaign statuses...')
        
        for campaign in campaigns:
            old_status = campaign.status
            new_status = campaign.update_status()
            
            if old_status != new_status:
                updated_count += 1
                self.stdout.write(f'  📝 Updated "{campaign.name}": {old_status} → {new_status}')
            
        self.stdout.write(
            self.style.SUCCESS(f'✅ Updated {updated_count} campaigns')
        )
        
        # Display status summary
        status_counts = {}
        for campaign in Campaign.objects.all():
            status = campaign.status
            status_counts[status] = status_counts.get(status, 0) + 1
            
        self.stdout.write('\n📊 Campaign Status Summary:')
        for status, count in status_counts.items():
            status_emoji = {
                'draft': '📝',
                'ready': '✅', 
                'active': '🟢',
                'paused': '⏸️',
                'scheduled': '⏰',
                'expired': '⏰'
            }.get(status, '❓')
            
            self.stdout.write(f'  {status_emoji} {status.title()}: {count}')
