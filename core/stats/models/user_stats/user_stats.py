from django.db import models

from core.authentication.models import User
from core.shared.models import BaseModel


class UserStats(BaseModel):
    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name="User")
    total_alerts = models.PositiveIntegerField(default=0, verbose_name="Total Alerts")
    total_alerts_resolved = models.PositiveIntegerField(default=0, verbose_name="Total Alerts Resolved")
    total_alerts_pending = models.PositiveIntegerField(default=0, verbose_name="Total Alerts Pending")

    def __str__(self):
        return f"Stats for {self.user.username}"

    class Meta:
        verbose_name = "User Stats"
        verbose_name_plural = "User Stats"
