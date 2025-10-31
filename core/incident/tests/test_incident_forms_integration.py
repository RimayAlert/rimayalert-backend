"""
Tests de integración para los formularios y vistas de incidentes.

Este módulo proporciona pruebas adicionales para la integración entre
formularios y vistas, así como pruebas de cobertura de código.
"""

import secrets
from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta

from core.authentication.models import User
from core.community.models import Community
from core.incident.models import (
    Incident,
    IncidentType,
    IncidentStatus,
)
from core.incident.forms import SearchIncidentForm


class IncidentViewIntegrationTest(TestCase):
    """Pruebas de integración entre vistas y formularios."""

    @classmethod
    def setUpTestData(cls):
        """Configuración inicial de datos para las pruebas."""
        password = secrets.token_urlsafe(32)
        cls.user = User.objects.create_user(
            username='integrationuser',
            password=password,
            email='integration@example.com',
            dni='2222222222'
        )

        cls.community = Community.objects.create(
            name='Integration Community',
            description='Integration test community'
        )

        cls.incident_type_1 = IncidentType.objects.create(name='Hurto', code='HURT_01')
        cls.incident_type_2 = IncidentType.objects.create(name='Violencia', code='VIOL_01')

        cls.status_pending = IncidentStatus.objects.create(name='Pendiente', code='PEND_01')
        cls.status_resolved = IncidentStatus.objects.create(name='Resuelto', code='RESOL_01')

        now = timezone.now()

        # Crear múltiples incidentes para pruebas de paginación y filtrado
        for i in range(5):
            Incident.objects.create(
                reported_by_user=cls.user,
                community=cls.community,
                incident_type=cls.incident_type_1 if i % 2 == 0 else cls.incident_type_2,
                incident_status=cls.status_pending if i % 2 == 0 else cls.status_resolved,
                title=f'Incidente de Prueba {i}',
                description=f'Descripción del incidente {i}',
                latitude=float(i),
                longitude=float(i),
                address=f'Calle Prueba {i}',
                severity_level=i + 1,
                occurred_at=now - timedelta(hours=i),
                reported_at=now
            )

    def setUp(self):
        """Configuración antes de cada prueba."""
        self.client = Client()
        self.list_url = reverse('incident:incident_list')

    def test_integration_filter_form_with_view(self):
        """Verifica la integración del formulario de filtro con la vista."""
        response = self.client.get(self.list_url)
        form = response.context['search_form']

        # Verifica que el formulario está en el contexto
        self.assertIsNotNone(form)
        self.assertIsInstance(form, SearchIncidentForm)

    def test_integration_filtered_query_preserves_form(self):
        """Verifica que los filtros aplicados se preservan en el formulario."""
        response = self.client.get(
            self.list_url,
            {'type': self.incident_type_1.id}
        )
        form = response.context['search_form']

        # Verifica que el formulario mantiene el valor del filtro (como string)
        self.assertEqual(form['type'].value(), str(self.incident_type_1.id))

    def test_integration_multiple_filters_applied(self):
        """Verifica que múltiples filtros se aplican correctamente."""
        response = self.client.get(self.list_url, {
            'type': self.incident_type_1.id,
            'status': self.status_pending.id
        })

        items = list(response.context['items'])
        form = response.context['search_form']

        # Verifica que solo se muestran incidentes que coinciden con ambos filtros
        self.assertTrue(all(
            item.incident_type == self.incident_type_1 and
            item.incident_status == self.status_pending
            for item in items
        ))

    def test_integration_invalid_form_data_ignored(self):
        """Verifica que datos inválidos en el formulario se ignoran."""
        response = self.client.get(self.list_url, {
            'type': 'invalid_type_id'
        })

        # La vista debe manejar datos inválidos graciosamente
        self.assertEqual(response.status_code, 200)

    def test_integration_detail_view_accessible_from_list(self):
        """Verifica que se puede acceder a la vista de detalle desde la lista."""
        response = self.client.get(self.list_url)
        items = response.context['items']

        # Obtener el primer incidente de la lista
        incident = list(items)[0]

        # Intentar acceder a su vista de detalle
        detail_url = reverse('incident:incident_detail', kwargs={'pk': incident.pk})
        detail_response = self.client.get(detail_url)

        self.assertEqual(detail_response.status_code, 200)
        self.assertEqual(detail_response.context['incident'].pk, incident.pk)


