import secrets

from django.contrib.auth import get_user_model
from django.contrib.gis.geos import Polygon
from django.db import IntegrityError
from django.urls import reverse, NoReverseMatch
from rest_framework import status
from rest_framework.test import APITestCase

from core.community.models import CommunityMembership, Community

User = get_user_model()


class CommunityAPITests(APITestCase):
    def setUp(self):
        self.password = secrets.token_urlsafe(32)
        self.user = User.objects.create(
            username="tester",
            email="tester@example.com",
            dni=secrets.token_urlsafe(16)
        )
        self.user.set_password(self.password)
        self.user.save()

        self.client.force_authenticate(user=self.user)

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

    def _url(self, name, fallback):
        try:
            return reverse(name)
        except NoReverseMatch:
            return fallback


    def test_assign_community_missing_coordinates(self):
        url = self._url('assign_community', '/communities/api/community/assign')
        response = self.client.post(url, data={})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('message', getattr(response, 'data', {}))

        response = self.client.post(url, data={'latitude': 0.0})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        response = self.client.post(url, data={'longitude': 0.0})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_assign_community_creates_membership(self):
        url = self._url('assign_community', '/communities/api/community/assign')
        data = {"latitude": 0.0, "longitude": 0.0}

        self.assertFalse(CommunityMembership.objects.filter(user=self.user).exists())

        response = self.client.post(url, data=data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['has_community'])
        self.assertEqual(response.data['community']['id'], self.community.id)
        self.assertEqual(response.data['community']['is_verified'], False)

        self.assertTrue(CommunityMembership.objects.filter(user=self.user, community=self.community).exists())

    def test_assign_community_existing_membership_returns_200(self):
        """Prueba que si ya existe membresía, se devuelve 200 y no se duplica."""
        CommunityMembership.objects.create(user=self.user, community=self.community)
        initial_membership_count = CommunityMembership.objects.count()

        url = self._url('assign_community', '/communities/api/community/assign')
        data = {"latitude": 0.0, "longitude": 0.0}
        response = self.client.post(url, data=data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['has_community'])
        self.assertEqual(response.data['community']['id'], self.community.id)
        self.assertIn("ya pertenece a una comunidad", response.data['message'])

        self.assertEqual(CommunityMembership.objects.count(), initial_membership_count)

    def test_assign_community_creates_new_community_and_membership(self):
        url = self._url('assign_community', '/communities/api/community/assign')
        data = {"latitude": 50.0, "longitude": 50.0}

        initial_community_count = Community.objects.count()

        response = self.client.post(url, data=data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data['has_community'])
        self.assertIn("Usuario asignado a una nueva comunidad", response.data['message'])

        self.assertEqual(Community.objects.count(), initial_community_count + 1)
        new_community = Community.objects.exclude(id=self.community.id).first()
        self.assertIsNotNone(new_community)
        self.assertEqual(response.data['community']['id'], new_community.id)
        self.assertTrue(CommunityMembership.objects.filter(user=self.user, community=new_community).exists())


    def test_membership_unique_constraint(self):
        """Prueba la restricción de unicidad de la membresía directamente en el modelo."""
        CommunityMembership.objects.create(user=self.user, community=self.community)
        with self.assertRaises(IntegrityError):
            CommunityMembership.objects.create(user=self.user, community=self.community)

    def test_unauthenticated_requests_are_rejected(self):
        """Prueba que los usuarios no autenticados no pueden asignar comunidad."""
        self.client.logout()
        assign_url = self._url('assign_community', '/communities/api/community/assign')
        r_post = self.client.post(assign_url, data={"latitude": 0.0, "longitude": 0.0})
        self.assertEqual(r_post.status_code, status.HTTP_401_UNAUTHORIZED)
