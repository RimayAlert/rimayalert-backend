from django.db import models
from django.db.models import Count
from django.forms.models import model_to_dict

from core.authentication.models import User
from core.incident.models import Incident
from core.shared.models import BaseModel


class UserStats(BaseModel):
    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name="User", related_name="u_stats_by_user")
    total_alerts = models.PositiveIntegerField(default=0, verbose_name="Total Alerts")
    total_alerts_resolved = models.PositiveIntegerField(default=0, verbose_name="Total Alerts Resolved")
    total_alerts_pending = models.PositiveIntegerField(default=0, verbose_name="Total Alerts Pending")

    def __str__(self):
        return f"Stats for {self.user.username}"

    def top_type(self):
        top = (
            Incident.objects.filter(reported_by_user=self.user)
            .values("incident_type__name")
            .annotate(total=Count("id"))
            .order_by("-total")
            .first()
        )
        if not top:
            return None
        total = self.total_alerts or 0
        percentage = 0
        if total > 0:
            percentage = round((top["total"] / total) * 100, 2)
        return {
            "name": top["incident_type__name"],
            "count": top["total"],
            "percentage": percentage
        }

    def to_json_api(self):
        item = model_to_dict(self, exclude=["user", "id"])
        item['top_type'] = self.top_type()
        return item

    class Meta:
        verbose_name = "User Stats"
        verbose_name_plural = "User Stats"
