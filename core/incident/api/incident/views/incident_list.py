from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from core.incident.api.incident.serializer.incident_list import IncidentListSerializer


class ListIncidentApiView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        incidents = user.incidents_by_reported_user.order_by('-reported_at')[:4]
        if incidents:
            data = IncidentListSerializer(incidents, many=True).data
        else:
            data = []
        return Response(data, status=status.HTTP_200_OK)
