from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView


class CheckCommunityUser(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        has_community = user.c_memberships_by_user.exists()
        data_response = {
            "hasCommunity": has_community,
            'community': None,
        }
        return Response(data=data_response, status=status.HTTP_200_OK)


class AssignCommunityUser(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        data = self.request.data
        print(data)

        return Response(status=status.HTTP_200_OK)
