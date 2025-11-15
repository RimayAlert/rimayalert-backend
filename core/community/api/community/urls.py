from django.urls import path

from core.community.api.community.views.community import AssignCommunityUser

urlpatterns = [
    path('assign', AssignCommunityUser.as_view(), name='assign_community')
]
