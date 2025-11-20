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

        cls.status_reported = IncidentStatus.objects.create(
            name='Reportado',
            code='001'
        )

        cls.status_resolved = IncidentStatus.objects.create(
            name='Resuelto',
            code='003'
        )

    def setUp(self):
        """Configuración antes de cada prueba."""
        self.client = Client()
        
        # Crear incidente de prueba
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
        
        # Crear UserStats para el usuario
        self.stats = UserStats.objects.create(
            user=self.user,
            total_alerts=5,
            total_alerts_resolved=2,
            total_alerts_pending=3
        )

    def test_resolve_incident_success(self):
        """Prueba que el incidente se marca como resuelto exitosamente."""
        url = reverse('incident:resolve_incident', kwargs={'pk': self.incident.pk})
        response = self.client.post(url)
        
        # Verificar redirección
        self.assertEqual(response.status_code, 302)
        
        # Verificar que el incidente cambió de estado
        self.incident.refresh_from_db()
        self.assertEqual(self.incident.incident_status, self.status_resolved)

    def test_resolve_incident_updates_stats(self):
        """Prueba que las estadísticas se actualizan correctamente."""
        url = reverse('incident:resolve_incident', kwargs={'pk': self.incident.pk})
        response = self.client.post(url)
        
        # Verificar que las estadísticas se actualizaron
        self.stats.refresh_from_db()
        self.assertEqual(self.stats.total_alerts_pending, 2)  # 3 - 1
        self.assertEqual(self.stats.total_alerts_resolved, 3)  # 2 + 1
        self.assertEqual(self.stats.total_alerts, 5)  # No debe cambiar

    def test_resolve_incident_redirects_to_list(self):
        """Prueba que redirige a la lista de incidentes después de resolver."""
        url = reverse('incident:resolve_incident', kwargs={'pk': self.incident.pk})
        response = self.client.post(url)
        
        self.assertRedirects(response, reverse('incident:incident_list'))

    def test_resolve_incident_shows_success_message(self):
        """Prueba que muestra un mensaje de éxito."""
        url = reverse('incident:resolve_incident', kwargs={'pk': self.incident.pk})
        response = self.client.post(url, follow=True)
        
        messages = list(response.context['messages'])
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), 'Incidente marcado como resuelto exitosamente.')

    def test_resolve_incident_not_found(self):
        """Prueba que retorna 404 para incidente no existente."""
        url = reverse('incident:resolve_incident', kwargs={'pk': 9999})
        response = self.client.post(url)
        
        self.assertEqual(response.status_code, 404)

    def test_resolve_incident_with_code_003(self):
        """Prueba que usa el estado con código '003' si existe."""
        url = reverse('incident:resolve_incident', kwargs={'pk': self.incident.pk})
        response = self.client.post(url)
        
        self.incident.refresh_from_db()
        self.assertEqual(self.incident.incident_status.code, '003')
        self.assertEqual(self.incident.incident_status.name, 'Resuelto')

    def test_resolve_incident_with_name_resuelto_fallback(self):
        """Prueba que usa el estado con nombre 'Resuelto' como fallback."""
        # Eliminar el estado con código '003'
        self.status_resolved.delete()
        
        # Crear estado con nombre 'Resuelto' pero sin código '003'
        status_resuelto = IncidentStatus.objects.create(
            name='Resuelto',
            code='RESOLVED_01'
        )
        
        url = reverse('incident:resolve_incident', kwargs={'pk': self.incident.pk})
        response = self.client.post(url)
        
        self.incident.refresh_from_db()
        self.assertEqual(self.incident.incident_status.name, 'Resuelto')
        self.assertEqual(self.incident.incident_status, status_resuelto)

    def test_resolve_incident_creates_stats_if_not_exists(self):
        """Prueba que crea UserStats si no existe para el usuario."""
        # Eliminar stats existente
        self.stats.delete()
        
        url = reverse('incident:resolve_incident', kwargs={'pk': self.incident.pk})
        response = self.client.post(url)
        
        # Verificar que se creó UserStats
        self.assertTrue(UserStats.objects.filter(user=self.user).exists())
        stats = UserStats.objects.get(user=self.user)
        self.assertEqual(stats.total_alerts_pending, -1)  # 0 - 1
        self.assertEqual(stats.total_alerts_resolved, 1)  # 0 + 1

    def test_resolve_incident_only_accepts_post(self):
        """Prueba que solo acepta método POST."""
        url = reverse('incident:resolve_incident', kwargs={'pk': self.incident.pk})
        
        # GET no debería funcionar
        response = self.client.get(url)
        self.assertEqual(response.status_code, 405)  # Method Not Allowed

    def test_resolve_incident_multiple_times(self):
        """Prueba resolver el mismo incidente múltiples veces."""
        url = reverse('incident:resolve_incident', kwargs={'pk': self.incident.pk})
        
        # Primera resolución
        response1 = self.client.post(url)
        self.assertEqual(response1.status_code, 302)
        
        self.stats.refresh_from_db()
        pending_after_first = self.stats.total_alerts_pending
        resolved_after_first = self.stats.total_alerts_resolved
        
        # Segunda resolución
        response2 = self.client.post(url)
        self.assertEqual(response2.status_code, 302)
        
        self.stats.refresh_from_db()
        # Las estadísticas deberían cambiar nuevamente
        self.assertEqual(self.stats.total_alerts_pending, pending_after_first - 1)
        self.assertEqual(self.stats.total_alerts_resolved, resolved_after_first + 1)
