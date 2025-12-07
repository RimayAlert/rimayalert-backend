import json
import logging

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from core.incident.api.incident.feature.incident import CreateIncidentFeature
from core.incident.services.notify_users import NearbyUsersNotifier

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

            incident_creator = CreateIncidentFeature(
                data=data_dict,
                user=request.user,
                image_file=image_file
            )
            incident = incident_creator.save_incident()

            incident_lat = data_dict.get('latitude')
            incident_lng = data_dict.get('longitude')

            if incident_lat and incident_lng:
                notify = NearbyUsersNotifier()
                notify.send_notifications(incident, incident_lat, incident_lng)
            return Response({
                'message': 'Incidente registrado exitosamente',
                'incident_id': incident.id,
            }, status=status.HTTP_201_CREATED)

        except Exception as e:
            logger.error(f"Error al registrar incidente: {str(e)}")
            return Response(
                {'error': f'Error al registrar incidente: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
