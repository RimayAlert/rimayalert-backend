import json
import secrets
from unittest.mock import patch, MagicMock
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIRequestFactory, force_authenticate
from rest_framework import status

from core.incident.api.incident.views.incident import RegisterIncidentApiView
from core.incident.models import Incident

User = get_user_model()


class RegisterIncidentApiViewTest(TestCase):
    """Pruebas unitarias para RegisterIncidentApiView"""

    def setUp(self):
        """Configuración inicial para las pruebas"""
        self.factory = APIRequestFactory()
        self.view = RegisterIncidentApiView.as_view()

        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password=secrets.token_urlsafe(32)
        )

        self.incident_data = {
            'type': 'Robo',
            'description': 'Choque en la intersección',
            'location': 'Av. Principal y Calle 5',
            'latitude': -12.0464,
            'longitude': -77.0428
        }

    def test_post_creates_incident_successfully(self):
        """Prueba que se crea un incidente exitosamente"""
        data = {
            'data': json.dumps(self.incident_data)
        }

        request = self.factory.post('/api/incident/register/', data, format='json')
        force_authenticate(request, user=self.user)

        response = self.view(request)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('message', response.data)
        self.assertIn('incident_id', response.data)
        self.assertEqual(response.data['message'], 'Incidente registrado exitosamente')

    def test_post_with_image_creates_incident_with_media(self):
        """Prueba creación de incidente con imagen"""
        mock_image = MagicMock()
        mock_image.name = 'test_image.jpg'
        mock_image.size = 1024

        data = {
            'data': json.dumps(self.incident_data),
            'image': mock_image
        }

        request = self.factory.post('/api/incident/register/', data, format='multipart')
        force_authenticate(request, user=self.user)

        with patch('core.incident.api.incident.views.incident.CreateIncidentFeature') as mock_feature:
            mock_incident = MagicMock()
            mock_incident.id = 1
            mock_feature.return_value.save_incident.return_value = mock_incident

            response = self.view(request)

            self.assertEqual(response.status_code, status.HTTP_201_CREATED)
            # Verificar que se pasó la imagen al feature
            mock_feature.assert_called_once()
            call_kwargs = mock_feature.call_args[1]
            self.assertIsNotNone(call_kwargs['image_file'])

    def test_post_without_data_field_returns_400(self):
        """Prueba que retorna 400 cuando falta el campo 'data'"""
        request = self.factory.post('/api/incident/register/', {}, format='json')
        force_authenticate(request, user=self.user)

        response = self.view(request)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
        self.assertEqual(response.data['error'], 'Campo "data" es requerido')

    def test_post_with_empty_data_field_returns_400(self):
        """Prueba que retorna 400 cuando el campo 'data' está vacío"""
        data = {'data': ''}

        request = self.factory.post('/api/incident/register/', data, format='json')
        force_authenticate(request, user=self.user)

        response = self.view(request)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)

    def test_post_with_invalid_json_returns_500(self):
        """Prueba que retorna 500 cuando el JSON es inválido"""
        data = {
            'data': 'invalid json string'
        }

        request = self.factory.post('/api/incident/register/', data, format='json')
        force_authenticate(request, user=self.user)

        response = self.view(request)

        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
        self.assertIn('error', response.data)

    @patch('core.incident.api.incident.views.incident.logger')
    def test_post_logs_received_data(self, mock_logger):
        """Prueba que registra los datos recibidos en el log"""
        data = {
            'data': json.dumps(self.incident_data)
        }

        request = self.factory.post('/api/incident/register/', data, format='json')
        force_authenticate(request, user=self.user)

        response = self.view(request)

        # Verificar que se llamó logger.info
        self.assertTrue(mock_logger.info.called)

    @patch('core.incident.api.incident.views.incident.logger')
    def test_post_logs_image_received(self, mock_logger):
        """Prueba que registra cuando se recibe una imagen"""
        mock_image = MagicMock()
        mock_image.name = 'test_image.jpg'
        mock_image.size = 2048

        data = {
            'data': json.dumps(self.incident_data),
            'image': mock_image
        }

        request = self.factory.post('/api/incident/register/', data, format='multipart')
        force_authenticate(request, user=self.user)

        with patch('core.incident.api.incident.views.incident.CreateIncidentFeature') as mock_feature:
            mock_incident = MagicMock()
            mock_incident.id = 1
            mock_feature.return_value.save_incident.return_value = mock_incident

            response = self.view(request)

            # Verificar que se registró la información de la imagen
            info_calls = [call[0][0] for call in mock_logger.info.call_args_list]
            self.assertTrue(any('Imagen recibida' in str(call) for call in info_calls))

    @patch('core.incident.api.incident.views.incident.logger')
    def test_post_logs_no_image_received(self, mock_logger):
        """Prueba que registra cuando NO se recibe una imagen"""
        data = {
            'data': json.dumps(self.incident_data)
        }

        request = self.factory.post('/api/incident/register/', data, format='json')
        force_authenticate(request, user=self.user)

        response = self.view(request)

        # Verificar que se registró que no hay imagen
        info_calls = [call[0][0] for call in mock_logger.info.call_args_list]
        self.assertTrue(any('No se recibió imagen' in str(call) for call in info_calls))

    @patch('core.incident.api.incident.views.incident.CreateIncidentFeature')
    def test_post_handles_feature_exception(self, mock_feature):
        """Prueba el manejo de excepciones del feature"""
        mock_feature.return_value.save_incident.side_effect = Exception('Error de prueba')

        data = {
            'data': json.dumps(self.incident_data)
        }

        request = self.factory.post('/api/incident/register/', data, format='json')
        force_authenticate(request, user=self.user)

        response = self.view(request)

        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
        self.assertIn('error', response.data)
        self.assertIn('Error al registrar incidente', response.data['error'])

    @patch('core.incident.api.incident.views.incident.logger')
    @patch('core.incident.api.incident.views.incident.CreateIncidentFeature')
    def test_post_logs_error_on_exception(self, mock_feature, mock_logger):
        """Prueba que registra errores cuando ocurre una excepción"""
        mock_feature.return_value.save_incident.side_effect = Exception('Error de prueba')

        data = {
            'data': json.dumps(self.incident_data)
        }

        request = self.factory.post('/api/incident/register/', data, format='json')
        force_authenticate(request, user=self.user)

        response = self.view(request)

        # Verificar que se llamó logger.error
        self.assertTrue(mock_logger.error.called)

    def test_view_requires_authentication(self):
        """Prueba que la vista requiere autenticación"""
        view_instance = RegisterIncidentApiView()

        # Verificar que tiene la permission class
        from rest_framework.permissions import IsAuthenticated
        self.assertIn(IsAuthenticated, view_instance.permission_classes)

    @patch('core.incident.api.incident.views.incident.CreateIncidentFeature')
    def test_post_passes_correct_data_to_feature(self, mock_feature):
        """Prueba que se pasan los datos correctos al feature"""
        mock_incident = MagicMock()
        mock_incident.id = 123
        mock_feature.return_value.save_incident.return_value = mock_incident

        data = {
            'data': json.dumps(self.incident_data)
        }

        request = self.factory.post('/api/incident/register/', data, format='json')
        force_authenticate(request, user=self.user)

        response = self.view(request)

        # Verificar que CreateIncidentFeature fue llamado con los parámetros correctos
        mock_feature.assert_called_once()
        call_kwargs = mock_feature.call_args[1]
        self.assertEqual(call_kwargs['data'], self.incident_data)
        self.assertEqual(call_kwargs['user'], self.user)

    def test_post_returns_correct_incident_id(self):
        """Prueba que retorna el ID correcto del incidente creado"""
        data = {
            'data': json.dumps(self.incident_data)
        }

        request = self.factory.post('/api/incident/register/', data, format='json')
        force_authenticate(request, user=self.user)

        response = self.view(request)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Verificar que existe un incidente con ese ID
        incident_id = response.data['incident_id']
        incident_exists = Incident.objects.filter(id=incident_id).exists()
        self.assertTrue(incident_exists)

    @patch('core.incident.api.incident.views.incident.logger')
    def test_post_logs_warning_when_no_data_field(self, mock_logger):
        """Prueba que registra un warning cuando falta el campo data"""
        request = self.factory.post('/api/incident/register/', {}, format='json')
        force_authenticate(request, user=self.user)

        response = self.view(request)

        # Verificar que se llamó logger.warning
        self.assertTrue(mock_logger.warning.called)
        warning_message = mock_logger.warning.call_args[0][0]
        self.assertIn('No se recibió campo', warning_message)

    def test_post_with_image_in_files(self):
        """Prueba que maneja la imagen cuando viene en request.FILES"""
        mock_image = MagicMock()
        mock_image.name = 'test_image.jpg'
        mock_image.size = 1024

        data = {
            'data': json.dumps(self.incident_data)
        }

        request = self.factory.post('/api/incident/register/', data, format='multipart')
        force_authenticate(request, user=self.user)
        request.FILES['image'] = mock_image

        with patch('core.incident.api.incident.views.incident.CreateIncidentFeature') as mock_feature:
            mock_incident = MagicMock()
            mock_incident.id = 1
            mock_feature.return_value.save_incident.return_value = mock_incident

            response = self.view(request)

            self.assertEqual(response.status_code, status.HTTP_201_CREATED)

