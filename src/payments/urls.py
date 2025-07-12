from django.urls import path

from payments.views import (
    CreateActivityBookingsOrder,
    VerifyPaymentWebhook,
)

urlpatterns = [
    path('orders/activity-bookings/', CreateActivityBookingsOrder.as_view(), name="create_activity_bookings_order"),
    path('webhooks/verify-payment/', VerifyPaymentWebhook.as_view(), name="verify_payment_webhook"),
]
