from django.db import models

from core.authentication.models import User
from core.incident.models.incident.incident import Incident


class IncidentComment(models.Model):
    incident = models.ForeignKey(
        Incident,
        on_delete=models.CASCADE,
        related_name="comments",
        verbose_name="Incidente"
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="incident_comments", verbose_name="Usuario")
    comment = models.TextField(verbose_name="Comentario")
    is_anonymous = models.BooleanField(default=False, verbose_name="Anónimo")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Creado en")
    is_active = models.BooleanField(default=True, verbose_name="Activo")

    def __str__(self):
        return f"Comentario #{self.id} en {self.incident.title}"

    class Meta:
        verbose_name = "Comentario de incidente"
        verbose_name_plural = "Comentarios de incidentes"
