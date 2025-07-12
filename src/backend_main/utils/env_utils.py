import os


required_env_vars = [
    "DEBUG",
    "SECRET_KEY",
    "CS_ALLOWED_HOSTS",
    "CS_CORS_ALLOWED_ORIGINS",
    "EMAIL_OTP_NUM_DIGITS",
    "EMAIL_OTP_LIFESPAN",
    "ACCESS_TOKEN_LIFESPAN",
    "REFRESH_TOKEN_LIFESPAN",
    "ZEPTO_MAIL_API_BASE_URL",
    "ZEPTO_MAIL_SENDERS_ADDRESS",
    "ZEPTO_MAIL_SENDERS_NAME",
    "ZEPTO_MAIL_AUTH_TOKEN",
    "TESTING_DB_ACCESS_SECRET_HEADER",
    "TESTING_DB_ACCESS_SECRET",
    "MOUNT_OPENAPI_ROUTES",
    "RAZORPAY_KEY_ID",
    "RAZORPAY_KEY_SECRET",
    "RAZORPAY_WEBHOOK_SECRET",
]


def check_env_vars_not_null():
    for var_name in required_env_vars:
        var_value = os.environ.get(var_name, None)

        if var_value is None:
            print(f"Required environment variable '{var_name}' not provided.")
            exit(1)
