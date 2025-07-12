from enum import Enum
import json
import logging

from rest_framework.response import Response

from backend_main.core.error_handling import generate_error_id
from backend_main.settings import DEBUG


logger = logging.getLogger('all_apps_logger')


class AppType(Enum):
    PARENT = 'PARENT'
    INSTRUCTOR = 'INSTRUCTOR'


class CustomError():
    nullable_attrs = [
        '__user_friendly_error',
        '__detail',
        '__detail_object',
        '__exception_traceback',
    ]
    debug_attrs = [
        'exception_traceback',
    ]
    
    def __init__(
            self,
            code,
            caller_function,
            response_status_code,
            detail=None,
            user_friendly_error=None,
            detail_object=None,
            exception_traceback=None,
        ):
        self.__id = generate_error_id()
        self.__code = code
        self.__response_status_code = response_status_code
        self.__user_friendly_error = user_friendly_error
        self.__detail = detail
        self.__detail_object = detail_object
        self.__exception_traceback = exception_traceback
        
        self.__reverse_stack_trace = [
            caller_function,
        ]
    
    def add_to_call_stack(self, function_name):
        self.__reverse_stack_trace.append(function_name)
    
    def to_json(self):
        error_json = {
            'id': self.__id,
            'code': self.__code,
            'traceback': self.__reverse_stack_trace,
        }

        if self.__user_friendly_error is not None:
            error_json['user_friendly_error'] = self.__user_friendly_error
        if self.__detail is not None:
            error_json['detail'] = self.__detail
        if self.__detail_object is not None:
            error_json['detail_object'] = self.__detail_object
        if self.__exception_traceback is not None:
            error_json['exception_traceback'] = self.__exception_traceback

        for attr_name in self.nullable_attrs:
            attr_value = getattr(self, attr_name, None)
            if attr_value is None:
                continue
            
            error_json[attr_name] = attr_value

        return error_json

    def create_log_with_json(self, error_json):
        logger.error(json.dumps(error_json))

    def create_log(self):
        error_json = self.to_json()
        self.create_log_with_json(error_json)

    def to_response(self):
        error_json = self.to_json()
        self.create_log_with_json(error_json)

        if not DEBUG:
            for attr_name in self.debug_attrs:
                if error_json.get(attr_name, None) is not None:
                    del error_json[attr_name]

        return Response(error_json, self.__response_status_code)


class CustomResult():
    def __init__(self, data=None, error=None):
        if data is not None:
            self.__success = True
        elif error is not None:
            self.__success = False
        else:
            raise ValueError("Either data or error should be not None when initializing CustomResult.")
        
        self.__data = data
        self.__error = error
    
    def is_successful(self):
        return self.__success
    
    def get_data(self):
        if not self.__success:
            raise ValueError("Cannot get data if result is not successful.")
        
        return self.__data
    
    def add_to_error_call_stack(self, function_name):
        if self.__success:
            raise ValueError("Cannot add to error_call_stack if result is successful.")

        self.__error.add_to_call_stack(function_name)
    
    def to_error_response(self):
        if self.__success:
            raise ValueError("Cannot convert to error response if result is successful.")
        
        return self.__error.to_response()
