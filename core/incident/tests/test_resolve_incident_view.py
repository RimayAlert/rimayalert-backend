import secrets
from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone
from django.contrib.gis.geos import Point

from core.authentication.models import User
from core.incident.models import Incident, IncidentType, IncidentStatus
from core.stats.models import UserStats


class ResolveIncidentViewTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        password = secrets.token_urlsafe(32)

        cls.user = User.objects.create_user(
            username='testuser',
            password=password,
            email='test@example.com',
            dni='1234567890'
        )

        cls.incident_type = IncidentType.objects.create(name='Robo', code='ROBO_01')

        cls.status_reported = IncidentStatus.objects.create(name='Reportado', code='001')
        cls.status_resolved = IncidentStatus.objects.create(name='Resuelto', code='003')

    def setUp(self):
        self.client = Client()

        self.incident = Incident.objects.create(
            reported_by_user=self.user,
            incident_type=self.incident_type,
            incident_status=self.status_reported,
            title='Incidente de Prueba',
            description='Descripción del incidente',
            location=Point(0.0, 0.0, srid=4326),
            address='Calle Principal 123',
            occurred_at=timezone.now()
        )

        self.stats = UserStats.objects.create(
            user=self.user,
            total_alerts=5,
            total_alerts_resolved=2,
            total_alerts_pending=3
        )

    def test_resolve_incident_success(self):
        url = reverse('incident:resolve_incident', kwargs={'pk': self.incident.pk})
        response = self.client.post(url)

        self.assertEqual(response.status_code, 302)

        self.incident.refresh_from_db()
        self.assertEqual(self.incident.incident_status, self.status_resolved)

    def test_resolve_incident_updates_stats(self):
        url = reverse('incident:resolve_incident', kwargs={'pk': self.incident.pk})
        self.client.post(url)

        self.stats.refresh_from_db()
        self.assertEqual(self.stats.total_alerts_pending, 2)
        self.assertEqual(self.stats.total_alerts_resolved, 3)

    def test_resolve_incident_redirects_to_list(self):
        url = reverse('incident:resolve_incident', kwargs={'pk': self.incident.pk})
        response = self.client.post(url)
        self.assertRedirects(response, reverse('incident:incident_list'))

    def test_resolve_incident_shows_success_message(self):
        url = reverse('incident:resolve_incident', kwargs={'pk': self.incident.pk})
        response = self.client.post(url, follow=True)

        messages = list(response.context['messages'])
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), 'Incidente marcado como resuelto exitosamente.')

    def test_resolve_incident_not_found(self):
        url = reverse('incident:resolve_incident', kwargs={'pk': 9999})
        response = self.client.post(url)
        self.assertEqual(response.status_code, 404)

    def test_resolve_incident_with_code_003(self):
        url = reverse('incident:resolve_incident', kwargs={'pk': self.incident.pk})
        self.client.post(url)
        self.incident.refresh_from_db()
        self.assertEqual(self.incident.incident_status.code, '003')

    def test_resolve_incident_with_name_resuelto_fallback(self):
        self.status_resolved.delete()

        fallback = IncidentStatus.objects.create(name='Resuelto', code='XYZ_01')

        url = reverse('incident:resolve_incident', kwargs={'pk': self.incident.pk})
        self.client.post(url)

        self.incident.refresh_from_db()
        self.assertEqual(self.incident.incident_status, fallback)

    def test_resolve_incident_creates_stats_if_not_exists(self):
        self.stats.delete()

        url = reverse('incident:resolve_incident', kwargs={'pk': self.incident.pk})
        self.client.post(url)

        stats = UserStats.objects.get(user=self.user)
        self.assertEqual(stats.total_alerts_pending, 0)
        self.assertEqual(stats.total_alerts_resolved, 1)

    def test_resolve_incident_only_accepts_post(self):
        url = reverse('incident:resolve_incident', kwargs={'pk': self.incident.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 405)

    def test_resolve_incident_multiple_times(self):
        url = reverse('incident:resolve_incident', kwargs={'pk': self.incident.pk})

        self.client.post(url)
        self.stats.refresh_from_db()

        p1 = self.stats.total_alerts_pending
        r1 = self.stats.total_alerts_resolved

        self.client.post(url)
        self.stats.refresh_from_db()

        self.assertEqual(self.stats.total_alerts_pending, max(0, p1 - 1))
        self.assertEqual(self.stats.total_alerts_resolved, r1 + 1)
