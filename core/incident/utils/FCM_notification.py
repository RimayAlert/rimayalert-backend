import logging

from firebase_admin import messaging

from core.authentication.models import FCMToken

logger = logging.getLogger(__name__)


class FCMNotificationUtils:

    @staticmethod
    def send_notification_to_users(users, title, body, data=None):
        """
        Envía notificación push a una lista de usuarios

        Args:
            users: Lista de instancias de User
            title: Título de la notificación
            body: Cuerpo del mensaje
            data: Dict opcional con datos adicionales

        Returns:
            Dict con resultados del envío
        """
        if not users:
            logger.warning("No hay usuarios para enviar notificaciones")
            return {'success': 0, 'failed': 0}

        # Obtener tokens activos de los usuarios
        user_ids = [user.id for user in users]
        tokens = FCMToken.objects.filter(
            user_id__in=user_ids,
            is_active=True
        ).values_list('token', flat=True)

        if not tokens:
            logger.warning(f"No se encontraron tokens FCM para {len(users)} usuarios")
            return {'success': 0, 'failed': 0}

        return FCMNotificationUtils.send_notification_to_tokens(
            tokens=list(tokens),
            title=title,
            body=body,
            data=data
        )

    @staticmethod
    def send_notification_to_tokens(tokens, title, body, data=None):
        """
        Envía notificación a una lista de tokens

        Args:
            tokens: Lista de tokens FCM
            title: Título de la notificación
            body: Cuerpo del mensaje
            data: Dict opcional con datos adicionales

        Returns:
            Dict con resultados: {'success': int, 'failed': int, 'invalid_tokens': list}
        """
        if not tokens:
            return {'success': 0, 'failed': 0, 'invalid_tokens': []}

        success_count = 0
        failed_count = 0
        invalid_tokens = []

        # Preparar datos adicionales
        notification_data = data or {}

        # Crear mensaje de notificación
        notification = messaging.Notification(
            title=title,
            body=body
        )

        # Enviar a cada token (Firebase permite envío en lote, pero para mejor control lo hacemos individual)
        for token in tokens:
            try:
                message = messaging.Message(
                    notification=notification,
                    data=notification_data,
                    token=token,
                    android=messaging.AndroidConfig(
                        priority='high',
                        notification=messaging.AndroidNotification(
                            sound='default',
                            priority='high'
                        )
                    ),
                    apns=messaging.APNSConfig(
                        payload=messaging.APNSPayload(
                            aps=messaging.Aps(
                                sound='default',
                                badge=1
                            )
                        )
                    )
                )

                response = messaging.send(message)
                success_count += 1
                logger.info(f"Notificación enviada exitosamente: {response}")

            except messaging.UnregisteredError:
                # Token inválido o desregistrado
                logger.warning(f"Token no registrado o inválido: {token[:20]}...")
                invalid_tokens.append(token)
                failed_count += 1

            except Exception as e:
                logger.error(f"Error al enviar notificación al token {token[:20]}...: {str(e)}")
                failed_count += 1

        # Desactivar tokens inválidos
        if invalid_tokens:
            FCMToken.objects.filter(token__in=invalid_tokens).update(is_active=False)
            logger.info(f"Desactivados {len(invalid_tokens)} tokens inválidos")

        result = {
            'success': success_count,
            'failed': failed_count,
            'invalid_tokens': invalid_tokens
        }

        logger.info(f"Resumen de envío: {result}")
        return result
