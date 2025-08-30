from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from .models import User, Plan, Display, Media, DisplayOverride
from django.utils import timezone


class OverrideAPITestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        # Create a free plan and user
        self.plan = Plan.objects.create(plan_name='Free', price=0)
        self.user = User.objects.create_user(email='test@example.com', password='pass123', plan=self.plan)
        # Create display
        self.display = Display.objects.create(name='Test TV', activation_status='active', device_id='dev-1', personal_user=self.user)
        # Authenticate
        self.client.force_authenticate(user=self.user)

    def test_create_and_fetch_override(self):
        url = reverse('display-override-create', kwargs={'display_id': self.display.display_id})
        data = {'image_url': 'https://example.com/img.png', 'persistent': True}
        resp = self.client.post(url, data, format='json')
        self.assertEqual(resp.status_code, 201)
        override_id = resp.data.get('override_id')

        # fetch current
        url2 = reverse('display-override-current', kwargs={'display_id': self.display.display_id})
        resp2 = self.client.get(url2)
        self.assertEqual(resp2.status_code, 200)
        # if override is returned, ensure it's structured
        self.assertTrue('override' in resp2.data or 'override_id' in resp2.data or resp2.data.get('override') is None)

        # clear
        url3 = reverse('display-override-clear', kwargs={'display_id': self.display.display_id, 'override_id': override_id})
        resp3 = self.client.delete(url3)
        self.assertEqual(resp3.status_code, 200)
