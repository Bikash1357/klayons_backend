import traceback

import razorpay
from rest_framework import status

from backend_main.settings import RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET
from backend_main.datatypes import CustomResult, CustomError


class RazorpayClient:
    def __init__(self):
        self.client = razorpay.Client(auth=(
            RAZORPAY_KEY_ID,
            RAZORPAY_KEY_SECRET,
        ))
    
    def create_order(self, amount, currency="INR"):
        data = {
            'amount': amount,
            'currency': currency,
        }

        try:
            new_order = self.client.order.create(data=data)
            result_data = {
                'order': new_order,
            }
            result = CustomResult(data=result_data)
            return result
        except Exception as e:
            traceback_str = traceback.format_exc()
            error = CustomError(
                code="razorpay_create_order_exception",
                caller_function="payments.logic.razorpay_api_client.RazorpayClient.create_order",
                response_status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                exception_traceback=traceback_str
            )
            result = CustomResult(error=error)
            return result
