import logging

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from core.community.api.community.feature.community import ValidateOrCreateCommunityFeature

logger = logging.getLogger(__name__)


class AssignCommunityUser(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        data = request.data
        latitude = data.get("latitude")
        longitude = data.get("longitude")
        if latitude is None or longitude is None:
            return Response({"message": "latitude y longitude son requeridos"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            feature = ValidateOrCreateCommunityFeature(request.user, latitude, longitude)
            logger.info(
                f"User {request.user.id} is attempting to assign community with "
                f"latitude: {latitude}, longitude: {longitude}"
            )
        except ValueError:
            logger.error(
                f"Invalid latitude or longitude provided by user {request.user.id}: "
                f"latitude={latitude}, longitude={longitude}"
            )
            return Response(
                {"message": "latitude y longitude deben ser numéricos"},
                status=status.HTTP_400_BAD_REQUEST
            )

        result = feature.execute()
        logger.info(f"Community assignment result for user {request.user.id}: {result}")
        return Response(
            {
                "has_community": result["has_community"],
                "community": result["community"],
                "message": result["message"]
            },
            status=result["status"]
        )
