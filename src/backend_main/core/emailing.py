import json
import os

from backend_main.api_clients.zepto_mail import ZeptoMailApiClient
from backend_main.core.templating import template_name_to_type, populate_template
from backend_main.settings import (
    ZEPTO_MAIL_API_BASE_URL,
    ZEPTO_MAIL_AUTH_TOKEN,
    ZEPTO_MAIL_SENDERS_ADDRESS,
    ZEPTO_MAIL_SENDERS_NAME,
    EMAIL_TEMPLATES_DIR,
)


emailer_api_client = ZeptoMailApiClient(ZEPTO_MAIL_API_BASE_URL, ZEPTO_MAIL_AUTH_TOKEN)

def load_email_subjects():
    subjects_json_file = os.path.join(EMAIL_TEMPLATES_DIR, "subjects.json")
    with open(subjects_json_file, 'r', encoding="utf-8") as f:
        email_subjects = json.load(f)
    
    return email_subjects
email_subjects = load_email_subjects()


def get_email_subject(template_name, template_fields):
    email_subject = email_subjects[template_name]
    return email_subject


def get_email_body_type_and_content(template_name, template_fields):
    template_type = template_name_to_type(template_name)

    template_file_name = template_name + "." + template_type

    populated_template_str = populate_template(template_file_name, template_fields)

    return template_type, populated_template_str


def send_email_to_user(user_email, user_name, template_name, template_fields):
    from_info = {
        'address': ZEPTO_MAIL_SENDERS_ADDRESS,
        'name': ZEPTO_MAIL_SENDERS_NAME 
    }
    to_info = [{
        'email_address': {
            'address': user_email,
            'name': user_name,
        },
    }]
    
    subject = get_email_subject(template_name, template_fields)
    if subject is None:
        # We have a problem
        pass

    body_type, body_content = get_email_body_type_and_content(template_name, template_fields)
    if body_type is None:
        # We have a problem
        pass
    if body_content is None:
        # We have a problem
        pass
    
    send_email_result = emailer_api_client.send_email(
        from_info,
        to_info,
        [],
        [],
        subject,
        body_type,
        body_content
    )
    if not send_email_result.is_successful():
        send_email_result.add_to_error_call_stack("backend_main.core.emailing.send_email_to_user")
    return send_email_result
