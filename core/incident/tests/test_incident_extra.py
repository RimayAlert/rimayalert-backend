import secrets
from unittest.mock import patch

from django.contrib.gis.geos import Point
from django.test import TestCase
from django.utils import timezone
from firebase_admin import messaging

from core.authentication.models import FCMToken
from core.authentication.models import User
from core.incident.models import Incident, IncidentType, IncidentStatus
from core.incident.utils.FCM_notification import FCMNotificationUtils


class IncidentExtraTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.pwd = secrets.token_urlsafe(32)
        cls.user = User.objects.create_user(
            username="extra",
            email="extra@test.com",
            password=cls.pwd,
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


class TestFCMNotificationUtils:

    # -------------------------------
    # Caso 1: No hay usuarios
    # -------------------------------
    def test_send_notification_no_users(self, caplog):
        caplog.clear()

        result = FCMNotificationUtils.send_notification_to_users(
            users=[], title="X", body="Y"
        )

        assert result == {"success": 0, "failed": 0}
        assert "No hay usuarios" in caplog.text

    # -------------------------------
    # Caso 2: Usuarios sin tokens
    # -------------------------------
    def test_send_notification_no_tokens(self, django_user_model, caplog):
        user = django_user_model.objects.create(username="test")

        result = FCMNotificationUtils.send_notification_to_users(
            users=[user], title="X", body="Y"
        )

        assert result == {"success": 0, "failed": 0}
        assert "No se encontraron tokens FCM" in caplog.text

    # -------------------------------
    # Caso 3: Envío exitoso para varios tokens
    # -------------------------------
    @patch("firebase_admin.messaging.send")
    def test_send_notification_success(self, mock_send, django_user_model):
        mock_send.return_value = "msg-id-123"

        user = django_user_model.objects.create(username="test")
        FCMToken.objects.create(user=user, token="TOKEN1", is_active=True)
        FCMToken.objects.create(user=user, token="TOKEN2", is_active=True)

        result = FCMNotificationUtils.send_notification_to_users(
            users=[user], title="Hola", body="Mensaje"
        )

        assert result["success"] == 2
        assert result["failed"] == 0
        assert result["invalid_tokens"] == []
        assert mock_send.call_count == 2

    # -------------------------------
    # Caso 4: Token inválido (UnregisteredError)
    # -------------------------------
    @patch("firebase_admin.messaging.send")
    def test_send_notification_invalid_token(self, mock_send, django_user_model):
        class FakeUnregistered(messaging.UnregisteredError):
            pass

        mock_send.side_effect = FakeUnregistered("invalid")

        user = django_user_model.objects.create(username="test")
        token = FCMToken.objects.create(user=user, token="BADTOKEN", is_active=True)

        result = FCMNotificationUtils.send_notification_to_users(
            users=[user], title="Hola", body="Mensaje"
        )

        token.refresh_from_db()

        assert result["success"] == 0
        assert result["failed"] == 1
        assert result["invalid_tokens"] == ["BADTOKEN"]
        assert token.is_active is False  # Se desactivó el token

    # -------------------------------
    # Caso 5: Error general
    # -------------------------------
    @patch("firebase_admin.messaging.send")
    def test_send_notification_exception(self, mock_send, django_user_model, caplog):
        mock_send.side_effect = Exception("Boom")

        user = django_user_model.objects.create(username="test")
        FCMToken.objects.create(user=user, token="TOKEN1", is_active=True)

        result = FCMNotificationUtils.send_notification_to_users(
            users=[user], title="Hola", body="Mensaje"
        )

        assert result["success"] == 0
        assert result["failed"] == 1
        assert "Error al enviar notificación" in caplog.text

    # -------------------------------
    # Caso 6: Llamar send_notification_to_tokens sin tokens
    # -------------------------------
    def test_send_notification_to_tokens_empty(self):
        result = FCMNotificationUtils.send_notification_to_tokens(
            tokens=[], title="X", body="Y"
        )

        assert result == {"success": 0, "failed": 0, "invalid_tokens": []}
