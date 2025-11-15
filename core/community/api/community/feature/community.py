from django.contrib.gis.geos import Point
from rest_framework import status

from core.community.models import CommunityMembership, Community


class ValidateOrCreateCommunityFeature:

    def __init__(self, user, latitude, longitude):
        self.user = user
        self.latitude = float(latitude)
        self.longitude = float(longitude)
        self.point = Point(self.longitude, self.latitude, srid=4326)

    def validate_user_membership(self):
        membership = self.user.c_memberships_by_user.first()
        if membership:
            return {
                "has_community": True,
                "community": {
                    "id": membership.community.id,
                    "name": membership.community.name,
                    "is_verified": membership.is_verified,
                },
                "message": "El usuario ya pertenece a una comunidad",
                "status": status.HTTP_200_OK
            }

        return None

    def find_community(self):
        community = Community.objects.filter(
            is_active=True,
            boundary_area__contains=self.point
        ).first()
        return community

    def create_community(self):
        buffer_polygon = self.point.buffer(0.0001)
        community = Community.objects.create(
            boundary_area=buffer_polygon,
            is_active=True
        )
        return community

    def assign_user(self, community):
        membership, created = CommunityMembership.objects.get_or_create(
            user=self.user,
            community=community,
            defaults={"is_verified": False}
        )

        return membership, created

    def execute(self):
        validated = self.validate_user_membership()
        if validated:
            return validated
        community = self.find_community()
        created_new = False
        if community is None:
            community = self.create_community()
            created_new = True
        membership, _ = self.assign_user(community)
        return {
            "has_community": True,
            "community": {
                "id": community.id,
                "name": community.name,
                "is_verified": membership.is_verified
            },
            "message": "Usuario asignado a una nueva comunidad" if created_new else "Usuario asignado a la comunidad",
            "status": status.HTTP_201_CREATED if created_new else status.HTTP_200_OK
        }
