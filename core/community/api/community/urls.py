from django.urls import path

from core.community.api.community.views.community import CheckCommunityUser, AssignCommunityUser

urlpatterns = [
    path('check', CheckCommunityUser.as_view(), name='check_community'),
    path('assign', AssignCommunityUser.as_view(), name='assign_community')
]
