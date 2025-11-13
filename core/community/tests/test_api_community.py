import secrets
from django.contrib.gis.geos import Polygon, Point
from django.urls import reverse, NoReverseMatch
from rest_framework import status
from rest_framework.test import APITestCase
from django.db import IntegrityError

from core.authentication.models import User
from core.community.models import Community, CommunityMembership


class CommunityAPITests(APITestCase):
    def setUp(self):
        # Crear usuario autenticado con dni único
        self.password = secrets.token_urlsafe(32)
        self.user = User.objects.create(username="tester", email="tester@example.com", dni=secrets.token_urlsafe(16))
        self.user.set_password(self.password)
        self.user.save()
        self.client.login(username="tester", password=self.password)

        # Crear comunidad con un polígono simple que contiene el punto (0,0)
        self.polygon = Polygon((
            (-10.0, -10.0),
            (-10.0, 10.0),
            (10.0, 10.0),
            (10.0, -10.0),
            (-10.0, -10.0),
        ), srid=4326)
        self.community = Community.objects.create(
            name="Comunidad Test",
            description="Desc",
            boundary_area=self.polygon,
            postal_code="0000",
            is_active=True,
        )

    # Helpers
    def _url(self, name, fallback):
        try:
            return reverse(name)
        except NoReverseMatch:
            return fallback

    def test_check_community_user_without_membership(self):
        url = self._url('check_community', '/communities/api/community/check')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(response.data['hasCommunity'])
        self.assertIsNone(response.data['community'])

    def test_check_community_user_with_membership(self):
        CommunityMembership.objects.create(user=self.user, community=self.community)
        url = self._url('check_community', '/communities/api/community/check')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['hasCommunity'])
        self.assertIsNotNone(response.data['community'])
        self.assertEqual(response.data['community']['id'], self.community.id)

    def test_assign_community_missing_coordinates(self):
        url = self._url('assign_community', '/communities/api/community/assign')
        response = self.client.post(url, data={})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        # response es Response DRF
        self.assertIn('error', getattr(response, 'data', {}))

    def test_assign_community_not_found(self):
        url = self._url('assign_community', '/communities/api/community/assign')
        # Punto fuera del polígono (50,50)
        data = {"latitude": 50.0, "longitude": 50.0}
        response = self.client.post(url, data=data)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn('error', getattr(response, 'data', {}))

    def test_assign_community_creates_membership(self):
        url = self._url('assign_community', '/communities/api/community/assign')
        data = {"latitude": 0.0, "longitude": 0.0}
        response = self.client.post(url, data=data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['communityId'], self.community.id)
        self.assertTrue(response.data['created'])
        self.assertFalse(response.data['isVerified'])  # por defecto False

    def test_assign_community_existing_membership_returns_200(self):
        # Crear primero la membresía
        point = Point(0.0, 0.0, srid=4326)
        self.assertTrue(self.community.boundary_area.contains(point))
        CommunityMembership.objects.create(user=self.user, community=self.community)
        url = self._url('assign_community', '/communities/api/community/assign')
        data = {"latitude": 0.0, "longitude": 0.0}
        response = self.client.post(url, data=data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(response.data['created'])
        self.assertEqual(response.data['communityId'], self.community.id)

    def test_membership_unique_constraint(self):
        CommunityMembership.objects.create(user=self.user, community=self.community)
        with self.assertRaises(IntegrityError):
            CommunityMembership.objects.create(user=self.user, community=self.community)

    def test_unauthenticated_requests_are_rejected(self):
        self.client.logout()
        check_url = self._url('check_community', '/communities/api/community/check')
        assign_url = self._url('assign_community', '/communities/api/community/assign')
        r1 = self.client.get(check_url)
        r2 = self.client.post(assign_url, data={"latitude": 0.0, "longitude": 0.0})
        self.assertEqual(r1.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(r2.status_code, status.HTTP_401_UNAUTHORIZED)
