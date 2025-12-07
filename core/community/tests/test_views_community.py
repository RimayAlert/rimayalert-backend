import secrets
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib.gis.geos import Polygon

from core.community.models import Community, CommunityMembership

User = get_user_model()


class CommunityViewsTests(TestCase):
    def setUp(self):
        self.password_admin = secrets.token_urlsafe(32)
        self.admin = User.objects.create(username='admin_user', email='admin@example.com', dni=secrets.token_urlsafe(16))
        self.admin.set_password(self.password_admin)
        self.admin.save()

        self.password_member = secrets.token_urlsafe(32)
        self.member = User.objects.create(username='member_user', email='member@example.com', dni=secrets.token_urlsafe(16))
        self.member.set_password(self.password_member)
        self.member.save()

        polygon = Polygon((
            (-10.0, -10.0),
            (-10.0, 10.0),
            (10.0, 10.0),
            (10.0, -10.0),
            (-10.0, -10.0),
        ), srid=4326)
        self.community = Community.objects.create(
            name='Comunidad Vista',
            description='Testing vistas',
            boundary_area=polygon,
            postal_code='12345'
        )

        # Crear membresías
        self.admin_membership = CommunityMembership.objects.create(
            user=self.admin, community=self.community, role='admin', is_verified=True
        )
        self.member_membership = CommunityMembership.objects.create(
            user=self.member, community=self.community, role='member', is_verified=False
        )

    def test_community_detail_view_requires_login(self):
        url = reverse('community:community_detail')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)  # redirect to login
        self.assertIn('/login', response.url.lower())

    def test_community_detail_view_shows_community(self):
        self.client.login(username='admin_user', password=self.password_admin)
        url = reverse('community:community_detail')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertIsNotNone(response.context)
        community = response.context.get('community')
        self.assertIsNotNone(community)
        self.assertEqual(community.id, self.community.id)

    def test_community_members_list_requires_login(self):
        url = reverse('community:community_members')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)

    def test_community_members_list_shows_members(self):
        self.client.login(username='admin_user', password=self.password_admin)
        url = reverse('community:community_members')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        items = response.context.get('items')
        self.assertIsNotNone(items)
        usernames = {m.user.username for m in items}
        self.assertIn(self.admin.username, usernames)
        self.assertIn(self.member.username, usernames)

    def test_verify_member_requires_login(self):
        url = reverse('community:verify_member', args=[self.member_membership.id])
        response = self.client.post(url)
        self.assertEqual(response.status_code, 302)

    def test_verify_member_requires_admin_or_moderator(self):
        self.client.login(username='member_user', password=self.password_member)
        url = reverse('community:verify_member', args=[self.member_membership.id])
        response = self.client.post(url)
        self.member_membership.refresh_from_db()
        self.assertFalse(self.member_membership.is_verified)

    def test_admin_can_toggle_verification(self):
        self.client.login(username='admin_user', password=self.password_admin)
        url = reverse('community:verify_member', args=[self.member_membership.id])
        response = self.client.post(url)
        self.assertEqual(response.status_code, 302)
        self.member_membership.refresh_from_db()
        self.assertTrue(self.member_membership.is_verified)
        response = self.client.post(url)
        self.member_membership.refresh_from_db()
        self.assertFalse(self.member_membership.is_verified)

    def test_verify_member_other_community_blocked(self):
        other_polygon = Polygon((
            (-20.0, -20.0),
            (-20.0, 20.0),
            (20.0, 20.0),
            (20.0, -20.0),
            (-20.0, -20.0),
        ), srid=4326)
        other_community = Community.objects.create(
            name='Otra Comunidad', boundary_area=other_polygon, postal_code='99999'
        )
        other_member_password = secrets.token_urlsafe(32)
        other_user = User.objects.create(username='other_user', email='other@example.com', dni=secrets.token_urlsafe(16))
        other_user.set_password(other_member_password)
        other_user.save()
        other_membership = CommunityMembership.objects.create(
            user=other_user, community=other_community, role='member'
        )

        self.client.login(username='admin_user', password=self.password_admin)
        url = reverse('community:verify_member', args=[other_membership.id])
        response = self.client.post(url)
        other_membership.refresh_from_db()
        self.assertFalse(other_membership.is_verified)
