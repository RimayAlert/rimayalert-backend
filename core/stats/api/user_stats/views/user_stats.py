import logging

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from core.stats.api.user_stats.serializer.user_stats import StatsListSerializer

logger = logging.getLogger(__name__)


class ListStatsApiView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            user = request.user
            data_stats = user.u_stats_by_user
            logger.info("Recuperando estadísticas de usuario")
            if data_stats:
                data = StatsListSerializer(data_stats, many=False).data
                logger.info("Recuperando lista de usuario")
            else:
                data = {}
            return Response(data, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Error al recuperar las estadísticas de usuario: {str(e)}")
            return Response({"detail": "Error retrieving user stats."},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)
