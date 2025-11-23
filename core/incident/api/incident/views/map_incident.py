# views.py

from django.contrib.gis.geos import Point
from django.contrib.gis.measure import D
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

from core.incident.api.incident.serializer.map_incident import MapIncidentSerializer
from core.incident.models import Incident


class MapIncidentsApiView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user

        try:
            user_profile = user.profiles_by_user
            if not user_profile.latitude or not user_profile.longitude:
                return Response(
                    {'error': 'Usuario sin ubicación configurada'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            user_lat = user_profile.latitude
            user_lng = user_profile.longitude

        except Exception as e:
            return Response(
                {'error': 'No se pudo obtener la ubicación del usuario'},
                status=status.HTTP_400_BAD_REQUEST
            )

        radius_km = 5.0

        user_location = Point(user_lng, user_lat, srid=4326)

        incidents = Incident.objects.filter(
            is_active=True,
            location__isnull=False,
            location__distance_lte=(user_location, D(km=radius_km))
        ).select_related(
            'incident_type',
            'incident_status',
            'reported_by_user'
        ).order_by('-reported_at')

        my_incidents = incidents.filter(reported_by_user=user)
        other_incidents = incidents.exclude(reported_by_user=user)

        context = {'request': request}
        my_incidents_data = MapIncidentSerializer(my_incidents, many=True, context=context).data
        other_incidents_data = MapIncidentSerializer(other_incidents, many=True, context=context).data

        data = {
            'my_incidents': my_incidents_data,
            'other_incidents': other_incidents_data,
            'total_count': len(my_incidents_data) + len(other_incidents_data),
            'radius_km': radius_km,
            'user_location': {
                'latitude': user_lat,
                'longitude': user_lng
            }
        }

        print(data)

        return Response(data, status=status.HTTP_200_OK)