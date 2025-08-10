from django.utils import timezone
from datetime import timedelta
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model
from api.models import Plan, Display, Campaign, Media, CampaignMedia, MediaImpression, DeviceHeartbeat

User = get_user_model()

class AnalyticsEndpointsTests(APITestCase):
    def setUp(self):
        self.plan = Plan.objects.create(plan_name="Test", price=0)
        self.user = User.objects.create_user(email="ana@test.com", password="pass", plan=self.plan)
        # Login
        res = self.client.post('/api/v1/login/', { 'email': 'ana@test.com', 'password': 'pass' })
        self.assertEqual(res.status_code, 200)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {res.data['access']}")
        # Display and campaign/media
        self.display = Display.objects.create(name="D1", personal_user=self.user, registered_by=self.user, device_id="DEV-1", activation_status='active')
        self.campaign = Campaign.objects.create(name="C1", personal_user=self.user, created_by=self.user)
        self.media = Media.objects.create(name="M1", personal_user=self.user, uploaded_by=self.user, file="uploads/test.jpg", media_type='image')
        CampaignMedia.objects.create(campaign=self.campaign, media=self.media, display_duration_seconds=5, order=0)

        # Impressions in the last 24h and 7d
        now = timezone.now()
        for h in range(3):
            MediaImpression.objects.create(
                display=self.display,
                campaign=self.campaign,
                media=self.media,
                started_at=now - timedelta(hours=h),
                duration_shown=5,
                scheduled_duration=5,
                completed=True,
                sequence_number=1,
                total_media_in_campaign=1,
            )
        # A week ago window too
        MediaImpression.objects.create(
            display=self.display,
            campaign=self.campaign,
            media=self.media,
            started_at=now - timedelta(days=6, hours=2),
            duration_shown=7,
            scheduled_duration=7,
            completed=True,
            sequence_number=1,
            total_media_in_campaign=1,
        )
        # Heartbeats in last hour
        for m in range(10):
            DeviceHeartbeat.objects.create(display=self.display, timestamp=now - timedelta(minutes=m))

    def test_analytics_summary_hourly(self):
        end = timezone.now()
        start = end - timedelta(hours=24)
        res = self.client.get('/api/v1/analytics/summary/', { 'start': start.isoformat(), 'end': end.isoformat(), 'granularity': 'hour' })
        self.assertEqual(res.status_code, 200)
        data = res.data
        self.assertIn('uptime', data)
        self.assertIn('impressions_timeseries_24h', data)
        self.assertGreaterEqual(len(data['impressions_timeseries_24h']), 1)

    def test_campaign_breakdown(self):
        end = timezone.now()
        start = end - timedelta(days=7)
        res = self.client.get('/api/v1/analytics/campaign-breakdown/', { 'start': start.date().isoformat(), 'end': end.date().isoformat() })
        self.assertEqual(res.status_code, 200)
        data = res.data
        self.assertIn('campaigns', data)
        self.assertGreaterEqual(len(data['campaigns']), 1)
        first = data['campaigns'][0]
        self.assertIn('campaign_id', first)
        self.assertIn('total_impressions', first)

    def test_export_csv_filters(self):
        # impressions
        end = timezone.now()
        start = end - timedelta(days=1)
        res = self.client.get('/api/v1/analytics/export/impressions.csv', { 'start': start.isoformat(), 'end': end.isoformat() })
        self.assertEqual(res.status_code, 200)
        self.assertTrue(res['Content-Type'].startswith('text/csv'))
        # devices
        res2 = self.client.get('/api/v1/analytics/export/devices.csv', { 'start': start.isoformat(), 'end': end.isoformat() })
        self.assertEqual(res2.status_code, 200)
        self.assertTrue(res2['Content-Type'].startswith('text/csv'))
