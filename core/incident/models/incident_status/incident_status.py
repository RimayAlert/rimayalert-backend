from django.db import models


class IncidentStatus(models.Model):
    name = models.CharField(max_length=50, unique=True, verbose_name="Nombre")
    code = models.CharField(max_length=20, unique=True, verbose_name="Código")
    description = models.TextField(blank=True, verbose_name="Descripción")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Estado de incidente"
        verbose_name_plural = "Estados de incidentes"
