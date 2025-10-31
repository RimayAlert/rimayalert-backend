from django.contrib import admin

from core.incident.models import Incident, IncidentType, IncidentStatus, IncidentComment

# Register your models here.
admin.site.register(Incident)
admin.site.register(IncidentType)
admin.site.register(IncidentStatus)
admin.site.register(IncidentComment)
