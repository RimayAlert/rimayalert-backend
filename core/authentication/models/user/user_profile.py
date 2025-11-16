from django.db import models
from django.contrib.gis.db import models as gis_models


class UserProfile(models.Model):
    user = models.OneToOneField('authentication.User', on_delete=models.CASCADE, related_name='profiles_by_user')
    bio = models.TextField(null=True, blank=True, verbose_name='Biografía')
    alias_name = models.TextField(null=True, blank=True, verbose_name='Alias name')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de creación')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Fecha de actualización')
    location = gis_models.PointField(srid=4326, blank=True, null=True, verbose_name="Área límite")
    latitude = models.FloatField(null=True, blank=True, verbose_name='Latitud')
    longitude = models.FloatField(null=True, blank=True, verbose_name='Longitud')

    def __str__(self):
        return f'Profile of {self.user.get_full_name()}'

    class Meta:
        verbose_name = 'User Profile'
        verbose_name_plural = 'User Profiles'
