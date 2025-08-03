from django.core.management.base import BaseCommand
from api.models import Plan

class Command(BaseCommand):
    help = 'Set up the pricing plans for DisplayAds'

    def handle(self, *args, **options):
        plans_data = [
            {
                'plan_name': 'Free',
                'price': 0.00,
                'currency': 'ZAR',
                'max_campaigns': 3,
                'max_displays': 5,
                'max_images': 10,
                'max_videos': 0,
                'max_users': 1,
                'max_storage_gb': 0.5,  # 500MB for free
                'has_video_support': False,
                'has_advanced_analytics': False,
                'has_api_access': False,
                'has_custom_branding': False,
                'has_priority_support': False,
                'has_advanced_scheduling': False,
                'max_screens': 5,
                'has_multi_user': False,
            },
            {
                'plan_name': 'Starter',
                'price': 99.00,
                'currency': 'ZAR',
                'max_campaigns': 15,
                'max_displays': 25,
                'max_images': 100,
                'max_videos': 20,
                'max_users': 3,
                'max_storage_gb': 10.0,  # 10GB storage
                'has_video_support': True,
                'has_advanced_analytics': True,
                'has_api_access': False,
                'has_custom_branding': False,
                'has_priority_support': True,
                'has_advanced_scheduling': True,
                'max_screens': 25,
                'has_multi_user': True,
            },
            {
                'plan_name': 'Professional',
                'price': 499.00,
                'currency': 'ZAR',
                'max_campaigns': 999999,  # "Unlimited"
                'max_displays': 100,
                'max_images': 999999,  # "Unlimited"
                'max_videos': 999999,  # "Unlimited"
                'max_users': 10,
                'max_storage_gb': 999999.0,  # Unlimited storage
                'has_video_support': True,
                'has_advanced_analytics': True,
                'has_api_access': True,
                'has_custom_branding': True,
                'has_priority_support': True,
                'has_advanced_scheduling': True,
                'max_screens': 100,
                'has_multi_user': True,
            }
        ]

        for plan_data in plans_data:
            plan, created = Plan.objects.get_or_create(
                plan_name=plan_data['plan_name'],
                defaults=plan_data
            )
            
            if created:
                self.stdout.write(
                    self.style.SUCCESS(f'✅ Created plan: {plan.plan_name} (R{plan.price}/month)')
                )
            else:
                # Update existing plan with new data
                for key, value in plan_data.items():
                    setattr(plan, key, value)
                plan.save()
                self.stdout.write(
                    self.style.WARNING(f'🔄 Updated plan: {plan.plan_name} (R{plan.price}/month)')
                )

        self.stdout.write(
            self.style.SUCCESS('\n🎉 Pricing plans setup complete!')
        )
        
        # Display summary
        self.stdout.write('\n📊 Plan Summary:')
        for plan in Plan.objects.all().order_by('price'):
            storage_display = f"{plan.max_storage_gb}GB" if plan.max_storage_gb < 999999 else "Unlimited"
            self.stdout.write(f'  • {plan.plan_name}: R{plan.price}/month')
            self.stdout.write(f'    - {plan.max_campaigns} campaigns, {plan.max_displays} displays')
            self.stdout.write(f'    - {plan.max_images} images, {plan.max_videos} videos')
            self.stdout.write(f'    - Storage: {storage_display}')
            self.stdout.write(f'    - Video support: {"✅" if plan.has_video_support else "❌"}')
            self.stdout.write('')
