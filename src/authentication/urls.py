from django.urls import path

from authentication.views import (
    RequestParentUserSignupEmailOtpAPIView,
    RequestLoginEmailOtpAPIView,
    LoginWithEmailOtpAPIView,
    CustomTokenRefreshView,
    ParentProfileAPIView,
)


urlpatterns = [
    path('signup/parent/request-email-otp/', RequestParentUserSignupEmailOtpAPIView.as_view(), name="signup__parent__request_email_otp"),
    path('login/request-email-otp/', RequestLoginEmailOtpAPIView.as_view(), name="login__request_email_otp"),
    path('login/verify-email-otp/', LoginWithEmailOtpAPIView.as_view(), name="login__verify_email_otp"),
    path('token/refresh-access/', CustomTokenRefreshView.as_view(), name="token_refresh"),
    # path('token/blacklist-refresh/', LogoutAPIView.as_view(), name="logout"),
    path('profile/parent/', ParentProfileAPIView.as_view(), name="parent_profile"),
]
