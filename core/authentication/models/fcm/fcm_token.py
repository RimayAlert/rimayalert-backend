from django.db import models


class FCMToken(models.Model):
    user = models.ForeignKey(
        "authentication.User",
        on_delete=models.CASCADE,
        related_name='fcm_tokens_by_user',
        verbose_name='Usuario'
    )
    token = models.CharField(max_length=255, unique=True, verbose_name='Token FCM')
    device_id = models.CharField(max_length=255, blank=True, null=True, verbose_name='ID del dispositivo')
    is_active = models.BooleanField(default=True, verbose_name='Activo')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Creado en')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Actualizado en')

    class Meta:
        verbose_name = 'Token FCM'
        verbose_name_plural = 'Tokens FCM'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.email} - {self.token[:20]}..."
