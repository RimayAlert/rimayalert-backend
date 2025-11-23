from django.contrib.gis.geos import Point

from core.authentication.models import UserProfile, User


class RegisterUserProfileFeature:

    def create_user_profile(self, user: User, profile_data: dict) -> UserProfile:
        latitude = profile_data.get('latitude')
        longitude = profile_data.get('longitude')

        profile = UserProfile.objects.create(
            user=user,
            alias_name=profile_data.get('displayName', ''),
            latitude=latitude,
            longitude=longitude,
            location=Point(longitude, latitude, srid=4326) if latitude and longitude else None,
        )

        return profile
