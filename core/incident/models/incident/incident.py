from django.contrib.gis.db import models as gis_models
from django.db import models

from core.authentication.models import User
from core.incident.models.incident_status.incident_status import IncidentStatus
from core.incident.models.incident_type.incident_type import IncidentType
from core.shared.models import BaseModel


class Incident(BaseModel):
    reported_by_user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Reportado por",
                                         related_name="incidents_by_reported_user")
    incident_type = models.ForeignKey(IncidentType, on_delete=models.PROTECT, verbose_name="Tipo de incidente")
    incident_status = models.ForeignKey(IncidentStatus, on_delete=models.PROTECT, verbose_name="Estado")
    title = models.CharField(max_length=200, verbose_name="Título")
    description = models.TextField(verbose_name="Descripción")
    location = gis_models.PointField(srid=4326, blank=True, null=True, verbose_name="Ubicación")
    address = models.CharField(max_length=255, blank=True, null=True, verbose_name="Dirección")
    is_anonymous = models.BooleanField(default=False, verbose_name="Anónimo")
    severity_level = models.IntegerField(blank=True, null=True, verbose_name="Nivel de severidad")
    is_active = models.BooleanField(default=True, verbose_name="Activo")
    occurred_at = models.DateTimeField(blank=True, null=True, verbose_name="Fecha del suceso")
    reported_at = models.DateTimeField(auto_now_add=True, verbose_name="Fecha del reporte")

    def __str__(self):
        return self.title

    def to_json_api(self):
        item = dict()
        item["id"] = self.id
        item['title'] = self.title
        item['description'] = self.description
        item['occurred_at'] = self.occurred_at and self.occurred_at.isoformat() or None
        item['severity_level'] = self.severity_level
        return item

    def to_json_map(self, current_user_id=None):
        item = dict()
        item["id"] = self.id
        item['title'] = self.title
        item['description'] = self.description
        item['latitude'] = self.location.y if self.location else None
        item['longitude'] = self.location.x if self.location else None
        item['severity_level'] = self.severity_level
        item['incident_type_name'] = self.incident_type.name if self.incident_type else None
        item['status_name'] = self.incident_status.name if self.incident_status else None
        item['is_own'] = self.reported_by_user_id == current_user_id if current_user_id else False
        item['occurred_at'] = self.occurred_at and self.occurred_at.isoformat() or None
        item['reported_at'] = self.reported_at.isoformat()
        item['address'] = self.address

        if current_user_id:
            notification = self.notifications.filter(notified_user_id=current_user_id).first()
            item['was_notified'] = notification is not None
            item['notified_at'] = notification.notification_sent_at.isoformat() if notification else None
            item['was_read'] = notification.was_read if notification else False
        else:
            item['was_notified'] = False
            item['notified_at'] = None
            item['was_read'] = False

        return item

    class Meta:
        verbose_name = "Incidente"
        verbose_name_plural = "Incidentes"


# models.py

class IncidentNotification(models.Model):
    incident = models.ForeignKey(
        Incident,
        on_delete=models.CASCADE,
        related_name='notifications',
        verbose_name="Incidente"
    )
    notified_user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='received_notifications',
        verbose_name="Usuario notificado"
    )
    notification_sent_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Fecha de notificación"
    )
    was_read = models.BooleanField(
        default=False,
        verbose_name="Leído"
    )
    read_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Fecha de lectura"
    )

    class Meta:
        db_table = "incident_notification"
        verbose_name = "Notificación de Incidente"
        verbose_name_plural = "Notificaciones de Incidentes"
        ordering = ['-notification_sent_at']
        indexes = [
            models.Index(fields=['notified_user', '-notification_sent_at']),
            models.Index(fields=['incident', 'notified_user']),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=['incident', 'notified_user'],
                name='unique_incident_notification_per_user'
            )
        ]

    def __str__(self):
        return f"{self.incident.title} -> {self.notified_user.username}"
