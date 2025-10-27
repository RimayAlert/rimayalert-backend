from core.authentication.models import UserProfile, User


class RegisterUserProfileFeature:

    def create_user_profile(self, user: User, profile_data: dict) -> UserProfile:
        profile = UserProfile.objects.create(
            user=user,
            alias_name=profile_data.get('displayName', '')
        )
        return profile
