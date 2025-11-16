import logging

from django.contrib.gis.db.models.functions import Distance as DistanceFunc
from django.contrib.gis.geos import Point
from django.contrib.gis.measure import Distance

from core.authentication.models import UserProfile
from core.community.models import CommunityMembership

logger = logging.getLogger(__name__)


class LocationUtils:

    def __init__(self, latitude, longitude, radius_km=2.0):
        self.latitude = latitude
        self.longitude = longitude
        self.radius_km = radius_km
        self.origin_point = Point(longitude, latitude, srid=4326)

    def get_nearby_users(self):
        try:
            # Buscar perfiles de usuarios dentro del radio
            nearby_profiles = UserProfile.objects.filter(
                location__distance_lte=(
                    self.origin_point,
                    Distance(km=self.radius_km)
                )
            ).annotate(
                distance=DistanceFunc('location', self.origin_point)
            ).select_related('user').order_by('distance')

            # Extraer los usuarios
            users = [profile.user for profile in nearby_profiles]

            logger.info(
                f"Encontrados {len(users)} usuarios dentro de {self.radius_km}km "
                f"de ({self.latitude}, {self.longitude})"
            )

            return users

        except Exception as e:
            logger.error(f"Error al buscar usuarios cercanos: {str(e)}")
            return []

    def get_nearby_users_with_distance(self):
        try:
            nearby_profiles = UserProfile.objects.filter(
                location__distance_lte=(
                    self.origin_point,
                    Distance(km=self.radius_km)
                )
            ).annotate(
                distance=DistanceFunc('location', self.origin_point)
            ).select_related('user').order_by('distance')

            users_with_distance = [
                {
                    'user': profile.user,
                    'distance_km': round(profile.distance.km, 2),
                    'profile': profile
                }
                for profile in nearby_profiles
            ]

            logger.info(f"Usuarios cercanos encontrados: {len(users_with_distance)}")

            return users_with_distance

        except Exception as e:
            logger.error(f"Error al buscar usuarios con distancia: {str(e)}")
            return []

    def get_nearby_community_members(self, community):
        try:
            nearby_users = self.get_nearby_users()
            community_user_ids = CommunityMembership.objects.filter(
                community=community,
                is_verified=True
            ).values_list('user_id', flat=True)

            filtered_users = [
                user for user in nearby_users
                if user.id in community_user_ids
            ]

            logger.info(
                f"Encontrados {len(filtered_users)} miembros de la comunidad "
                f"'{community.name}' cercanos"
            )

            return filtered_users

        except Exception as e:
            logger.error(f"Error al buscar miembros cercanos de comunidad: {str(e)}")
            return []
