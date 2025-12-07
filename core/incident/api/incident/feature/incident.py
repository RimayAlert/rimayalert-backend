import logging
from django.utils import timezone
from django.contrib.gis.geos import Point

from core.incident.models import IncidentMedia, Incident, IncidentType, IncidentStatus
from core.stats.models import UserStats

logger = logging.getLogger(__name__)

class CreateIncidentFeature:
    def __init__(self, data, user, image_file=None):
        self.data = data
        self.user = user
        self.image_file = image_file

    def save_incident(self):
        try:
            incident_type, created = IncidentType.objects.get_or_create(
                name=self.data.get('type'),
                defaults={
                    'code': self.data.get('type', '').lower().replace(' ', '_'),
                    'description': f"Tipo de incidente: {self.data.get('type')}"
                }
            )
            logger.info(f"Tipo de incidente: {incident_type.name} - {'Creado' if created else 'Existente'}")

            incident_status, created = IncidentStatus.objects.get_or_create(
                code="reported",
                defaults={
                    'name': "Reported",
                    'description': "Incident has been reported and is pending review."
                }
            )
            logger.info(f"Estado: {incident_status.name} - {'Creado' if created else 'Existente'}")

            latitude = self.data.get('latitude')
            longitude = self.data.get('longitude')
            point = None
            if latitude is not None and longitude is not None:
                try:
                    point = Point(float(longitude), float(latitude), srid=4326)
                except (TypeError, ValueError):
                    logger.warning("Coordenadas inválidas, se ignorará location")

            incident = Incident.objects.create(
                reported_by_user=self.user,
                incident_type=incident_type,
                incident_status=incident_status,
                title=self.data.get('type'),
                description=self.data.get('description', ''),
                address=self.data.get('location', ''),
                location=point,
                is_anonymous=True,
                occurred_at=timezone.now()
            )
            stats, _ = UserStats.objects.get_or_create(user=incident.reported_by_user)
            stats.total_alerts += 1
            stats.total_alerts_pending += 1
            stats.save()
            logger.info(f"Incidente creado: ID {incident.id}")

            if self.image_file:
                media = IncidentMedia.objects.create(
                    incident=incident,
                    media_type='image',
                    file=self.image_file
                )
                logger.info(f"Imagen guardada: {media.file.name}")
            return incident

        except Exception as e:
            logger.error(f"Error al crear incidente: {str(e)}")
            raise