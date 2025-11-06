from django.db import models

from core.incident.models.incident.incident import Incident


class IncidentMedia(models.Model):
    MEDIA_TYPE_CHOICES = [
        ("image", "Imagen"),
        ("video", "Video"),
        ("audio", "Audio"),
    ]

    incident = models.ForeignKey(Incident, on_delete=models.CASCADE, related_name="media", verbose_name="Incidente")
    media_type = models.CharField(max_length=20, choices=MEDIA_TYPE_CHOICES, verbose_name="Tipo de medio")
    file = models.FileField(upload_to='incidents/%Y/%m/%d/', verbose_name="Archivo" , null=True, blank=True)
    description = models.TextField(blank=True, null=True, verbose_name="Descripción")
    uploaded_at = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de subida")

    class Meta:
        verbose_name = "Archivo multimedia"
        verbose_name_plural = "Archivos multimedia"
