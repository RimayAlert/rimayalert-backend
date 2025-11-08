from django import template
from django.utils import timezone

register = template.Library()


@register.filter
def timesince_short(value):
    if not value:
        return ""

    now = timezone.now()
    diff = now - value
    seconds = diff.total_seconds()

    if seconds < 0 or seconds < 60:
        return "Justo ahora"

    intervals = [
        (2592000, "mes", "meses"),
        (604800, "semana", "semanas"),
        (86400, "día", "días"),
        (3600, "hora", "horas"),
        (60, "min", "min"),
    ]

    for limit, singular, plural in intervals:
        if seconds >= limit:
            count = int(seconds // limit)
            label = plural if count > 1 else singular
            return f"Hace {count} {label}"

    return "Justo ahora"


@register.filter
def incident_type_icon(incident_type):
    if not incident_type:
        return "fas fa-exclamation-circle"

    if hasattr(incident_type, 'icon') and incident_type.icon:
        return incident_type.icon

    return "fas fa-exclamation-triangle"