class IncidentFormValidationTest(TestCase):
    """Pruebas de validación del formulario SearchIncidentForm."""

    @classmethod
    def setUpTestData(cls):
        """Configuración inicial de datos para las pruebas."""
        cls.incident_type = IncidentType.objects.create(name='Secuestro', code='SECU_01')
        cls.incident_status = IncidentStatus.objects.create(name='Activo', code='ACTIV_01')

    def test_form_accepts_empty_data(self):
        """Verifica que el formulario acepta datos vacíos."""
        form = SearchIncidentForm(data={})
        self.assertTrue(form.is_valid())
        self.assertIsNone(form.cleaned_data['type'])
        self.assertIsNone(form.cleaned_data['status'])

    def test_form_accepts_valid_type_id(self):
        """Verifica que el formulario acepta un ID de tipo válido."""
        form = SearchIncidentForm(data={'type': self.incident_type.id})
        self.assertTrue(form.is_valid())

    def test_form_accepts_valid_status_id(self):
        """Verifica que el formulario acepta un ID de estado válido."""
        form = SearchIncidentForm(data={'status': self.incident_status.id})
        self.assertTrue(form.is_valid())

    def test_form_rejects_invalid_type_id(self):
        """Verifica que el formulario rechaza un ID de tipo inválido."""
        form = SearchIncidentForm(data={'type': 9999})
        self.assertFalse(form.is_valid())

    def test_form_rejects_invalid_status_id(self):
        """Verifica que el formulario rechaza un ID de estado inválido."""
        form = SearchIncidentForm(data={'status': 9999})
        self.assertFalse(form.is_valid())

    def test_form_widget_classes(self):
        """Verifica que los widgets tienen las clases CSS correctas."""
        form = SearchIncidentForm()
        type_widget = form.fields['type'].widget
        status_widget = form.fields['status'].widget

        self.assertIn('form-select', type_widget.attrs['class'])
        self.assertIn('form-select', status_widget.attrs['class'])

    def test_form_field_labels(self):
        """Verifica que los campos tienen las etiquetas correctas."""
        form = SearchIncidentForm()
        self.assertEqual(form.fields['type'].label, 'Tipo de Incidente')
        self.assertEqual(form.fields['status'].label, 'Estado')

    def test_form_empty_labels(self):
        """Verifica que los campos tienen etiquetas vacías opcionales."""
        form = SearchIncidentForm()
        self.assertEqual(form.fields['type'].empty_label, 'Todos los tipos')
        self.assertEqual(form.fields['status'].empty_label, 'Todos los estados')


class IncidentViewQueryOptimizationTest(TestCase):
    """Pruebas de optimización de consultas en las vistas."""

    @classmethod
    def setUpTestData(cls):
        """Configuración inicial de datos para las pruebas."""
        password = secrets.token_urlsafe(32)
        cls.user = User.objects.create_user(
            username='queryuser',
            password=password,
            email='query@example.com',
            dni='3333333333'
        )

        cls.community = Community.objects.create(
            name='Query Community',
            description='Query test'
        )

        cls.incident_type = IncidentType.objects.create(name='Fraude', code='FRAU_01')
        cls.status = IncidentStatus.objects.create(name='Investigando', code='INVES_01')

        # Crear múltiples incidentes
        now = timezone.now()
        for i in range(10):
            Incident.objects.create(
                reported_by_user=cls.user,
                community=cls.community,
                incident_type=cls.incident_type,
                incident_status=cls.status,
                title=f'Query Test {i}',
                description='Test',
                latitude=0.0,
                longitude=0.0,
                occurred_at=now
            )

    def setUp(self):
        """Configuración antes de cada prueba."""
        self.client = Client()

    def test_list_view_uses_prefetch_related(self):
        """Verifica que la vista de lista usa prefetch_related."""
        url = reverse('incident:incident_list')

        # El número de queries debe ser constante sin importar el número de incidentes
        with self.assertNumQueries(6):
            response = self.client.get(url)
            # Iterar sobre todos los items para forzar la evaluación del queryset
            list(response.context['items'])

    def test_detail_view_uses_select_related(self):
        """Verifica que la vista de detalle usa select_related."""
        incident = Incident.objects.first()
        url = reverse('incident:incident_detail', kwargs={'pk': incident.pk})

        with self.assertNumQueries(1):
            response = self.client.get(url)
            # Acceder a todas las relaciones
            incident_obj = response.context['incident']
            _ = incident_obj.reported_by_user.username
            _ = incident_obj.community.name
            _ = incident_obj.incident_type.name
            _ = incident_obj.incident_status.name


