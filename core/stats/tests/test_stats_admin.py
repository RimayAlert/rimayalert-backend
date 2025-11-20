"""
Tests for Stats Admin Registration.

Este módulo contiene pruebas para verificar que los modelos de estadísticas
están correctamente registrados en el Django Admin.
"""

from django.test import TestCase
from django.contrib import admin

from core.stats.models import UserStats


class StatsAdminTest(TestCase):
    """Pruebas para el registro de modelos en Django Admin."""

    def test_user_stats_registered_in_admin(self):
        """Verifica que UserStats está registrado en el Django Admin."""
        self.assertTrue(admin.site.is_registered(UserStats))

    def test_user_stats_admin_site_configuration(self):
        """Verifica que UserStats tiene configuración básica en admin."""
        self.assertIn(UserStats, admin.site._registry)
        
    def test_user_stats_admin_has_model_admin(self):
        """Verifica que UserStats tiene un ModelAdmin asociado."""
        model_admin = admin.site._registry.get(UserStats)
        self.assertIsNotNone(model_admin)
