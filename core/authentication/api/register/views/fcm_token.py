import logging

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from core.authentication.api.register.feature.FCM_token import RegisterFCMTokenFeature
from core.authentication.api.register.serializers.fcm_token import UpdateFCMTokenSerializer

logger = logging.getLogger(__name__)


class UpdateFCMTokenApiView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        try:
            serializer = UpdateFCMTokenSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)

            fcm_data = {
                "token": serializer.validated_data.get('fcm_token'),
                "deviceId": serializer.validated_data.get('device_id')
            }

            fcm_feature = RegisterFCMTokenFeature()
            token_obj = fcm_feature.register_or_update_token(request.user, fcm_data)

            if token_obj:
                return Response({
                    'message': 'Token FCM actualizado exitosamente'
                }, status=status.HTTP_200_OK)
            else:
                return Response({
                    'error': 'No se pudo actualizar el token'
                }, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            logger.error(f"Error al actualizar token FCM: {str(e)}")
            return Response({
                'error': 'Error interno del servidor'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
