from django.test import TestCase
from core.incident.api.incident.serializer.map_incident import MapIncidentSerializer

class DummyIncident:
    def __init__(self, id, title, distance, incident_type):
        self.id = id
        self.title = title
        self.distance = distance
        self.incident_type = incident_type

    def to_json_map(self):
        return {
            "id": self.id,
            "title": self.title,
            "distance": self.distance,
            "incident_type": self.incident_type
        }

class MapIncidentSerializerTest(TestCase):

    def test_serialize_data(self):
        obj = DummyIncident(1, "Test", 15.7, "Robo")

        serializer = MapIncidentSerializer(obj)

        self.assertEqual(serializer.data["id"], 1)
        self.assertEqual(serializer.data["title"], "Test")
        self.assertEqual(serializer.data["distance"], 15.7)
        self.assertEqual(serializer.data["incident_type"], "Robo")
