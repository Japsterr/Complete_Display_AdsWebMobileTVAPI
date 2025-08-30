# POS Synchronization Scheduler - Stage 4
import json
import time
import threading
import logging
from datetime import datetime, timedelta
from django.core.management.base import BaseCommand
from django.core.cache import cache
from django.db import transaction

from api.models import POSIntegration, Menu, POSUpdateLog
from api.pos_sync_manager import POSSyncManager

# Simple scheduler implementation (replace with celery for production)
class SimpleScheduler:
    def __init__(self):
        self.jobs = []
    
    def every(self, interval):
        return ScheduleJob(self, interval)
    
    def run_pending(self):
        for job in self.jobs:
            if job.should_run():
                job.run()

class ScheduleJob:
    def __init__(self, scheduler, interval):
        self.scheduler = scheduler
        self.interval = interval
        self.job_func = None
        self.last_run = None
        self.unit = None
        self.at_time = None
        
    def minutes(self):
        self.unit = 'minutes'
        self.scheduler.jobs.append(self)
        return self
        
    def hour(self):
        self.unit = 'hour'
        self.scheduler.jobs.append(self)
        return self
        
    def day(self):
        self.unit = 'day'
        self.scheduler.jobs.append(self)
        return self
        
    def at(self, time_str):
        self.at_time = time_str
        return self
        
    def do(self, job_func):
        self.job_func = job_func
        return self
        
    def should_run(self):
        if not self.last_run:
            self.last_run = datetime.now()
            return True
            
        now = datetime.now()
        if self.unit == 'minutes':
            return (now - self.last_run).total_seconds() >= self.interval * 60
        elif self.unit == 'hour':
            return (now - self.last_run).total_seconds() >= 3600
        elif self.unit == 'day':
            if self.at_time:
                target_time = datetime.strptime(self.at_time, "%H:%M").time()
                if now.time() >= target_time and (now - self.last_run).days >= 1:
                    return True
            else:
                return (now - self.last_run).days >= 1
        return False
        
    def run(self):
        if self.job_func:
            self.job_func()
            self.last_run = datetime.now()

schedule = SimpleScheduler()

logger = logging.getLogger(__name__)


