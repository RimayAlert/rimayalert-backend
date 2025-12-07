import secrets
from unittest.mock import patch, MagicMock
from uuid import uuid4

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from core.authentication.models import User


class UpdateFCMTokenApiViewTest(APITestCase):
    def setUp(self):
        self.password = secrets.token_urlsafe(16)
        self.user = User.objects.create_user(
            username='tester',
            password=secrets.token_urlsafe(32),
            email='tester@test.com',
            dni=str(uuid4())
        )
        self.client.force_authenticate(user=self.user)
        self.url = reverse('authentication:api_update_fcm_token')

    @patch('core.authentication.api.register.views.fcm_token.RegisterFCMTokenFeature')
    def test_update_fcm_token_success(self, mock_feature_class):
        mock_feature = MagicMock()
        mock_feature.register_or_update_token.return_value = True
        mock_feature_class.return_value = mock_feature

        payload = {
            "fcm_token": "dummy_token",
            "device_id": "device123"
        }
        with patch(
                'core.authentication.api.register.views.fcm_token.UpdateFCMTokenSerializer') as mock_serializer_class:
            mock_serializer = MagicMock()
            mock_serializer.is_valid.return_value = True
            mock_serializer.validated_data = payload
            mock_serializer_class.return_value = mock_serializer

            response = self.client.post(self.url, data=payload, format='json')
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertIn('message', response.data)

    @patch('core.authentication.api.register.views.fcm_token.RegisterFCMTokenFeature')
    def test_update_fcm_token_error(self, mock_feature_class):
        mock_feature = MagicMock()
        mock_feature.register_or_update_token.return_value = False
        mock_feature_class.return_value = mock_feature

        payload = {
            "fcm_token": "dummy_token",
            "device_id": "device123"
        }
        with patch(
                'core.authentication.api.register.views.fcm_token.UpdateFCMTokenSerializer') as mock_serializer_class:
            mock_serializer = MagicMock()
            mock_serializer.is_valid.return_value = True
            mock_serializer.validated_data = payload
            mock_serializer_class.return_value = mock_serializer

            response = self.client.post(self.url, data=payload, format='json')
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            self.assertIn('error', response.data)

    @patch('core.authentication.api.register.views.fcm_token.logger')
    @patch('core.authentication.api.register.views.fcm_token.UpdateFCMTokenSerializer')
    def test_update_fcm_token_internal_error(self, mock_serializer_class, mock_logger):
        mock_serializer = MagicMock()
        mock_serializer.is_valid.side_effect = Exception("Internal error")
        mock_serializer_class.return_value = mock_serializer

        payload = {
            "fcm_token": "dummy_token",
            "device_id": "device123"
        }
        response = self.client.post(self.url, data=payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
        self.assertIn('error', response.data)
        self.assertTrue(mock_logger.error.called)
