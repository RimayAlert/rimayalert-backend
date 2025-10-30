from django.db import models

from core.authentication.models import User
from core.community.models.community.community import Community
from core.incident.models.incident_status.incident_status import IncidentStatus
from core.incident.models.incident_type.incident_type import IncidentType
from core.shared.models import BaseModel


class Incident(BaseModel):
    reported_by_user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Reportado por")
    community = models.ForeignKey(Community, on_delete=models.CASCADE, verbose_name="Comunidad")
    incident_type = models.ForeignKey(IncidentType, on_delete=models.PROTECT, verbose_name="Tipo de incidente", )
    incident_status = models.ForeignKey(IncidentStatus, on_delete=models.PROTECT, verbose_name="Estado")
    title = models.CharField(max_length=200, verbose_name="Título")
    description = models.TextField(verbose_name="Descripción")
    latitude = models.DecimalField(max_digits=9, decimal_places=6, verbose_name="Latitud")
    longitude = models.DecimalField(max_digits=9, decimal_places=6, verbose_name="Longitud")
    address = models.CharField(max_length=255, blank=True, verbose_name="Dirección")
    is_anonymous = models.BooleanField(default=False, verbose_name="Anónimo")
    severity_level = models.IntegerField(blank=True, null=True, verbose_name="Nivel de severidad")
    is_active = models.BooleanField(default=True, verbose_name="Activo")
    occurred_at = models.DateTimeField(verbose_name="Fecha del suceso")
    reported_at = models.DateTimeField(blank=True, null=True, verbose_name="Fecha del reporte")

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Incidente"
        verbose_name_plural = "Incidentes"
