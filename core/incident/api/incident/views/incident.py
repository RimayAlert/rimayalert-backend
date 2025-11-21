import json
import logging

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from core.incident.api.incident.feature.incident import CreateIncidentFeature
from core.incident.utils.FCM_notification import FCMNotificationUtils
from core.incident.utils.location import LocationUtils

logger = logging.getLogger(__name__)


class RegisterIncidentApiView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        try:
            json_data = request.data.get('data')
            if not json_data:
                logger.warning("No se recibió campo 'data'")
                return Response(
                    {'error': 'Campo "data" es requerido'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            data_dict = json.loads(json_data)
            logger.info(f"Datos recibidos: {data_dict}")

            image_file = request.data.get('image') or request.FILES.get('image')
            if image_file:
                logger.info(f"Imagen recibida: {image_file.name} - {image_file.size} bytes")
            else:
                logger.info("No se recibió imagen")
            incident_feature = CreateIncidentFeature(
                data=data_dict,
                user=request.user,
                image_file=image_file
            )
            incident = incident_feature.save_incident()

            incident_lat = data_dict.get('latitude')
            incident_lng = data_dict.get('longitude')

            if incident_lat and incident_lng:
                self._notify_nearby_users(
                    incident=incident,
                    latitude=incident_lat,
                    longitude=incident_lng
                )

            return Response({
                'message': 'Incidente registrado exitosamente',
                'incident_id': incident.id,
            }, status=status.HTTP_201_CREATED)

        except Exception as e:
            logger.error(f"Error al registrar incidente: {str(e)}", exc_info=True)
            return Response(
                {'error': f'Error al registrar incidente: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def _notify_nearby_users(self, incident, latitude, longitude):
        try:
            location_utils = LocationUtils(float(latitude), float(longitude), 2.0)
            nearby_users = location_utils.get_nearby_users()
            if not nearby_users:
                logger.info("No hay usuarios cercanos para notificar")
                return

            title = "🚨 Alerta de Incidente Cercano"
            body = f"Se reportó un incidente a menos de 2km de tu ubicación"

            notification_data = {
                'incident_id': str(incident.id),
                'incident_type': str(incident.incident_type) if hasattr(incident, 'incident_type') else 'incident',
                'latitude': str(latitude),
                'longitude': str(longitude),
                'click_action': 'OPEN_INCIDENT_DETAIL'
            }

            result = FCMNotificationUtils.send_notification_to_users(
                users=nearby_users,
                title=title,
                body=body,
                data=notification_data
            )

            logger.info(
                f"Notificaciones enviadas - Exitosas: {result['success']}, "
                f"Fallidas: {result['failed']}"
            )

        except Exception as e:
            logger.error(f"Error al notificar usuarios cercanos: {str(e)}", exc_info=True)