class POSSyncScheduler:
    """Advanced scheduling system for POS synchronization"""
    
    def __init__(self):
        self.sync_manager = POSSyncManager()
        self.running = False
        self.scheduler_thread = None
        
    def start_scheduler(self):
        """Start the background scheduler"""
        if self.running:
            logger.warning("Scheduler already running")
            return
        
        self.running = True
        self.scheduler_thread = threading.Thread(target=self._run_scheduler, daemon=True)
        self.scheduler_thread.start()
        logger.info("POS sync scheduler started")
    
    def stop_scheduler(self):
        """Stop the background scheduler"""
        self.running = False
        if self.scheduler_thread:
            self.scheduler_thread.join(timeout=5)
        logger.info("POS sync scheduler stopped")
    
    def _run_scheduler(self):
        """Main scheduler loop"""
        # Schedule different sync frequencies
        schedule.every(5).minutes.do(self._sync_high_priority)
        schedule.every(15).minutes.do(self._sync_medium_priority)
        schedule.every().hour.do(self._sync_low_priority)
        schedule.every().day.at("02:00").do(self._daily_maintenance)
        
        while self.running:
            try:
                schedule.run_pending()
                time.sleep(60)  # Check every minute
            except Exception as e:
                logger.error(f"Scheduler error: {str(e)}")
                time.sleep(60)  # Continue after error
    
    def _sync_high_priority(self):
        """Sync high-priority POS integrations (every 5 minutes)"""
        try:
            high_priority_integrations = POSIntegration.objects.filter(
                is_active=True,
                sync_priority='high'
            )
            
            for pos_integration in high_priority_integrations:
                self._perform_scheduled_sync(pos_integration, 'high_priority_sync')
                
        except Exception as e:
            logger.error(f"High priority sync error: {str(e)}")
    
    def _sync_medium_priority(self):
        """Sync medium-priority POS integrations (every 15 minutes)"""
        try:
            medium_priority_integrations = POSIntegration.objects.filter(
                is_active=True,
                sync_priority='medium'
            )
            
            for pos_integration in medium_priority_integrations:
                self._perform_scheduled_sync(pos_integration, 'medium_priority_sync')
                
        except Exception as e:
            logger.error(f"Medium priority sync error: {str(e)}")
    
    def _sync_low_priority(self):
        """Sync low-priority POS integrations (every hour)"""
        try:
            low_priority_integrations = POSIntegration.objects.filter(
                is_active=True,
                sync_priority='low'
            )
            
            for pos_integration in low_priority_integrations:
                self._perform_scheduled_sync(pos_integration, 'low_priority_sync')
                
        except Exception as e:
            logger.error(f"Low priority sync error: {str(e)}")
    
    def _perform_scheduled_sync(self, pos_integration, operation_type):
        """Perform sync for a specific POS integration"""
        try:
            # Check if sync is already in progress
            cache_key = f"pos_sync_in_progress_{pos_integration.id}"
            if cache.get(cache_key):
                logger.debug(f"Sync already in progress for POS {pos_integration.id}")
                return
            
            # Set sync in progress flag
            cache.set(cache_key, True, timeout=300)  # 5 minute timeout
            
            # Get associated menus
            menus = Menu.objects.filter(
                # Add filter for menus associated with this POS integration
                # This depends on your Menu model structure
            )
            
            total_updates = 0
            for menu in menus:
                try:
                    result = self.sync_manager.sync_menu_bidirectional(
                        menu.menu_id,
                        pos_integration.id
                    )
                    total_updates += result.get('total_updates', 0)
                    
                except Exception as menu_error:
                    logger.error(f"Menu sync error for {menu.menu_id}: {str(menu_error)}")
                    
                    # Log the error
                    POSUpdateLog.objects.create(
                        pos_integration=pos_integration,
                        operation=operation_type,
                        success=False,
                        details=json.dumps({
                            'error': str(menu_error),
                            'menu_id': menu.menu_id,
                            'timestamp': datetime.now().isoformat()
                        })
                    )
            
            # Log successful sync
            POSUpdateLog.objects.create(
                pos_integration=pos_integration,
                operation=operation_type,
                success=True,
                details=json.dumps({
                    'total_updates': total_updates,
                    'menus_synced': len(menus),
                    'timestamp': datetime.now().isoformat()
                })
            )
            
            logger.info(f"Scheduled sync completed for POS {pos_integration.id}: {total_updates} updates")
            
        except Exception as e:
            logger.error(f"Scheduled sync failed for POS {pos_integration.id}: {str(e)}")
            
            # Log the failure
            POSUpdateLog.objects.create(
                pos_integration=pos_integration,
                operation=operation_type,
                success=False,
                details=json.dumps({
                    'error': str(e),
                    'timestamp': datetime.now().isoformat()
                })
            )
        
        finally:
            # Clear sync in progress flag
            cache.delete(cache_key)
    
    def _daily_maintenance(self):
        """Perform daily maintenance tasks"""
        try:
            logger.info("Starting daily POS sync maintenance")
            
            # Clean up old logs (keep last 30 days)
            thirty_days_ago = datetime.now() - timedelta(days=30)
            deleted_count = POSUpdateLog.objects.filter(
                created_at__lt=thirty_days_ago
            ).delete()[0]
            
            logger.info(f"Cleaned up {deleted_count} old sync logs")
            
            # Update sync statistics cache
            self._update_sync_statistics()
            
            # Check for inactive integrations
            self._check_inactive_integrations()
            
            logger.info("Daily maintenance completed")
            
        except Exception as e:
            logger.error(f"Daily maintenance error: {str(e)}")
    
    def _update_sync_statistics(self):
        """Update cached sync statistics for all POS integrations"""
        try:
            integrations = POSIntegration.objects.filter(is_active=True)
            
            for integration in integrations:
                # Calculate success rate
                total_syncs = POSUpdateLog.objects.filter(
                    pos_integration=integration,
                    operation__contains='sync'
                ).count()
                
                successful_syncs = POSUpdateLog.objects.filter(
                    pos_integration=integration,
                    operation__contains='sync',
                    success=True
                ).count()
                
                success_rate = (successful_syncs / total_syncs * 100) if total_syncs > 0 else 0
                
                # Cache the statistics
                cache_key = f"pos_sync_stats_{integration.id}"
                stats = {
                    'total_syncs': total_syncs,
                    'successful_syncs': successful_syncs,
                    'success_rate': round(success_rate, 2),
                    'last_updated': datetime.now().isoformat()
                }
                cache.set(cache_key, stats, timeout=86400)  # Cache for 24 hours
                
        except Exception as e:
            logger.error(f"Error updating sync statistics: {str(e)}")
    
    def _check_inactive_integrations(self):
        """Check for POS integrations that haven't synced recently"""
        try:
            # Find integrations that haven't synced in the last 24 hours
            twenty_four_hours_ago = datetime.now() - timedelta(hours=24)
            
            inactive_integrations = POSIntegration.objects.filter(
                is_active=True
            ).exclude(
                id__in=POSUpdateLog.objects.filter(
                    created_at__gte=twenty_four_hours_ago,
                    success=True
                ).values_list('pos_integration_id', flat=True)
            )
            
            for integration in inactive_integrations:
                logger.warning(f"POS integration {integration.id} ({integration.name}) has not synced in 24+ hours")
                
                # Optionally, try to test the connection
                try:
                    pos_items = self.sync_manager._fetch_pos_items(integration)
                    if not pos_items:
                        logger.error(f"POS integration {integration.id} connection test failed")
                except Exception as test_error:
                    logger.error(f"POS integration {integration.id} connection error: {str(test_error)}")
                    
        except Exception as e:
            logger.error(f"Error checking inactive integrations: {str(e)}")
    
    def trigger_immediate_sync(self, pos_integration_id, menu_id=None):
        """Trigger an immediate sync for specific POS integration"""
        try:
            pos_integration = POSIntegration.objects.get(id=pos_integration_id)
            
            if menu_id:
                # Sync specific menu
                result = self.sync_manager.sync_menu_bidirectional(menu_id, pos_integration_id)
                
                POSUpdateLog.objects.create(
                    pos_integration=pos_integration,
                    operation='immediate_sync',
                    success=True,
                    details=json.dumps({
                        'menu_id': menu_id,
                        'result': result,
                        'timestamp': datetime.now().isoformat()
                    })
                )
                
                return result
            else:
                # Sync all menus for this integration
                menus = Menu.objects.filter(
                    # Add appropriate filter based on your model structure
                )
                
                total_result = {'total_updates': 0, 'menus_synced': 0}
                
                for menu in menus:
                    try:
                        result = self.sync_manager.sync_menu_bidirectional(
                            menu.menu_id,
                            pos_integration_id
                        )
                        total_result['total_updates'] += result.get('total_updates', 0)
                        total_result['menus_synced'] += 1
                        
                    except Exception as menu_error:
                        logger.error(f"Menu sync error: {str(menu_error)}")
                
                POSUpdateLog.objects.create(
                    pos_integration=pos_integration,
                    operation='immediate_sync_all',
                    success=True,
                    details=json.dumps({
                        'result': total_result,
                        'timestamp': datetime.now().isoformat()
                    })
                )
                
                return total_result
                
        except Exception as e:
            logger.error(f"Immediate sync failed: {str(e)}")
            raise


