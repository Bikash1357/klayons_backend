from django.urls import path

from notifications.views import NotificationListView, NotificationMarkAsReadView


urlpatterns = [
    path('objects/list/', NotificationListView.as_view(), name='notification-list'),
    path('objects/<int:pk>/mark-as-read/', NotificationMarkAsReadView.as_view(), name='notification-mark-as-read'),
]

