from drf_spectacular.utils import extend_schema
from rest_framework import generics, status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from authentication.models import CustomUser
from authentication.serializers.models import CustomUserOtpSerializer
from backend_main.serializers.common import ErrorResponseSerializer
from backend_main.utils.auth_utils import validate_db_access_secret
from backend_main.utils.orm_utils import try_get_object_by_unique_field
from core.models import Society
from core.serializers import SocietySerializer

from django.db import transaction
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication

from authentication.permissions import IsParentUser
from activities.models import ActivityInstance, ActivityBooking, Child, PaymentPendingActivityBooking
from payments.serializers import CreateActivityBookingsOrderRequestSerializer
from payments.models import Order
from payments.logic.razorpay_api_client import RazorpayClient
from backend_main.settings import RAZORPAY_WEBHOOK_SECRET
from authentication.models import ParentUser
from backend_main.utils.orm_utils import try_get_object_by_unique_field
from backend_main.datatypes import CustomError

import hmac
import hashlib
import json

import logging
import random


razorpay_client = RazorpayClient()


class CreateActivityBookingsOrder(APIView):
    # permission_classes = [IsAuthenticated, IsParentUser]
    # # authentication_classes = [JWTAuthentication]

    def post(self, request):
        total_cost = random.randint(100, 1000)

        create_razorpay_order_result = razorpay_client.create_order(total_cost)
        if not create_razorpay_order_result.is_successful():
            create_razorpay_order_result.add_to_error_call_stack("payments.views.CreateActivityBookingsOrder.post")
            return create_razorpay_order_result.to_error_response()
        
        create_razorpay_order_data = create_razorpay_order_result.get_data()
        razorpay_order = create_razorpay_order_data['order']

        user = ParentUser.objects.get(id=1)

        new_order = Order.objects.create(
            # parent_user=request.derived_user,
            parent_user=user,
            amount=razorpay_order['amount'],
            currency=razorpay_order['currency'],
            razorpay_order_id=razorpay_order['id'],
            razorpay_receipt=razorpay_order['receipt'],
            payment_completed=False
        )

        return Response({
            'data': {
                'razorpay_order': razorpay_order,
            },
        }, status=status.HTTP_201_CREATED)


        request_body_serializer = CreateActivityBookingsOrderRequestSerializer(data=request.data)
        if not request_body_serializer.is_valid():
            # TODO: handle error
            pass

        activity_instance_and_children_pairs = request.data['activity_instance_and_children_pairs']
        
        # Verify all children are of the parent user who is making the request
        all_child_ids = []
        for activity_instance_and_children_pair in activity_instance_and_children_pairs:
            child_ids = activity_instance_and_children_pair['child_ids']
            all_child_ids += child_ids
        
        all_child_ids = list(set(all_child_ids))
        for child_id in all_child_ids:
            child_object = Child.objects.get(child_id)
            if child_object.parent_user != request.derived_user:
                # TODO: return error
                pass

        with transaction.atomic():
            total_cost = 0.0
            for activity_instance_and_children_pair in activity_instance_and_children_pairs:
                activity_instance_id = activity_instance_and_children_pair['activity_instance']
                child_ids = activity_instance_and_children_pair['child_ids']
                num_children = len(child_ids)

                activity_instance = ActivityInstance.objects.get(activity_instance_id)

                if activity_instance.capacity < num_children:
                    # TODO: respond with error
                    pass

                total_cost += activity_instance.cost * num_children

            # Create Razorpay Order
            create_razorpay_order_result = razorpay_client.create_order(total_cost)
            if not create_razorpay_order_result['success']:
                transaction.set_rollback(True)
                # TODO: return error response
            
            razorpay_order = create_razorpay_order_result['data']['order']

            # Create order
            new_order = Order.objects.create(
                parent_user=request.derived_user,
                amount=razorpay_order['amount'],
                currency=razorpay_order['currenty'],
                razorpay_order_id=razorpay_order['id'],
                razorpay_receipt=razorpay_order['receipt']
            )

            for activity_instance_and_children_pair in activity_instance_and_children_pairs:
                activity_instance_id = activity_instance_and_children_pair['activity_instance']
                child_ids = activity_instance_and_children_pair['child_ids']
                num_children = len(child_ids)

                activity_instance = ActivityInstance.objects.get(activity_instance_id)
                activity_instance.capacity -= num_children
                activity_instance.save()

                payment_pending_booking = PaymentPendingActivityBooking.objects.create(
                    parent_user=request.derived_user,
                    activity_instance=activity_instance,
                    order=new_order,
                )
                payment_pending_booking.children.set(child_ids)
        
        return Response({
            'order': razorpay_order,
        }, status=status.HTTP_201_CREATED)


class VerifyPaymentWebhook(APIView):
    def post(self, request):
        raw_body = request.body

        # Verify Razorpay Signature
        provided_signature = request.headers.get('x-razorpay-signature', None)
        if not provided_signature:
            error = CustomError(
                code="no_razorpay_signature_provided",
                caller_function="payments.views.VerifyPaymentWebhook.post",
                response_status_code=status.HTTP_403_FORBIDDEN
            )
            return error.to_response()

        expected_signature = hmac.new(
            key=RAZORPAY_WEBHOOK_SECRET.encode(),
            msg=raw_body,
            digestmod=hashlib.sha256
        ).hexdigest()

        if not hmac.compare_digest(expected_signature, provided_signature):
            error = CustomError(
                code="invalid_razorpay_signature",
                caller_function="payments.views.VerifyPaymentWebhook.post",
                response_status_code=status.HTTP_401_UNAUTHORIZED
            )
            return error.to_response()

        # Extract Payment and Order Info
        payload = request.data['payload']
        payment_entity = payload['payment']['entity']

        payment_id = payment_entity['id']
        payment_status = payment_entity['status']
        order_id = payment_entity['order_id']

        # Check Payment Status
        if payment_status != "captured":
            error = CustomError(
                code="payment_not_captured",
                caller_function="payments.views.VerifyPaymentWebhook.post",
                response_status_code=status.HTTP_400_BAD_REQUEST
            )
            return error.to_response()
                
        # Check Order Object
        order = try_get_object_by_unique_field(Order, 'razorpay_order_id', order_id)
        if order is None:
            # TODO: This is a weird situation, should be handled in a way that user does not lose their money
            error = CustomError(
                code="invalid_razorpay_order_id",
                caller_function="payments.views.VerifyPaymentWebhook.post",
                response_status_code=status.HTTP_400_BAD_REQUEST
            )
            return error.to_response()

        order.razorpay_payment_id = payment_id
        order.payment_completed = True
        # Mark activities as booked in an atomic transaction
        order.save()

        return Response({
            'data': {
                'message': "OK",
            },
        }, status=status.HTTP_200_OK) 
