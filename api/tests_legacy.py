
from rest_framework.test import APITestCase
from .models import DisplayGroup, Tag, MediaApproval, Display, Media

class DisplayGroupEndpointTests(APITestCase):
	def setUp(self):
		self.plan = Plan.objects.create(plan_name="Test Plan", price=0)
		self.user = User.objects.create_user(email="testgroup@example.com", password="testpass", plan=self.plan)
		self.display = Display.objects.create(name="Test Display", registered_by=self.user)
		self.client.force_authenticate(user=self.user)

	def test_displaygroup_crud(self):
		# Create
		response = self.client.post(
			"/api/v1/display-groups/",
			{"name": "Group 1", "owner": self.user.id, "displays": [self.display.display_id]}
		)
		self.assertEqual(response.status_code, 201)
		group_id = response.data["id"]
		# Read
		response = self.client.get(f"/api/v1/display-groups/{group_id}/")
		self.assertEqual(response.status_code, 200)
		# Update
		response = self.client.patch(f"/api/v1/display-groups/{group_id}/", {"name": "Group Updated"})
		self.assertEqual(response.status_code, 200)
		# Delete
		response = self.client.delete(f"/api/v1/display-groups/{group_id}/")
		self.assertEqual(response.status_code, 204)

class TagEndpointTests(APITestCase):
	def setUp(self):
		self.plan = Plan.objects.create(plan_name="Test Plan", price=0)
		self.user = User.objects.create_user(email="testtag@example.com", password="testpass", plan=self.plan)
		self.client.force_authenticate(user=self.user)

	def test_tag_crud(self):
		# Create
		response = self.client.post("/api/v1/tags/", {"name": "Tag1"})
		self.assertEqual(response.status_code, 201)
		tag_id = response.data["id"]
		# Read
		response = self.client.get(f"/api/v1/tags/{tag_id}/")
		self.assertEqual(response.status_code, 200)
		# Update
		response = self.client.patch(f"/api/v1/tags/{tag_id}/", {"name": "TagUpdated"})
		self.assertEqual(response.status_code, 200)
		# Delete
		response = self.client.delete(f"/api/v1/tags/{tag_id}/")
		self.assertEqual(response.status_code, 204)

class MediaApprovalEndpointTests(APITestCase):
	def setUp(self):
		self.plan = Plan.objects.create(plan_name="Test Plan", price=0)
		self.user = User.objects.create_user(email="testapproval@example.com", password="testpass", plan=self.plan)
		self.media = Media.objects.create(name="Test Media", uploaded_by=self.user, personal_user=self.user, file="test.jpg")
		self.client.force_authenticate(user=self.user)

	def test_mediaapproval_crud(self):
		# Create
		response = self.client.post("/api/v1/media-approvals/", {"media": self.media.media_id, "status": "pending"})
		self.assertEqual(response.status_code, 201)
		approval_id = response.data["id"]
		# Read
		response = self.client.get(f"/api/v1/media-approvals/{approval_id}/")
		self.assertEqual(response.status_code, 200)
		# Update
		response = self.client.patch(f"/api/v1/media-approvals/{approval_id}/", {"status": "approved"})
		self.assertEqual(response.status_code, 200)
		# Delete
		response = self.client.delete(f"/api/v1/media-approvals/{approval_id}/")
		self.assertEqual(response.status_code, 204)

from rest_framework.test import APITestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from .models import Organization, Membership, Invitation, AuditLog, Plan

User = get_user_model()

class OrganizationEndpointTests(APITestCase):
	def setUp(self):
		self.plan = Plan.objects.create(plan_name="Test Plan", price=0)
		self.user = User.objects.create_user(email="testorg@example.com", password="testpass", plan=self.plan)
		self.client.force_authenticate(user=self.user)

	def test_organization_crud(self):
		# Create
		response = self.client.post("/api/v1/organizations/", {"name": "Test Org", "owner": self.user.id})
		self.assertEqual(response.status_code, 201)
		org_id = response.data["id"]
		# Read
		response = self.client.get(f"/api/v1/organizations/{org_id}/")
		self.assertEqual(response.status_code, 200)
		# Update
		response = self.client.patch(f"/api/v1/organizations/{org_id}/", {"name": "Updated Org"})
		self.assertEqual(response.status_code, 200)
		# Delete
		response = self.client.delete(f"/api/v1/organizations/{org_id}/")
		self.assertEqual(response.status_code, 204)

class MembershipEndpointTests(APITestCase):
	def setUp(self):
		self.plan = Plan.objects.create(plan_name="Test Plan", price=0)
		self.user = User.objects.create_user(email="testmember@example.com", password="testpass", plan=self.plan)
		self.org = Organization.objects.create(name="Org", owner=self.user)
		self.client.force_authenticate(user=self.user)

	def test_membership_crud(self):
		# Create
		response = self.client.post("/api/v1/memberships/", {"user": self.user.id, "organization": self.org.id, "role": "admin"})
		self.assertEqual(response.status_code, 201)
		mem_id = response.data["id"]
		# Read
		response = self.client.get(f"/api/v1/memberships/{mem_id}/")
		self.assertEqual(response.status_code, 200)
		# Update
		response = self.client.patch(f"/api/v1/memberships/{mem_id}/", {"role": "member"})
		self.assertEqual(response.status_code, 200)
		# Delete
		response = self.client.delete(f"/api/v1/memberships/{mem_id}/")
		self.assertEqual(response.status_code, 204)

class InvitationEndpointTests(APITestCase):
	def setUp(self):
		self.plan = Plan.objects.create(plan_name="Test Plan", price=0)
		self.user = User.objects.create_user(email="testinvite@example.com", password="testpass", plan=self.plan)
		self.org = Organization.objects.create(name="Org", owner=self.user)
		self.client.force_authenticate(user=self.user)

	def test_invitation_crud(self):
		# Create
		response = self.client.post("/api/v1/invitations/", {"email": "invitee@example.com", "organization": self.org.id, "invited_by": self.user.id, "accepted": False})
		self.assertEqual(response.status_code, 201)
		inv_id = response.data["id"]
		# Read
		response = self.client.get(f"/api/v1/invitations/{inv_id}/")
		self.assertEqual(response.status_code, 200)
		# Update
		response = self.client.patch(f"/api/v1/invitations/{inv_id}/", {"accepted": True})
		self.assertEqual(response.status_code, 200)
		# Delete
		response = self.client.delete(f"/api/v1/invitations/{inv_id}/")
		self.assertEqual(response.status_code, 204)

class AuditLogEndpointTests(APITestCase):
	def setUp(self):
		self.plan = Plan.objects.create(plan_name="Test Plan", price=0)
		self.user = User.objects.create_user(email="testaudit@example.com", password="testpass", plan=self.plan)
		self.client.force_authenticate(user=self.user)

	def test_auditlog_crud(self):
		# Create
		response = self.client.post("/api/v1/audit-logs/", {"action": "test", "user": self.user.id, "details": "details"})
		self.assertEqual(response.status_code, 201)
		log_id = response.data["id"]
		# Read
		response = self.client.get(f"/api/v1/audit-logs/{log_id}/")
		self.assertEqual(response.status_code, 200)
		# Update
		response = self.client.patch(f"/api/v1/audit-logs/{log_id}/", {"details": "updated details"})
		self.assertEqual(response.status_code, 200)
		# Delete
		response = self.client.delete(f"/api/v1/audit-logs/{log_id}/")
		self.assertEqual(response.status_code, 204)
