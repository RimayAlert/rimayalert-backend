from django.db import models


class UserProfile(models.Model):
    user = models.OneToOneField('authentication.User', on_delete=models.CASCADE, related_name='profile')
    bio = models.TextField(null=True, blank=True, verbose_name='Biografía')
    alias_name = models.TextField(null=True, blank=True, verbose_name='Alias name')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de creación')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Fecha de actualización')

    def __str__(self):
        return f'Profile of {self.user.get_full_name()}'

    class Meta:
        verbose_name = 'User Profile'
        verbose_name_plural = 'User Profiles'
