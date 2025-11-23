import json
import secrets
from unittest.mock import patch

from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta
from django.contrib.gis.geos import Point
from rest_framework.test import APITestCase

from core.authentication.models import User
from core.community.models import Community
from core.incident.models import (
    Incident,
    IncidentType,
    IncidentStatus,
)


class IncidentListViewTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        password = secrets.token_urlsafe(32)
        cls.user = User.objects.create_user(
            username='testuser',
            password=password,
            email='test@example.com',
            dni='1234567890'
        )

        cls.community = Community.objects.create(
            name='Test Community',
            description='Test community description'
        )

        cls.incident_type_1 = IncidentType.objects.create(
            name='Robo',
            code='ROBO_01'
        )
        cls.incident_type_2 = IncidentType.objects.create(
            name='Accidente',
            code='ACC_01'
        )

        cls.status_open = IncidentStatus.objects.create(
            name='Abierto',
            code='OPEN_01'
        )
        cls.status_closed = IncidentStatus.objects.create(
            name='Cerrado',
            code='CLOSED_01'
        )

        now = timezone.now()
        cls.incident_1 = Incident.objects.create(
            reported_by_user=cls.user,
            incident_type=cls.incident_type_1,
            incident_status=cls.status_open,
            title='Incidente de Robo 1',
            description='Descripción del robo 1',
            location=Point(0.0, 0.0, srid=4326),
            address='Calle Principal 123',
            severity_level=5,
            occurred_at=now - timedelta(hours=2),
            reported_at=now
        )

        cls.incident_2 = Incident.objects.create(
            reported_by_user=cls.user,
            incident_type=cls.incident_type_2,
            incident_status=cls.status_closed,
            title='Incidente de Accidente 1',
            description='Descripción del accidente 1',
            location=Point(0.1, 0.1, srid=4326),
            address='Calle Secundaria 456',
            severity_level=3,
            occurred_at=now - timedelta(hours=5),
            reported_at=now
        )

        cls.incident_3 = Incident.objects.create(
            reported_by_user=cls.user,
            incident_type=cls.incident_type_1,
            incident_status=cls.status_closed,
            title='Incidente de Robo 2',
            description='Descripción del robo 2',
            location=Point(0.2, 0.2, srid=4326),
            address='Calle Terciaria 789',
            severity_level=7,
            occurred_at=now - timedelta(hours=10),
            reported_at=now
        )

    def setUp(self):
        self.client = Client()
        self.url = reverse('incident:incident_list')

    def test_incident_list_view_status_code(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_incident_list_view_template_used(self):
        response = self.client.get(self.url)
        self.assertTemplateUsed(response, 'incident/list/incident_list.html')

    def test_incident_list_view_context_name(self):
        response = self.client.get(self.url)
        self.assertIn('items', response.context)

    def test_incident_list_view_all_incidents_displayed(self):
        response = self.client.get(self.url)
        items = list(response.context['items'])
        self.assertEqual(len(items), 3)

    def test_incident_list_view_filter_by_type(self):
        response = self.client.get(self.url, {'type': self.incident_type_1.id})
        items = list(response.context['items'])
        self.assertEqual(len(items), 2)
        self.assertTrue(all(item.incident_type == self.incident_type_1 for item in items))

    def test_incident_list_view_filter_by_status(self):
        response = self.client.get(self.url, {'status': self.status_open.id})
        items = list(response.context['items'])
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0].incident_status, self.status_open)

    def test_incident_list_view_filter_by_type_and_status(self):
        response = self.client.get(self.url, {
            'type': self.incident_type_1.id,
            'status': self.status_closed.id
        })
        items = list(response.context['items'])
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0], self.incident_3)

    def test_incident_list_view_invalid_filter_no_results(self):
        incident_type_empty = IncidentType.objects.create(name='Vandalismo', code='VAND_01')
        response = self.client.get(self.url, {'type': incident_type_empty.id})
        items = list(response.context['items'])
        self.assertEqual(len(items), 0)

    def test_incident_list_view_search_form_in_context(self):
        response = self.client.get(self.url)
        self.assertIn('search_form', response.context)
        self.assertIsNotNone(response.context['search_form'])

    def test_incident_list_view_prefetch_related(self):
        with self.assertNumQueries(6):
            response = self.client.get(self.url)
            list(response.context['items'])


class IncidentDetailViewTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        password = secrets.token_urlsafe(32)
        cls.user = User.objects.create_user(
            username='detailuser',
            password=password,
            email='detail@example.com',
            dni='0987654321'
        )

        cls.community = Community.objects.create(
            name='Detail Community',
            description='Detail community description'
        )

        cls.incident_type = IncidentType.objects.create(
            name='Emergencia Médica',
            code='EMERG_MED_01'
        )
        cls.status = IncidentStatus.objects.create(
            name='En Progreso',
            code='PROGRESS_01'
        )

        now = timezone.now()
        cls.incident = Incident.objects.create(
            reported_by_user=cls.user,
            incident_type=cls.incident_type,
            incident_status=cls.status,
            title='Emergencia Médica Test',
            description='Descripción de la emergencia médica',
            location=Point(-73.2, 5.5, srid=4326),
            address='Hospital Central, Cra 50 #10-50',
            severity_level=9,
            occurred_at=now - timedelta(hours=1),
            reported_at=now
        )

    def setUp(self):
        self.client = Client()
        self.url = reverse('incident:incident_detail', kwargs={'pk': self.incident.pk})

    def test_incident_detail_view_status_code(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_incident_detail_view_template_used(self):
        response = self.client.get(self.url)
        self.assertTemplateUsed(response, 'incident/detail/incident_detail.html')

    def test_incident_detail_view_context_name(self):
        response = self.client.get(self.url)
        self.assertIn('incident', response.context)

    def test_incident_detail_view_correct_incident(self):
        response = self.client.get(self.url)
        incident = response.context['incident']
        self.assertEqual(incident.id, self.incident.id)
        self.assertEqual(incident.title, self.incident.title)

    def test_incident_detail_view_incident_data(self):
        response = self.client.get(self.url)
        incident = response.context['incident']

        self.assertEqual(incident.title, 'Emergencia Médica Test')
        self.assertEqual(incident.description, 'Descripción de la emergencia médica')
        self.assertEqual(incident.severity_level, 9)
        self.assertFalse(incident.is_anonymous)
        self.assertTrue(incident.is_active)

    def test_incident_detail_view_relationships(self):
        response = self.client.get(self.url)
        incident = response.context['incident']

        self.assertEqual(incident.reported_by_user, self.user)
        self.assertEqual(incident.incident_type, self.incident_type)
        self.assertEqual(incident.incident_status, self.status)

    def test_incident_detail_view_nonexistent_incident(self):
        nonexistent_url = reverse('incident:incident_detail', kwargs={'pk': 9999})
        response = self.client.get(nonexistent_url)
        self.assertEqual(response.status_code, 404)

    def test_incident_detail_view_select_related(self):
        with self.assertNumQueries(1):
            response = self.client.get(self.url)
            incident = response.context['incident']
            _ = incident.reported_by_user.username
            _ = incident.incident_type.name
            _ = incident.incident_status.name


class SearchIncidentFormTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.incident_type = IncidentType.objects.create(name='Asalto', code='ASAL_01')
        cls.incident_status = IncidentStatus.objects.create(name='Reportado', code='REPORT_01')

    def test_search_form_valid_with_no_data(self):
        from core.incident.forms import SearchIncidentForm
        form = SearchIncidentForm(data={})
        self.assertTrue(form.is_valid())

    def test_search_form_valid_with_type_filter(self):
        from core.incident.forms import SearchIncidentForm
        form = SearchIncidentForm(data={'type': self.incident_type.id})
        self.assertTrue(form.is_valid())
        self.assertEqual(
            form.cleaned_data['type'],
            self.incident_type
        )

    def test_search_form_valid_with_status_filter(self):
        from core.incident.forms import SearchIncidentForm
        form = SearchIncidentForm(data={'status': self.incident_status.id})
        self.assertTrue(form.is_valid())
        self.assertEqual(
            form.cleaned_data['status'],
            self.incident_status
        )

    def test_search_form_valid_with_both_filters(self):
        from core.incident.forms import SearchIncidentForm
        form = SearchIncidentForm(data={
            'type': self.incident_type.id,
            'status': self.incident_status.id
        })
        self.assertTrue(form.is_valid())

    def test_search_form_fields_required_false(self):
        from core.incident.forms import SearchIncidentForm
        form = SearchIncidentForm(data={})
        self.assertFalse(form.fields['type'].required)
        self.assertFalse(form.fields['status'].required)


class IncidentModelTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        password = secrets.token_urlsafe(32)
        cls.user = User.objects.create_user(
            username='modeluser',
            password=password,
            email='model@example.com',
            dni='1111111111'
        )
        cls.community = Community.objects.create(
            name='Model Community',
            description='Model community'
        )
        cls.incident_type = IncidentType.objects.create(name='Incendio', code='INCEND_01')
        cls.status = IncidentStatus.objects.create(name='Controlado', code='CONTROL_01')

    def test_incident_creation(self):
        incident = Incident.objects.create(
            reported_by_user=self.user,
            incident_type=self.incident_type,
            incident_status=self.status,
            title='Test Incendio',
            description='Descripción de incendio',
            location=Point(0.0, 0.0, srid=4326),
            occurred_at=timezone.now()
        )
        self.assertIsNotNone(incident.id)
        self.assertEqual(incident.title, 'Test Incendio')

    def test_incident_string_representation(self):
        incident = Incident.objects.create(
            reported_by_user=self.user,
            incident_type=self.incident_type,
            incident_status=self.status,
            title='String Test Incendio',
            description='Description',
            location=Point(0.0, 0.0, srid=4326),
            occurred_at=timezone.now()
        )
        self.assertEqual(str(incident), 'String Test Incendio')

    def test_incident_anonymous_flag(self):
        incident = Incident.objects.create(
            reported_by_user=self.user,
            incident_type=self.incident_type,
            incident_status=self.status,
            title='Anonymous Test',
            description='Description',
            location=Point(0.0, 0.0, srid=4326),
            is_anonymous=True,
            occurred_at=timezone.now()
        )
        self.assertTrue(incident.is_anonymous)

    def test_incident_active_flag_default(self):
        incident = Incident.objects.create(
            reported_by_user=self.user,
            incident_type=self.incident_type,
            incident_status=self.status,
            title='Active Test',
            description='Description',
            location=Point(0.0, 0.0, srid=4326),
            occurred_at=timezone.now()
        )
        self.assertTrue(incident.is_active)

    def test_incident_json_location_field(self):
        incident = Incident.objects.create(
            reported_by_user=self.user,
            incident_type=self.incident_type,
            incident_status=self.status,
            title='Location Test',
            description='Description',
            location=Point(-75.5, 10.5, srid=4326),
            occurred_at=timezone.now()
        )
        self.assertIsNotNone(incident.location)
        self.assertEqual(incident.location.x, -75.5)
        self.assertEqual(incident.location.y, 10.5)

    def test_incident_severity_level_optional(self):
        incident = Incident.objects.create(
            reported_by_user=self.user,
            incident_type=self.incident_type,
            incident_status=self.status,
            title='No Severity Test',
            description='Description',
            location=Point(0.0, 0.0, srid=4326),
            occurred_at=timezone.now()
        )
        self.assertIsNone(incident.severity_level)
