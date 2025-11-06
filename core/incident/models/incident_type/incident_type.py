from django.db import models


class IncidentType(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name="Nombre")
    code = models.CharField(max_length=20, unique=True, verbose_name="Código", blank=True, null=True)
    description = models.TextField(blank=True, verbose_name="Descripción")
    icon = models.CharField(max_length=50, blank=True, verbose_name="Icono")
    color_hex = models.CharField(max_length=7, blank=True, verbose_name="Color HEX")
    default_severity = models.IntegerField(blank=True, null=True, verbose_name="Severidad predeterminada")
    requires_authority = models.BooleanField(default=False, verbose_name="Requiere autoridad")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Tipo de incidente"
        verbose_name_plural = "Tipos de incidentes"
