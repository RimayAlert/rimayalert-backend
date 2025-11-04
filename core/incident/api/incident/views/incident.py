import logging

from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.views import APIView

logger = logging.getLogger(__name__)


class RegisterIncidentApiView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        print("User:", request.user)
        print("Is authenticated:", request.user.is_authenticated)
        print("Auth:", request.auth)

