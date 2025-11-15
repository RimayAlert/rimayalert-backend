from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from core.community.api.community.feature.community import ValidateOrCreateCommunityFeature


class AssignCommunityUser(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        data = request.data
        latitude = data.get("latitude")
        longitude = data.get("longitude")
        if latitude is None or longitude is None:
            return Response(
                {"message": "latitude y longitude son requeridos"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            feature = ValidateOrCreateCommunityFeature(
                user=request.user,
                latitude=latitude,
                longitude=longitude
            )
        except ValueError:
            return Response(
                {"message": "latitude y longitude deben ser numéricos"},
                status=status.HTTP_400_BAD_REQUEST
            )

        result = feature.execute()
        return Response(
            {
                "has_community": result["has_community"],
                "community": result["community"],
                "message": result["message"]
            },
            status=result["status"]
        )
