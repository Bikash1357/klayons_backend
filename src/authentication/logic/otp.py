from datetime import timedelta
import random

from django.utils import timezone

from backend_main.settings import EMAIL_OTP_NUM_DIGITS, EMAIL_OTP_LIFESPAN


EMAIL_OTP_RANGE_START = 10**(EMAIL_OTP_NUM_DIGITS - 1)
EMAIL_OTP_RANGE_END = 10**EMAIL_OTP_NUM_DIGITS


def create_new_random_email_otp():
    otp_int = random.randint(EMAIL_OTP_RANGE_START, EMAIL_OTP_RANGE_END)
    otp_str = str(otp_int)

    otp_expiration = timezone.now() + timedelta(seconds=EMAIL_OTP_LIFESPAN)

    return otp_str, otp_expiration
