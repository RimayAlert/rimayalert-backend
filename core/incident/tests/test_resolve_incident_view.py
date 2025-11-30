"""
Tests for ResolveIncidentView.

Este módulo contiene pruebas unitarias para la vista ResolveIncidentView,
que permite marcar incidentes como resueltos y actualizar las estadísticas del usuario.
"""

import secrets
from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone
from django.contrib.gis.geos import Point

from core.authentication.models import User
from core.incident.models import Incident, IncidentType, IncidentStatus
from core.stats.models import UserStats


class ResolveIncidentViewTest(TestCase):
    """Pruebas para ResolveIncidentView."""

    @classmethod
    def setUpTestData(cls):
        """Configuración inicial de datos para las pruebas."""
        password = secrets.token_urlsafe(32)
        cls.user = User.objects.create_user(
            username='testuser',
            password=password,
            email='test@example.com',
            dni='1234567890'
        )

        cls.incident_type = IncidentType.objects.create(
            name='Robo',
            code='ROBO_01'
        )

        # Estado inicial del incidente
        cls.status_reported = IncidentStatus.objects.create(
            name='Reportado',
            code='001'
        )

        # Estado correcto para "resuelto"
        cls.status_resolved = IncidentStatus.objects.create(
            name='Resuelto',
            code='003'
        )

    def setUp(self):
        """Configuración antes de cada prueba."""
        self.client = Client()

        # Crear incidente base
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

        # Crear UserStats iniciales
        self.stats = UserStats.objects.create(
            user=self.user,
            total_alerts=5,
            total_alerts_resolved=2,
            total_alerts_pending=3
        )

    # ---------------------------------------------------------
    # TESTS PRINCIPALES
    # ---------------------------------------------------------

    def test_resolve_incident_success(self):
        """El incidente debe actualizarse al estado 'Resuelto'."""
        url = reverse('incident:resolve_incident', kwargs={'pk': self.incident.pk})
        response = self.client.post(url)

        self.assertEqual(response.status_code, 302)

        self.incident.refresh_from_db()
        self.assertEqual(self.incident.incident_status, self.status_resolved)

    def test_resolve_incident_updates_stats(self):
        """Las estadísticas deben actualizarse correctamente."""
        url = reverse('incident:resolve_incident', kwargs={'pk': self.incident.pk})
        self.client.post(url)

        self.stats.refresh_from_db()
        self.assertEqual(self.stats.total_alerts_pending, 2)  # 3 - 1
        self.assertEqual(self.stats.total_alerts_resolved, 3)  # 2 + 1
        self.assertEqual(self.stats.total_alerts, 5)

    def test_resolve_incident_redirects_to_list(self):
        """Después de resolver debe redirigir a la lista."""
        url = reverse('incident:resolve_incident', kwargs={'pk': self.incident.pk})
        response = self.client.post(url)

        self.assertRedirects(response, reverse('incident:incident_list'))

    def test_resolve_incident_shows_success_message(self):
        """Debe mostrar mensaje de éxito."""
        url = reverse('incident:resolve_incident', kwargs={'pk': self.incident.pk})
        response = self.client.post(url, follow=True)

        messages = list(response.context['messages'])
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), 'Incidente marcado como resuelto exitosamente.')

    # ---------------------------------------------------------
    # ERRORES Y CASOS ESPECIALES
    # ---------------------------------------------------------

    def test_resolve_incident_not_found(self):
        """Debe devolver 404 si el incidente no existe."""
        url = reverse('incident:resolve_incident', kwargs={'pk': 9999})
        response = self.client.post(url)
        self.assertEqual(response.status_code, 404)

    def test_resolve_incident_with_code_003(self):
        """Debe usar el estado con código '003' si existe."""
        url = reverse('incident:resolve_incident', kwargs={'pk': self.incident.pk})
        self.client.post(url)

        self.incident.refresh_from_db()
        self.assertEqual(self.incident.incident_status.code, '003')
        self.assertEqual(self.incident.incident_status.name, 'Resuelto')

    def test_resolve_incident_with_name_resuelto_fallback(self):
        """Si no existe código '003', debe usar nombre 'Resuelto'."""
        # Eliminar estado con código 003
        self.status_resolved.delete()

        # Crear otro estado con nombre "Resuelto"
        fallback_status = IncidentStatus.objects.create(
            name='Resuelto',
            code='XYZ_01'
        )

        url = reverse('incident:resolve_incident', kwargs={'pk': self.incident.pk})
        self.client.post(url)

        self.incident.refresh_from_db()
        self.assertEqual(self.incident.incident_status, fallback_status)

    def test_resolve_incident_creates_stats_if_not_exists(self):
        """Debe crear stats si no existen."""
        self.stats.delete()

        url = reverse('incident:resolve_incident', kwargs={'pk': self.incident.pk})
        self.client.post(url)

        stats = UserStats.objects.get(user=self.user)

        self.assertEqual(stats.total_alerts_pending, 0)
        self.assertEqual(stats.total_alerts_resolved, 1)

    def test_resolve_incident_only_accepts_post(self):
        """GET debe ser rechazado con 405."""
        url = reverse('incident:resolve_incident', kwargs={'pk': self.incident.pk})
        response = self.client.get(url)

        self.assertEqual(response.status_code, 405)

    def test_resolve_incident_multiple_times(self):
        """Resolver múltiples veces debe afectar stats correctamente."""
        url = reverse('incident:resolve_incident', kwargs={'pk': self.incident.pk})

        # 1ra resolución
        self.client.post(url)
        self.stats.refresh_from_db()

        first_pending = self.stats.total_alerts_pending
        first_resolved = self.stats.total_alerts_resolved

        # 2da resolución
        self.client.post(url)
        self.stats.refresh_from_db()

        self.assertEqual(self.stats.total_alerts_pending, max(0, first_pending - 1))
        self.assertEqual(self.stats.total_alerts_resolved, first_resolved + 1)
