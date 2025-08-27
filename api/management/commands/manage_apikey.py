from django.core.management.base import BaseCommand, CommandError
from api.models import ApiKey, Business
import secrets


class Command(BaseCommand):
    help = 'Manage ApiKeys: create, rotate, revoke, list'

    def add_arguments(self, parser):
        sub = parser.add_subparsers(dest='action')

        create_parser = sub.add_parser('create')
        create_parser.add_argument('--name', required=True)
        create_parser.add_argument('--business-id', type=int, required=False)

        rotate_parser = sub.add_parser('rotate')
        rotate_parser.add_argument('--id', type=int, required=True, help='ApiKey id to rotate')

        revoke_parser = sub.add_parser('revoke')
        revoke_parser.add_argument('--id', type=int, required=True, help='ApiKey id to revoke')

        list_parser = sub.add_parser('list')
        list_parser.add_argument('--business-id', type=int, required=False)

    def handle(self, *args, **options):
        action = options.get('action')
        if action == 'create':
            name = options.get('name')
            business_id = options.get('business_id')
            business = None
            if business_id:
                try:
                    business = Business.objects.get(pk=business_id)
                except Business.DoesNotExist:
                    raise CommandError('Business not found')
            key = secrets.token_urlsafe(32)
            ak = ApiKey.objects.create(name=name, key=key, business=business)
            self.stdout.write(self.style.SUCCESS(f'Created ApiKey id={ak.key_id} name="{ak.name}" key="{ak.key}"'))

        elif action == 'rotate':
            ak_id = options.get('id')
            try:
                ak = ApiKey.objects.get(pk=ak_id)
            except ApiKey.DoesNotExist:
                raise CommandError('ApiKey not found')
            new_key = secrets.token_urlsafe(32)
            ak.key = new_key
            ak.revoked = False
            ak.save()
            self.stdout.write(self.style.SUCCESS(f'Rotated ApiKey id={ak.key_id} new_key="{ak.key}"'))

        elif action == 'revoke':
            ak_id = options.get('id')
            try:
                ak = ApiKey.objects.get(pk=ak_id)
            except ApiKey.DoesNotExist:
                raise CommandError('ApiKey not found')
            ak.revoked = True
            ak.save()
            self.stdout.write(self.style.SUCCESS(f'Revoked ApiKey id={ak.key_id} name="{ak.name}"'))

        elif action == 'list':
            business_id = options.get('business_id')
            qs = ApiKey.objects.all()
            if business_id:
                qs = qs.filter(business_id=business_id)
            for ak in qs.order_by('-created_at'):
                status = 'revoked' if ak.revoked else 'active'
                self.stdout.write(f'id={ak.key_id} name="{ak.name}" business_id={ak.business_id} status={status} created_at={ak.created_at} key={ak.key if not ak.revoked else 'REVOKED'}')
        else:
            raise CommandError('No action specified. Use create|rotate|revoke|list')