# Global scheduler instance
pos_sync_scheduler = POSSyncScheduler()


class Command(BaseCommand):
    """Django management command to run POS sync scheduler"""
    
    help = 'Run the POS synchronization scheduler'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--daemon',
            action='store_true',
            help='Run as daemon process',
        )
    
    def handle(self, *args, **options):
        """Handle the management command"""
        self.stdout.write('Starting POS sync scheduler...')
        
        try:
            pos_sync_scheduler.start_scheduler()
            
            if options['daemon']:
                # Run as daemon
                while True:
                    time.sleep(60)
            else:
                # Run for testing (10 minutes)
                time.sleep(600)
                pos_sync_scheduler.stop_scheduler()
                
        except KeyboardInterrupt:
            self.stdout.write('Stopping scheduler...')
            pos_sync_scheduler.stop_scheduler()
        except Exception as e:
            self.stderr.write(f'Scheduler error: {str(e)}')
            pos_sync_scheduler.stop_scheduler()
            raise
        
        self.stdout.write('POS sync scheduler stopped')


# Additional utility functions for sync management
class SyncHealthMonitor:
    """Monitor the health of POS synchronization"""
    
    @staticmethod
    def get_health_status():
        """Get overall health status of all POS integrations"""
        try:
            integrations = POSIntegration.objects.filter(is_active=True)
            total_integrations = integrations.count()
            
            if total_integrations == 0:
                return {
                    'status': 'no_integrations',
                    'message': 'No active POS integrations found'
                }
            
            # Check recent sync success rate
            one_hour_ago = datetime.now() - timedelta(hours=1)
            recent_logs = POSUpdateLog.objects.filter(
                created_at__gte=one_hour_ago,
                operation__contains='sync'
            )
            
            if recent_logs.count() == 0:
                return {
                    'status': 'no_recent_activity',
                    'message': 'No sync activity in the last hour'
                }
            
            successful_syncs = recent_logs.filter(success=True).count()
            total_syncs = recent_logs.count()
            success_rate = (successful_syncs / total_syncs * 100) if total_syncs > 0 else 0
            
            if success_rate >= 95:
                status = 'healthy'
            elif success_rate >= 80:
                status = 'warning'
            else:
                status = 'unhealthy'
            
            return {
                'status': status,
                'success_rate': round(success_rate, 2),
                'total_integrations': total_integrations,
                'recent_syncs': total_syncs,
                'successful_syncs': successful_syncs,
                'message': f'Success rate: {success_rate:.1f}% over last hour'
            }
            
        except Exception as e:
            logger.error(f"Health check error: {str(e)}")
            return {
                'status': 'error',
                'message': str(e)
            }
    
    @staticmethod
    def get_integration_health(pos_integration_id):
        """Get health status for specific POS integration"""
        try:
            pos_integration = POSIntegration.objects.get(id=pos_integration_id)
            
            # Check recent activity
            six_hours_ago = datetime.now() - timedelta(hours=6)
            recent_logs = POSUpdateLog.objects.filter(
                pos_integration=pos_integration,
                created_at__gte=six_hours_ago,
                operation__contains='sync'
            )
            
            if recent_logs.count() == 0:
                return {
                    'status': 'no_activity',
                    'message': 'No sync activity in the last 6 hours'
                }
            
            successful_syncs = recent_logs.filter(success=True).count()
            total_syncs = recent_logs.count()
            success_rate = (successful_syncs / total_syncs * 100) if total_syncs > 0 else 0
            
            last_sync = recent_logs.order_by('-created_at').first()
            
            if success_rate >= 90:
                status = 'healthy'
            elif success_rate >= 70:
                status = 'warning'
            else:
                status = 'unhealthy'
            
            return {
                'status': status,
                'pos_integration_id': pos_integration_id,
                'success_rate': round(success_rate, 2),
                'recent_syncs': total_syncs,
                'successful_syncs': successful_syncs,
                'last_sync': last_sync.created_at if last_sync else None,
                'last_sync_success': last_sync.success if last_sync else None
            }
            
        except POSIntegration.DoesNotExist:
            return {
                'status': 'not_found',
                'message': 'POS integration not found'
            }
        except Exception as e:
            logger.error(f"Integration health check error: {str(e)}")
            return {
                'status': 'error',
                'message': str(e)
            }