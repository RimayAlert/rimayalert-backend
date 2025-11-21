import logging

from core.authentication.models import FCMToken

logger = logging.getLogger(__name__)


class RegisterFCMTokenFeature:
    def __init__(self):
        self.user = None
        self.token = None
        self.device_id = None

    def register_or_update_token(self, user, fcm_data):
        self.user = user
        self.token = fcm_data.get("token")
        self.device_id = fcm_data.get("deviceId")

        if not self.token:
            logger.warning('FCMToken token not registered')
            return None

        try:
            token_obj, created = FCMToken.objects.update_or_create(
                token=self.token,
                defaults={
                    'user': self.user,
                    'device_id': self.device_id,
                    'is_active': True
                }
            )

            if created:
                logger.info(f'FCMToken created for user {self.user.email}')
            else:
                logger.info(f'FCMToken updated for user {self.user.email}')

            return token_obj

        except Exception as e:
            logger.error(f"Error al registrar token FCM para {self.user.email}: {str(e)}")
            raise

    def deactivate_old_tokens(self, user, current_token):
        try:
            FCMToken.objects.filter(
                user=user,
                is_active=True
            ).exclude(
                token=current_token
            ).update(is_active=False)

            logger.info(f"Tokens antiguos desactivados para usuario {user.username}")
        except Exception as e:
            logger.error(f"Error al desactivar tokens antiguos: {str(e)}")
