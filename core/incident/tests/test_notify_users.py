import secrets
from unittest.mock import patch, MagicMock
from django.test import TestCase
from django.contrib.auth import get_user_model
from core.incident.models import Incident, IncidentType, IncidentStatus

from core.incident.services.notify_users import NearbyUsersNotifier

User = get_user_model()

class NotifyUsersTest(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(
            username='userone',
            email='one@test.com',
            password=secrets.token_urlsafe(10),
            dni=secrets.token_urlsafe(8),
        )
        self.user2 = User.objects.create_user(
            username='usertwo',
            email='two@test.com',
            password=secrets.token_urlsafe(10),
            dni=secrets.token_urlsafe(8),
        )
        self.incident_type = IncidentType.objects.create(name="Robo", code="robo")
        self.incident_status = IncidentStatus.objects.create(name="Reportado", code="reported")
        self.incident = Incident.objects.create(
            reported_by_user=self.user1,
            incident_type=self.incident_type,
            incident_status=self.incident_status,  # ← aquí resuelves el error
            title="Incidente prueba",
            occurred_at="2025-12-07T12:00:00Z",
        )

    @patch('core.incident.utils.FCM_notification.FCMNotificationUtils.send_notification_to_users')
    @patch('core.incident.utils.location.LocationUtils.get_nearby_users')
    def test_notify_users_sends_notification_success(self, mock_get_nearby_users, mock_send_notification):
        mock_get_nearby_users.return_value = [self.user1, self.user2]
        mock_send_notification.return_value = {
            "success": 2,
            "failed": 0
        }

        notifier = NearbyUsersNotifier()
        notifier.send_notifications(self.incident, latitude="-12.0464", longitude="-77.0428")

        mock_send_notification.assert_called_once()
        args, kwargs = mock_send_notification.call_args
        self.assertIn(self.user1, kwargs['users'])
        self.assertIn(self.user2, kwargs['users'])
        self.assertEqual(kwargs['title'], "🚨 Alerta de Robo Cercano")

    @patch('core.incident.utils.location.LocationUtils.get_nearby_users')
    @patch('core.incident.utils.FCM_notification.FCMNotificationUtils.send_notification_to_users')
    def test_notify_users_handles_no_users(self, mock_send_notification, mock_get_nearby_users):
        mock_get_nearby_users.return_value = []
        notifier = NearbyUsersNotifier()
        notifier.send_notifications(self.incident, latitude="-12.0464", longitude="-77.0428")
        mock_send_notification.assert_not_called()

    @patch('core.incident.utils.location.LocationUtils.get_nearby_users')
    @patch('core.incident.utils.FCM_notification.FCMNotificationUtils.send_notification_to_users')
    def test_notify_users_handles_exception(self, mock_send_notification, mock_get_nearby_users):
        mock_get_nearby_users.side_effect = Exception("Fallo interno")
        notifier = NearbyUsersNotifier()
        with self.assertLogs('core.incident.services.notify_users', level='ERROR'):
            notifier.send_notifications(self.incident, latitude="-12.0464", longitude="-77.0428")