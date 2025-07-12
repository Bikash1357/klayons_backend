from datetime import datetime

from backend_main.core.emailing import send_email_to_user
from backend_main.utils.datetime_utils import time_diff_to_string


def otp_type_to_email_template_name(otp_type):
    template_name = f"request_{str(otp_type.value).lower()}_otp"
    return template_name


def otp_expiration_to_display_string(otp_expiration):
    if otp_expiration.tzinfo is not None:
        current_time = datetime.now(otp_expiration.tzinfo)
    else:
        current_time = datetime.now()

    otp_expiration_time_delta = otp_expiration - current_time

    otp_expiration_time_delta_string = time_diff_to_string(otp_expiration_time_delta)
    return otp_expiration_time_delta_string


def send_otp_email_to_user(user_email, user_name, otp_type, otp_str, otp_expiration):
    email_template_name = otp_type_to_email_template_name(otp_type)
    otp_expiration_time_delta_string = otp_expiration_to_display_string(otp_expiration)
    
    email_template_data = {
        'user_name': user_name,
        'otp_str': otp_str,
        'otp_expiration': otp_expiration_time_delta_string,
    }

    send_email_result = send_email_to_user(
        user_email,
        user_name,
        email_template_name,
        email_template_data
    )
    if not send_email_result.is_successful():
        send_email_result.add_to_error_call_stack("authentication.logic.emailing.send_otp_email_to_user")
    return send_email_result
