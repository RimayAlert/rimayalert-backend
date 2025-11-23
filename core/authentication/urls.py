from django.urls import path, include

from core.authentication.views import LoginAuthView, SignupView
from core.authentication.views.logout.logout import LogoutView

app_name = 'authentication'
urlpatterns = [
    path('', LoginAuthView.as_view(), name='login'),
    path('signup/', SignupView.as_view(), name='signup'),
    path('logout/', LogoutView, name='logout'),
    path('api/', include('core.authentication.api.urls'))
]
