import secrets
from unittest.mock import patch, MagicMock
from django.test import TestCase
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.contrib.gis.geos import Point

from core.incident.api.incident.feature.incident import CreateIncidentFeature
from core.incident.models import IncidentType, IncidentMedia

User = get_user_model()


class CreateIncidentFeatureTest(TestCase):

    def setUp(self):
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

    def test_save_incident_creates_incident_successfully(self):
        """Prueba que se crea un incidente correctamente"""
        feature = CreateIncidentFeature(
            data=self.incident_data,
            user=self.user
        )
        
        incident = feature.save_incident()
        
        self.assertIsNotNone(incident)
        self.assertEqual(incident.title, 'Robo')
        self.assertEqual(incident.description, 'Choque en la intersección')
        self.assertEqual(incident.address, 'Av. Principal y Calle 5')
        self.assertIsNotNone(incident.location)
        self.assertIsInstance(incident.location, Point)
        self.assertEqual(incident.location.x, -77.0428)
        self.assertEqual(incident.location.y, -12.0464)
        self.assertEqual(incident.reported_by_user, self.user)
        self.assertTrue(incident.is_anonymous)

    def test_save_incident_creates_new_incident_type(self):
        """Prueba que se crea un nuevo tipo de incidente si no existe"""
        feature = CreateIncidentFeature(
            data=self.incident_data,
            user=self.user
        )
        
        initial_count = IncidentType.objects.count()
        incident = feature.save_incident()
        
        self.assertEqual(IncidentType.objects.count(), initial_count + 1)
        self.assertEqual(incident.incident_type.name, 'Robo')
        self.assertEqual(incident.incident_type.code, 'robo')

    def test_save_incident_reuses_existing_incident_type(self):
        """Prueba que reutiliza un tipo de incidente existente"""
        existing_type = IncidentType.objects.create(
            name='Robo',
            code='robo',
            description='Tipo existente'
        )
        
        feature = CreateIncidentFeature(
            data=self.incident_data,
            user=self.user
        )
        
        initial_count = IncidentType.objects.count()
        incident = feature.save_incident()
        self.assertEqual(IncidentType.objects.count(), initial_count)
        self.assertEqual(incident.incident_type.id, existing_type.id)

    def test_save_incident_creates_or_gets_reported_status(self):
        """Prueba que crea o obtiene el estado 'reported'"""
        feature = CreateIncidentFeature(
            data=self.incident_data,
            user=self.user
        )
        
        incident = feature.save_incident()
        
        self.assertIsNotNone(incident.incident_status)
        self.assertEqual(incident.incident_status.code, 'reported')
        self.assertEqual(incident.incident_status.name, 'Reported')

    @patch('core.incident.api.incident.feature.incident.IncidentMedia.objects.create')
    def test_save_incident_with_image_file(self, mock_media_create):
        """Prueba que guarda la imagen asociada al incidente"""
        mock_image = MagicMock()
        mock_image.name = 'test_image.jpg'
        mock_media = MagicMock()
        mock_media.file.name = 'test_image.jpg'
        mock_media.media_type = 'image'
        mock_media_create.return_value = mock_media

        feature = CreateIncidentFeature(
            data=self.incident_data,
            user=self.user,
            image_file=mock_image
        )
        
        incident = feature.save_incident()
        mock_media_create.assert_called_once()
        call_kwargs = mock_media_create.call_args[1]
        self.assertEqual(call_kwargs['incident'], incident)
        self.assertEqual(call_kwargs['media_type'], 'image')
        self.assertEqual(call_kwargs['file'], mock_image)

    def test_save_incident_without_image_file(self):
        """Prueba que funciona sin archivo de imagen"""
        feature = CreateIncidentFeature(
            data=self.incident_data,
            user=self.user,
            image_file=None
        )
        
        incident = feature.save_incident()
        
        media_count = IncidentMedia.objects.filter(incident=incident).count()
        self.assertEqual(media_count, 0)

    def test_save_incident_with_minimal_data(self):
        minimal_data = {
            'type': 'Robo',
            'latitude': -12.0464,
            'longitude': -77.0428
        }
        
        feature = CreateIncidentFeature(
            data=minimal_data,
            user=self.user
        )
        
        incident = feature.save_incident()
        
        self.assertIsNotNone(incident)
        self.assertEqual(incident.title, 'Robo')
        self.assertEqual(incident.description, '')
        self.assertEqual(incident.address, '')
        self.assertIsNotNone(incident.location)
        self.assertIsInstance(incident.location, Point)
        self.assertEqual(incident.location.x, -77.0428)
        self.assertEqual(incident.location.y, -12.0464)

    @patch('core.incident.api.incident.feature.incident.logger')
    def test_save_incident_logs_info_messages(self, mock_logger):
        """Prueba que registra mensajes de log informativos"""
        feature = CreateIncidentFeature(
            data=self.incident_data,
            user=self.user
        )
        
        incident = feature.save_incident()
        
        self.assertTrue(mock_logger.info.called)
        self.assertGreaterEqual(mock_logger.info.call_count, 3)

    @patch('core.incident.models.Incident.objects.create')
    def test_save_incident_handles_exception(self, mock_create):
        mock_create.side_effect = Exception('Error de base de datos')
        
        feature = CreateIncidentFeature(
            data=self.incident_data,
            user=self.user
        )
        
        with self.assertRaises(Exception) as context:
            feature.save_incident()
        
        self.assertIn('Error de base de datos', str(context.exception))

    @patch('core.incident.api.incident.feature.incident.logger')
    @patch('core.incident.models.Incident.objects.create')
    def test_save_incident_logs_error_on_exception(self, mock_create, mock_logger):
        """Prueba que registra errores cuando ocurre una excepción"""
        mock_create.side_effect = Exception('Error de prueba')
        
        feature = CreateIncidentFeature(
            data=self.incident_data,
            user=self.user
        )
        
        with self.assertRaises(Exception):
            feature.save_incident()
        
        self.assertTrue(mock_logger.error.called)

    def test_feature_initialization(self):
        """Prueba la inicialización correcta de la clase"""
        mock_image = MagicMock()
        
        feature = CreateIncidentFeature(
            data=self.incident_data,
            user=self.user,
            image_file=mock_image
        )
        
        self.assertEqual(feature.data, self.incident_data)
        self.assertEqual(feature.user, self.user)
        self.assertEqual(feature.image_file, mock_image)

    def test_save_incident_sets_occurred_at(self):
        """Prueba que se establece la fecha de ocurrencia"""
        feature = CreateIncidentFeature(
            data=self.incident_data,
            user=self.user
        )
        
        incident = feature.save_incident()
        
        self.assertIsNotNone(incident.occurred_at)
        time_diff = timezone.now() - incident.occurred_at
        self.assertLess(time_diff.total_seconds(), 5)

    def test_save_incident_creates_user_stats_if_not_exists(self):
        """Prueba que se crea UserStats si no existe para el usuario"""
        from core.stats.models import UserStats
        self.assertFalse(UserStats.objects.filter(user=self.user).exists())
        
        feature = CreateIncidentFeature(
            data=self.incident_data,
            user=self.user
        )
        
        incident = feature.save_incident()
        
        self.assertTrue(UserStats.objects.filter(user=self.user).exists())
        stats = UserStats.objects.get(user=self.user)
        self.assertEqual(stats.total_alerts, 1)
        self.assertEqual(stats.total_alerts_pending, 1)

    def test_save_incident_updates_existing_user_stats(self):
        """Prueba que actualiza UserStats existente correctamente"""
        from core.stats.models import UserStats
        stats = UserStats.objects.create(
            user=self.user,
            total_alerts=5,
            total_alerts_resolved=2,
            total_alerts_pending=3
        )
        
        feature = CreateIncidentFeature(
            data=self.incident_data,
            user=self.user
        )
        
        incident = feature.save_incident()
        stats.refresh_from_db()
        self.assertEqual(stats.total_alerts, 6)
        self.assertEqual(stats.total_alerts_pending, 4)
        self.assertEqual(stats.total_alerts_resolved, 2)  # No debe cambiar

    def test_save_incident_increments_total_alerts(self):
        """Prueba que total_alerts se incrementa correctamente"""
        from core.stats.models import UserStats
        
        feature = CreateIncidentFeature(
            data=self.incident_data,
            user=self.user
        )
        
        incident = feature.save_incident()
        
        stats = UserStats.objects.get(user=self.user)
        self.assertEqual(stats.total_alerts, 1)
        
        feature2 = CreateIncidentFeature(
            data=self.incident_data,
            user=self.user
        )
        incident2 = feature2.save_incident()
        
        stats.refresh_from_db()
        self.assertEqual(stats.total_alerts, 2)

    def test_save_incident_increments_total_alerts_pending(self):
        """Prueba que total_alerts_pending se incrementa correctamente"""
        from core.stats.models import UserStats
        
        feature = CreateIncidentFeature(
            data=self.incident_data,
            user=self.user
        )
        
        incident = feature.save_incident()
        
        stats = UserStats.objects.get(user=self.user)
        self.assertEqual(stats.total_alerts_pending, 1)
        
        feature2 = CreateIncidentFeature(
            data=self.incident_data,
            user=self.user
        )
        incident2 = feature2.save_incident()
        
        stats.refresh_from_db()
        self.assertEqual(stats.total_alerts_pending, 2)
