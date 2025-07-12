from django.urls import path, include
from rest_framework.routers import DefaultRouter

from activities.views import ChildViewSet, ActivityInstancesByUserSocietyAPIView, GetParentUserCalenderAPIView


children_router = DefaultRouter()
children_router.register(r'', ChildViewSet, basename='child')


urlpatterns = [
    path('children/', include(children_router.urls)),
    path('activities/instances/by-society', ActivityInstancesByUserSocietyAPIView.as_view(), name="activity_instance_by_user_society"),
    path('parent-user-calender', GetParentUserCalenderAPIView.as_view(), name="get_parent_user_calender"),
]
