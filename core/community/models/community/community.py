from django.db import models


class Community(models.Model):
    name = models.CharField(max_length=200, verbose_name="Nombre")
    description = models.TextField(blank=True, verbose_name="Descripción")
    boundary_area = models.JSONField(blank=True, null=True, verbose_name="Área límite")
    postal_code = models.CharField(max_length=10, blank=True, verbose_name="Código postal")
    is_active = models.BooleanField(default=True, verbose_name="Está activa")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Creado en")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Actualizado en")

    class Meta:
        db_table = "community"
        verbose_name = "Comunidad"
        verbose_name_plural = "Comunidades"

    def __str__(self):
        return self.name
