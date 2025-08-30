# Django Management Command for Stage 6 Performance Optimization
from django.core.management.base import BaseCommand
from django.core.cache import cache
from django.db import connection
from api.deployment_optimizer import deployment_optimizer, performance_monitor
from api.advanced_cache import AdvancedCacheManager
import json


class Command(BaseCommand):
    help = 'Optimize system performance for production deployment'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--mode',
            type=str,
            default='analyze',
            choices=['analyze', 'optimize', 'monitor', 'deploy-check'],
            help='Operation mode'
        )
        
        parser.add_argument(
            '--component',
            type=str,
            choices=['database', 'cache', 'all'],
            default='all',
            help='Component to optimize'
        )
        
        parser.add_argument(
            '--format',
            type=str,
            choices=['json', 'text'],
            default='text',
            help='Output format'
        )
    
    def handle(self, *args, **options):
        mode = options['mode']
        component = options['component']
        output_format = options['format']
        
        try:
            if mode == 'analyze':
                self.analyze_performance(component, output_format)
            elif mode == 'optimize':
                self.optimize_performance(component, output_format)
            elif mode == 'monitor':
                self.start_monitoring(output_format)
            elif mode == 'deploy-check':
                self.deployment_checklist(output_format)
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error during performance optimization: {str(e)}')
            )
    
    def analyze_performance(self, component, output_format):
        """Analyze current performance"""
        self.stdout.write("Analyzing system performance...")
        
        results = {}
        
        if component in ['database', 'all']:
            self.stdout.write("Analyzing database performance...")
            db_analysis = deployment_optimizer.optimize_database_settings()
            results['database'] = db_analysis
        
        if component in ['cache', 'all']:
            self.stdout.write("Analyzing cache performance...")
            cache_analysis = deployment_optimizer.optimize_cache_settings()
            results['cache'] = cache_analysis
        
        # System metrics
        if component == 'all':
            monitor_summary = performance_monitor.get_performance_summary()
            results['system'] = monitor_summary
        
        self._output_results(results, output_format, "Performance Analysis")
    
    def optimize_performance(self, component, output_format):
        """Apply performance optimizations"""
        self.stdout.write("Applying performance optimizations...")
        
        results = {}
        
        if component in ['cache', 'all']:
            # Warm up cache
            self.stdout.write("Warming up cache...")
            cache_manager = AdvancedCacheManager()
            
            # Warm frequently accessed data
            try:
                from api.models import Menu, MenuItem, Campaign
                
                # Cache active menus
                active_menus = Menu.objects.filter(is_active=True)[:10]
                for menu in active_menus:
                    cache_key = f"menu_display_{menu.id}"
                    cache.set(cache_key, menu, timeout=300)
                
                # Cache active campaigns
                active_campaigns = Campaign.objects.filter(is_active=True)[:10]
                for campaign in active_campaigns:
                    cache_key = f"campaign_{campaign.id}"
                    cache.set(cache_key, campaign, timeout=300)
                
                results['cache_warming'] = {
                    'status': 'completed',
                    'menus_cached': len(active_menus),
                    'campaigns_cached': len(active_campaigns)
                }
                
            except Exception as e:
                results['cache_warming'] = {
                    'status': 'error',
                    'error': str(e)
                }
        
        if component in ['database', 'all']:
            # Database optimization suggestions
            db_optimization = deployment_optimizer.optimize_database_settings()
            results['database_optimization'] = db_optimization
        
        self._output_results(results, output_format, "Performance Optimization")
    
    def start_monitoring(self, output_format):
        """Start performance monitoring"""
        self.stdout.write("Starting performance monitoring...")
        
        success = performance_monitor.start_monitoring()
        
        if success:
            self.stdout.write(
                self.style.SUCCESS("Performance monitoring started successfully")
            )
            
            # Show initial metrics
            import time
            time.sleep(5)  # Wait for initial metrics
            
            summary = performance_monitor.get_performance_summary()
            self._output_results(summary, output_format, "Initial Performance Metrics")
        else:
            self.stdout.write(
                self.style.ERROR("Failed to start performance monitoring")
            )
    
    def deployment_checklist(self, output_format):
        """Generate deployment checklist"""
        self.stdout.write("Generating deployment checklist...")
        
        checklist = deployment_optimizer.generate_deployment_checklist()
        self._output_results(checklist, output_format, "Deployment Checklist")
        
        # Show summary
        summary = checklist.get('summary', {})
        total_tasks = summary.get('total_tasks', 0)
        completed_tasks = summary.get('completed_tasks', 0)
        critical_pending = summary.get('critical_pending', 0)
        
        self.stdout.write(f"\nDeployment Readiness Summary:")
        self.stdout.write(f"Total tasks: {total_tasks}")
        self.stdout.write(f"Completed: {completed_tasks}")
        self.stdout.write(f"Progress: {summary.get('progress_percentage', 0):.1f}%")
        
        if critical_pending > 0:
            self.stdout.write(
                self.style.WARNING(f"Critical tasks pending: {critical_pending}")
            )
        else:
            self.stdout.write(
                self.style.SUCCESS("No critical tasks pending")
            )
    
    def _output_results(self, results, output_format, title):
        """Output results in specified format"""
        if output_format == 'json':
            self.stdout.write(json.dumps(results, indent=2, default=str))
        else:
            self.stdout.write(f"\n{title}:")
            self.stdout.write("=" * len(title))
            self._format_text_output(results)
    
    def _format_text_output(self, data, indent=0):
        """Format data as readable text"""
        for key, value in data.items():
            if isinstance(value, dict):
                self.stdout.write("  " * indent + f"{key}:")
                self._format_text_output(value, indent + 1)
            elif isinstance(value, list):
                self.stdout.write("  " * indent + f"{key}:")
                for i, item in enumerate(value):
                    if isinstance(item, dict):
                        self.stdout.write("  " * (indent + 1) + f"[{i}]:")
                        self._format_text_output(item, indent + 2)
                    else:
                        self.stdout.write("  " * (indent + 1) + f"- {item}")
            else:
                self.stdout.write("  " * indent + f"{key}: {value}")