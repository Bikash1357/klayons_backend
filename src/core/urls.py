from django.urls import path

from backend_main.settings import APP_MODE
from core.views import (
    SocietyListView,
    GetOtpForUserAPIView,
)


urlpatterns = [
    path('societies/', SocietyListView.as_view(), name="society_list"),
]

testing_url_patterns = [
    path('testing/access-db/otp-for-user/', GetOtpForUserAPIView.as_view(), name="get_otp_for_user"),
]

if APP_MODE == "TESTING":
    urlpatterns += testing_url_patterns
