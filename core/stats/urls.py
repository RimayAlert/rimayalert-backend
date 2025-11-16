from django.urls import path, include

app_name = 'stats'

urlpatterns = [
    #     API
    path('api/', include('core.stats.api.urls'))
]
