import datetime
import json
import logging
import uuid

from rest_framework.response import Response


logger = logging.getLogger('all_apps_logger')


def generate_error_id():
    current_time = datetime.datetime.now()
    current_time_str =  current_time.strftime("%Y-%m-%d-%H-%M-%S") + f"-{current_time.microsecond}"

    error_id = f"{current_time_str}--{uuid.uuid4()}"
    return error_id
