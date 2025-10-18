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
    file_path = models.CharField(max_length=500, verbose_name="Ruta del archivo")
    file_url = models.CharField(max_length=500, blank=True, verbose_name="URL del archivo")
    description = models.TextField(blank=True, verbose_name="Descripción")
    uploaded_at = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de subida")

    class Meta:
        verbose_name = "Archivo multimedia"
        verbose_name_plural = "Archivos multimedia"
