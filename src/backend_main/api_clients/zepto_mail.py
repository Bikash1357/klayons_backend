import threading

import requests
from rest_framework import status

from backend_main.datatypes import CustomResult, CustomError


class ZeptoMailApiClient:
    def __init__(self, base_url, auth_token):
        self._thread_local = threading.local()

        self._base_url = base_url
        self._auth_token = auth_token

        self.urls = {
            'send_email': f"{self._base_url}/email",
        }
    
    def _get_requests_session(self):
        if not hasattr(self._thread_local, 'session'):
            self._thread_local.requests_session = requests.Session()
            self._thread_local.requests_session.headers.update({
                'Authorization': self._auth_token,
            })
        
        return self._thread_local.requests_session

    def send_email(self, from_info, to_info, cc_info, reply_to_info, subject, body_type, body_content):
        requests_session = self._get_requests_session()

        body_content_key = f"{body_type}body"

        request_body = {
            'from': from_info,
            'to': to_info,
            'cc': cc_info,
            'reply_to': reply_to_info,
            'subject': subject,
            body_content_key: body_content,
        }

        response = requests_session.post(self.urls['send_email'], json=request_body)

        if response.status_code != 201:
            error = CustomError(
                code="zepto_mail_non_200_response",
                caller_function="backend_main.api_clients.zepto_mail.ZeptoMailApiClient.send_email",
                response_status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
            result = CustomResult(error=error)
            return result
        
        data = {
            'message': "OK",
        }
        result = CustomResult(data=data)
        return result
