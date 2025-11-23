from django.test import TestCase
from django.utils import timezone
from django.contrib.gis.geos import Point
from core.authentication.models import User
from core.community.models import Community
from core.incident.models import Incident, IncidentType, IncidentStatus

class IncidentExtraTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            username="extra",
            email="extra@test.com",
            password="123456",
            dni="1111111111"
        )
        cls.type = IncidentType.objects.create(name="Robo", code="R1")
        cls.status = IncidentStatus.objects.create(name="Abierto", code="S1")

    def test_incident_str_method(self):
        incident = Incident.objects.create(
            reported_by_user=self.user,
            incident_type=self.type,
            incident_status=self.status,
            title="Mi incidente",
            location=Point(1, 1),
            occurred_at=timezone.now()
        )

        self.assertEqual(str(incident), "Mi incidente")