class IncidentViewErrorHandlingTest(TestCase):
    """Pruebas de manejo de errores en las vistas."""

    def setUp(self):
        """Configuración antes de cada prueba."""
        self.client = Client()

    def test_detail_view_404_on_nonexistent_incident(self):
        """Verifica que se retorna 404 para un incidente inexistente."""
        url = reverse('incident:incident_detail', kwargs={'pk': 99999})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_list_view_handles_empty_database(self):
        """Verifica que la vista de lista maneja una base de datos vacía."""
        url = reverse('incident:incident_list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        items = list(response.context['items'])
        self.assertEqual(len(items), 0)

    def test_list_view_with_malformed_query_params(self):
        """Verifica que la vista maneja parámetros de consulta malformados."""
        url = reverse('incident:incident_list')
        response = self.client.get(url, {
            'type': 'not_a_number',
            'status': 'also_not_a_number'
        })
        self.assertEqual(response.status_code, 200)


class IncidentRelationshipsTest(TestCase):
    """Pruebas de las relaciones entre modelos."""

    @classmethod
    def setUpTestData(cls):
        """Configuración inicial de datos para las pruebas."""
        password1 = secrets.token_urlsafe(32)
        password2 = secrets.token_urlsafe(32)

        cls.user1 = User.objects.create_user(
            username='reluser1',
            password=password1,
            email='rel1@example.com',
            dni='4444444444'
        )
        cls.user2 = User.objects.create_user(
            username='reluser2',
            password=password2,
            email='rel2@example.com',
            dni='5555555555'
        )

        cls.community1 = Community.objects.create(
            name='Rel Community 1',
            description='Rel test 1'
        )
        cls.community2 = Community.objects.create(
            name='Rel Community 2',
            description='Rel test 2'
        )

        cls.type1 = IncidentType.objects.create(name='Tráfico', code='TRAF_01')
        cls.type2 = IncidentType.objects.create(name='Ambiental', code='AMBI_01')

        cls.status1 = IncidentStatus.objects.create(name='No Resuelto', code='NORESO_01')
        cls.status2 = IncidentStatus.objects.create(name='Escalado', code='ESCAL_01')

    def test_incident_can_belong_to_different_users(self):
        """Verifica que los incidentes pueden pertenecer a diferentes usuarios."""
        incident1 = Incident.objects.create(
            reported_by_user=self.user1,
            community=self.community1,
            incident_type=self.type1,
            incident_status=self.status1,
            title='User 1 Incident',
            description='Test',
            latitude=0.0,
            longitude=0.0,
            occurred_at=timezone.now()
        )

        incident2 = Incident.objects.create(
            reported_by_user=self.user2,
            community=self.community1,
            incident_type=self.type1,
            incident_status=self.status1,
            title='User 2 Incident',
            description='Test',
            latitude=0.0,
            longitude=0.0,
            occurred_at=timezone.now()
        )

        self.assertNotEqual(incident1.reported_by_user, incident2.reported_by_user)

    def test_community_has_multiple_incidents(self):
        """Verifica que una comunidad puede tener múltiples incidentes."""
        for i in range(3):
            Incident.objects.create(
                reported_by_user=self.user1,
                community=self.community1,
                incident_type=self.type1,
                incident_status=self.status1,
                title=f'Community Incident {i}',
                description='Test',
                latitude=0.0,
                longitude=0.0,
                occurred_at=timezone.now()
            )

        community_incidents = Incident.objects.filter(community=self.community1)
        self.assertEqual(community_incidents.count(), 3)

    def test_incident_type_cascade_protect(self):
        """Verifica que el tipo de incidente está protegido contra eliminación."""
        incident = Incident.objects.create(
            reported_by_user=self.user1,
            community=self.community1,
            incident_type=self.type1,
            incident_status=self.status1,
            title='Protected Type Test',
            description='Test',
            latitude=0.0,
            longitude=0.0,
            occurred_at=timezone.now()
        )

        # Intentar eliminar el tipo de incidente debe fallar
        with self.assertRaises(Exception):
            self.type1.delete()

    def test_incident_status_cascade_protect(self):
        """Verifica que el estado de incidente está protegido contra eliminación."""
        incident = Incident.objects.create(
            reported_by_user=self.user1,
            community=self.community1,
            incident_type=self.type1,
            incident_status=self.status1,
            title='Protected Status Test',
            description='Test',
            latitude=0.0,
            longitude=0.0,
            occurred_at=timezone.now()
        )

        # Intentar eliminar el estado de incidente debe fallar
        with self.assertRaises(Exception):
            self.status1.delete()

    def test_user_cascade_delete_incidents(self):
        """Verifica que al eliminar un usuario se eliminan sus incidentes."""
        incident = Incident.objects.create(
            reported_by_user=self.user1,
            community=self.community1,
            incident_type=self.type1,
            incident_status=self.status1,
            title='User Cascade Test',
            description='Test',
            latitude=0.0,
            longitude=0.0,
            occurred_at=timezone.now()
        )

        incident_id = incident.id

        # Eliminar el usuario
        self.user1.delete()

        # Verificar que el incidente fue eliminado
        self.assertFalse(Incident.objects.filter(id=incident_id).exists())

    def test_community_cascade_delete_incidents(self):
        """Verifica que al eliminar una comunidad se eliminan sus incidentes."""
        incident = Incident.objects.create(
            reported_by_user=self.user1,
            community=self.community1,
            incident_type=self.type1,
            incident_status=self.status1,
            title='Community Cascade Test',
            description='Test',
            latitude=0.0,
            longitude=0.0,
            occurred_at=timezone.now()
        )

        incident_id = incident.id

        # Eliminar la comunidad
        self.community1.delete()

        # Verificar que el incidente fue eliminado
        self.assertFalse(Incident.objects.filter(id=incident_id).exists())

