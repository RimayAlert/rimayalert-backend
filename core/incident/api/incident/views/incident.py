import json
import logging

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from core.incident.api.incident.feature.incident import CreateIncidentFeature

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
