"""
Django management command to run advanced POS synchronization scheduler
Stage 4 - Advanced POS Synchronization
"""
import json
from django.core.management.base import BaseCommand
from api.pos_scheduler import pos_sync_scheduler


class Command(BaseCommand):
    """Management command for POS sync scheduler"""
    
    help = 'Run the advanced POS synchronization scheduler'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--daemon',
            action='store_true',
            help='Run as daemon process (for production)',
        )
        parser.add_argument(
            '--test-duration',
            type=int,
            default=600,
            help='Test duration in seconds (default: 600)',
        )
        parser.add_argument(
            '--immediate-sync',
            type=int,
            help='Trigger immediate sync for specific POS integration ID',
        )
        parser.add_argument(
            '--menu-id',
            type=str,
            help='Specific menu ID to sync (use with --immediate-sync)',
        )
        parser.add_argument(
            '--health-check',
            action='store_true',
            help='Run health check and exit',
        )
    
    def handle(self, *args, **options):
        """Handle the management command"""
        
        if options['health_check']:
            self.run_health_check()
            return
        
        if options['immediate_sync']:
            self.run_immediate_sync(options['immediate_sync'], options.get('menu_id'))
            return
        
        self.stdout.write(
            self.style.SUCCESS('Starting advanced POS synchronization scheduler...')
        )
        
        try:
            pos_sync_scheduler.start_scheduler()
            
            if options['daemon']:
                self.stdout.write('Running as daemon process. Press Ctrl+C to stop.')
                # Run as daemon
                import time
                while True:
                    time.sleep(60)
            else:
                # Run for testing
                test_duration = options['test_duration']
                self.stdout.write(f'Running for {test_duration} seconds for testing...')
                import time
                time.sleep(test_duration)
                pos_sync_scheduler.stop_scheduler()
                
        except KeyboardInterrupt:
            self.stdout.write(self.style.WARNING('Stopping scheduler...'))
            pos_sync_scheduler.stop_scheduler()
        except Exception as e:
            self.stderr.write(self.style.ERROR(f'Scheduler error: {str(e)}'))
            pos_sync_scheduler.stop_scheduler()
            raise
        
        self.stdout.write(self.style.SUCCESS('POS synchronization scheduler stopped'))
    
    def run_health_check(self):
        """Run health check and display results"""
        from api.pos_scheduler import SyncHealthMonitor
        
        self.stdout.write('Running POS sync health check...')
        
        # Overall health
        overall_health = SyncHealthMonitor.get_health_status()
        self.stdout.write(f"Overall Status: {overall_health['status']}")
        self.stdout.write(f"Message: {overall_health['message']}")
        
        if overall_health['status'] in ['healthy', 'warning', 'unhealthy']:
            self.stdout.write(f"Success Rate: {overall_health['success_rate']}%")
            self.stdout.write(f"Total Integrations: {overall_health['total_integrations']}")
            self.stdout.write(f"Recent Syncs: {overall_health['recent_syncs']}")
        
        # Individual integration health
        from api.models import POSIntegration
        integrations = POSIntegration.objects.filter(is_active=True)
        
        if integrations.exists():
            self.stdout.write('\\nIndividual Integration Health:')
            for integration in integrations:
                health = SyncHealthMonitor.get_integration_health(integration.id)
                status_icon = {
                    'healthy': '✓',
                    'warning': '⚠',
                    'unhealthy': '✗',
                    'no_activity': '○',
                    'error': '✗'
                }.get(health['status'], '?')
                
                self.stdout.write(f"  {status_icon} {integration.name}: {health['status']}")
                if 'success_rate' in health:
                    self.stdout.write(f"    Success Rate: {health['success_rate']}%")
                if 'last_sync' in health and health['last_sync']:
                    self.stdout.write(f"    Last Sync: {health['last_sync']}")
    
    def run_immediate_sync(self, pos_integration_id, menu_id=None):
        """Run immediate sync for specific integration"""
        self.stdout.write(f'Triggering immediate sync for POS integration {pos_integration_id}...')
        
        try:
            result = pos_sync_scheduler.trigger_immediate_sync(pos_integration_id, menu_id)
            
            self.stdout.write(self.style.SUCCESS('Immediate sync completed!'))
            self.stdout.write(f"Results: {json.dumps(result, indent=2)}")
            
        except Exception as e:
            self.stderr.write(self.style.ERROR(f'Immediate sync failed: {str(e)}'))
            raise