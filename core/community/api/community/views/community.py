from django.contrib.gis.geos import Point
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from core.community.models import CommunityMembership, Community


class CheckCommunityUser(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        membership = user.c_memberships_by_user.select_related('community').first()

        data_response = {
            "hasCommunity": membership is not None,
            "community": {
                "id": membership.community.id,
                "name": membership.community.name,
                "isVerified": membership.is_verified
            } if membership else None,
        }
        return Response(data=data_response, status=status.HTTP_200_OK)


class AssignCommunityUser(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        data = request.data
        latitude = data.get('latitude')
        longitude = data.get('longitude')

        # Aceptar 0.0 como válido; sólo rechazar si es None
        if latitude is None or longitude is None:
            return Response(
                {"error": "latitude y longitude son requeridos"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            point = Point(float(longitude), float(latitude), srid=4326)
        except (TypeError, ValueError):
            return Response(
                {"error": "latitude y longitude deben ser numéricos"},
                status=status.HTTP_400_BAD_REQUEST
            )

        community = Community.objects.filter(
            boundary_area__contains=point,
            is_active=True
        ).first()

        if not community:
            return Response(
                {"error": "No se encontró comunidad para la ubicación proporcionada"},
                status=status.HTTP_404_NOT_FOUND
            )

        membership, created = CommunityMembership.objects.get_or_create(
            user=request.user,
            community=community,
            defaults={'is_verified': False}
        )

        return Response(
            {
                "communityId": community.id,
                "communityName": community.name,
                "isVerified": membership.is_verified,
                "created": created
            },
            status=status.HTTP_201_CREATED if created else status.HTTP_200_OK
        )
