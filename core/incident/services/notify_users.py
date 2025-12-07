import logging

from core.incident.models import IncidentNotification
from core.incident.utils.FCM_notification import FCMNotificationUtils
from core.incident.utils.location import LocationUtils

logger = logging.getLogger(__name__)


class NearbyUsersNotifier():

    def send_notifications(self, incident, latitude, longitude):
        try:
            location_utils = LocationUtils(float(latitude), float(longitude), 2.0)
            nearby_users = location_utils.get_nearby_users()

            if not nearby_users:
                logger.info("No hay usuarios cercanos para notificar")
                return

            incident_type = getattr(incident, "incident_type", "incidente")
            incident_type_lower = str(incident_type).lower()

            title_map = {
                "robo": "🚨 Alerta de Robo Cercano",
                "asalto": "🚨 Alerta de Asalto Cercano",
                "accidente": "🚑 Accidente de Tránsito Cercano",
                "emergencia": "🆘 Emergencia Médica Cercana",
                "medico": "🆘 Emergencia Médica Cercana",
                "incendio": "🔥 Alerta de Incendio Cercano",
                "seguridad": "🛡️ Alerta de Seguridad en tu Zona",
            }

            body_map = {
                "robo": "Se ha reportado un posible robo cerca de tu ubicación. Mantente alerta.",
                "asalto": "Se ha reportado un asalto en tu zona. Evita transitar por el área.",
                "accidente": "Se registró un accidente de tránsito a menos de 2 km de tu ubicación.",
                "emergencia": "Se ha reportado una emergencia médica cercana.",
                "medico": "Atención: emergencia médica registrada en tu sector.",
                "incendio": "Se reporta un posible incendio cerca de tu ubicación. Toma precauciones.",
                "seguridad": "Se ha reportado una situación de seguridad en tu zona. Permanece atento y toma precauciones.",
            }

            title = title_map.get(incident_type_lower, "⚠️ Incidente Cercano")
            body = body_map.get(incident_type_lower, "Se detectó un incidente cerca de tu ubicación.")

            notification_data = {
                'incident_id': str(incident.id),
                'incident_type': str(incident.incident_type),
                'latitude': str(latitude),
                'longitude': str(longitude),
                'click_action': 'OPEN_INCIDENT_DETAIL'
            }

            result = FCMNotificationUtils.send_notification_to_users(
                users=nearby_users,
                title=title,
                body=body,
                data=notification_data
            )

            notifications_to_create = []
            for user in nearby_users:
                notifications_to_create.append(
                    IncidentNotification(
                        incident=incident,
                        notified_user=user
                    )
                )

            if notifications_to_create:
                IncidentNotification.objects.bulk_create(
                    notifications_to_create,
                    ignore_conflicts=True
                )

            logger.info(
                f"Notificaciones enviadas - Exitosas: {result['success']}, "
                f"Fallidas: {result['failed']}, "
                f"Registros guardados: {len(notifications_to_create)}"
            )

        except Exception as e:
            logger.error(f"Error al notificar usuarios cercanos: {str(e)}")
