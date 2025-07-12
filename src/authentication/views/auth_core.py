import logging

from django.utils import timezone
from drf_spectacular.utils import extend_schema
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenRefreshView

from authentication.logic.emailing import send_otp_email_to_user
from authentication.logic.otp import create_new_random_email_otp
from authentication.datatypes import OTPType
from authentication.models import CustomUser, ParentUser
from authentication.serializers.requests import (
    RequestParentSignupEmailOtpRequestSerializer,
    RequestLoginEmailOtpRequestSerializer,
    VerifyLoginEmailOtpRequestSerializer,
    CustomTokenRefreshSerializer,
)
from backend_main.settings import APP_MODE
from backend_main.utils.orm_utils import try_get_object_by_unique_field
from backend_main.datatypes import CustomError, CustomResult


logger = logging.getLogger('all_apps_logger')


@extend_schema(auth=[], request=RequestParentSignupEmailOtpRequestSerializer)
class RequestParentUserSignupEmailOtpAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        "Request login email OTP for a user."

        """
        Flow:
            1) Valiate request body
            2) Check if user exists for given email
                - If user exists, return that a user already exists with this email
            3) Create a new user with the provided info
            4) Generate OTP with expiration
            5) Send email to user with the generated OTP
            6) Update the user model to contain the new OTP and expiration
            7) Return success message
        """

        logger.debug("enter_view__authentication.views.RequestSignupEmailOtpAPIView.post")

        # Validate request body, validation of foreign keys and unique fields is done in the serializer
        request_body_serializer = RequestParentSignupEmailOtpRequestSerializer(data=request.data)
        if not request_body_serializer.is_valid():
            logger.debug("request_body_validation_error")
            return Response({
                'validation_errors': request_body_serializer.errors,
            }, status=status.HTTP_400_BAD_REQUEST)
        
        email = request_body_serializer.validated_data['email']
        full_name = request_body_serializer.validated_data['full_name']
        phone_number = request_body_serializer.validated_data['phone_number']
        society_id = request_body_serializer.validated_data['society_id']
        house_number = request_body_serializer.validated_data['house_number']

        # Create Custom User Model
        new_user = CustomUser.objects.create_user(
            email=email,
            full_name=full_name,
            phone_number=phone_number,
            last_sent_email_otp="0000000",
            user_type="PARENT"
        )
        _new_parent_user = ParentUser.objects.create(
            user=new_user,
            society=society_id,
            house_number=house_number
        )

        # Generate OTP
        otp_str, otp_expiration = create_new_random_email_otp()

        # Email OTP to user
        if APP_MODE != "TESTING":
            send_email_result = send_otp_email_to_user(
                new_user.email,
                new_user.full_name,
                OTPType.LOGIN,
                otp_str,
                otp_expiration
            )
        else:
            logger.info(f'send_email_aborted_in_testing_mode')
            send_email_result_data = {
                'message': "OK",
            }
            send_email_result = CustomResult(data=send_email_result_data)
        if not send_email_result.is_successful():
            send_email_result.add_to_error_call_stack("authentication.views.RequestParentUserSignupEmailOtpAPIView.post")
            return send_email_result.to_error_response()

        # Update the user model to have the new OTP and expiration
        new_user.last_sent_email_otp = otp_str
        new_user.last_sent_email_otp_expiration = otp_expiration
        new_user.last_sent_email_otp_used = False
        new_user.save()

        # Return success message
        return Response({
            'message': "OK",
        }, status=status.HTTP_200_OK)


@extend_schema(auth=[], request=RequestLoginEmailOtpRequestSerializer)
class RequestLoginEmailOtpAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        "Request login email OTP for a user."

        """
        Flow:
            1) Valiate request body
            2) Check if user exists for given email
                - If user exists, continue to (3)
                - If user does not exist, return success saying email has been sent to user.
            3) Generate OTP with expiration
            4) Send email to user with the generated OTP
            5) Update the user model to contain the new OTP and expiration
            6) Return success message
        """

        logger.debug("enter_view__authentication.views.RequestLoginEmailOtpAPIView.post")

        # Validate request body
        request_body_serializer = RequestLoginEmailOtpRequestSerializer(data=request.data)
        if not request_body_serializer.is_valid():
            logger.debug("request_body_validation_error")
            return Response({
                'validation_errors': request_body_serializer.errors,
            }, status=status.HTTP_400_BAD_REQUEST)
        
        email = request_body_serializer.validated_data['email']
        app_type = request_body_serializer.validated_data['app_type']

        # Find user with given email
        found_user = try_get_object_by_unique_field(CustomUser, 'email', email)
        if found_user is None: # if user does not exist, still respond with success
            logger.info(f'attempted_request_login_with_non_existing_user(email="{email}")')
            return Response({
                'message': "OK",
            }, status=status.HTTP_200_OK)
        
        if found_user.user_type != app_type:
            error = CustomError(
                code="attempted_login_in_wrong_app",
                caller_function="authentication.views.RequestLoginEmailOtpAPIView.post",
                response_status_code=status.HTTP_428_PRECONDITION_REQUIRED,
                detail_object={
                    'user_type': found_user.user_type,
                    'app_type': app_type,   
                }
            )
            return error.to_response()
                
        # Generate OTP
        otp_str, otp_expiration = create_new_random_email_otp()

        # Email OTP to user
        if APP_MODE != "TESTING":
            send_email_result = send_otp_email_to_user(
                found_user.email,
                found_user.full_name,
                OTPType.LOGIN,
                otp_str,
                otp_expiration
            )
        else:
            logger.info(f'send_email_aborted_in_testing_mode')
            send_email_result_data = {
                'message': "OK",
            }
            send_email_result = CustomResult(data=send_email_result_data)
        if not send_email_result.is_successful():
            send_email_result.add_to_error_call_stack("authentication.views.RequestLoginEmailOtpAPIView.post")
            return send_email_result.to_error_response()

        # Update the user model to have the new OTP and expiration
        found_user.last_sent_email_otp = otp_str
        found_user.last_sent_email_otp_expiration = otp_expiration
        found_user.last_sent_email_otp_used = False
        found_user.save()

        # Return success message
        return Response({
            'message': "OK",
        }, status=status.HTTP_200_OK)


@extend_schema(auth=[], request=VerifyLoginEmailOtpRequestSerializer)
class LoginWithEmailOtpAPIView(APIView):
    "Obtain Access and Refresh tokens from email and OTP."

    permission_classes = [AllowAny]

    @extend_schema(request=VerifyLoginEmailOtpRequestSerializer)
    def post(self, request, *args, **kwargs):
        logger.debug("enter_view__authentication.views.LoginWithEmailOtpAPIView.post")

        request_body_serializer = VerifyLoginEmailOtpRequestSerializer(data=request.data)
        if not request_body_serializer.is_valid():
            logger.debug("request_body_validation_error")
            return Response({
                'validation_errors': request_body_serializer.errors,
            }, status=status.HTTP_400_BAD_REQUEST)
        
        email = request.data['email']
        entered_otp = request.data['entered_otp']
        app_type = request.data['app_type']

        found_user = try_get_object_by_unique_field(CustomUser, "email", email)
        if found_user is None:
            error = CustomError(
                code="user_not_found",
                caller_function="authentication.views.LoginWithEmailOtpAPIView.post",
                response_status_code=status.HTTP_400_BAD_REQUEST
            )
            return error.to_response()

        if found_user.user_type != app_type:
            error = CustomError(
                code="attempted_login_in_wrong_app",
                caller_function="authentication.views.LoginWithEmailOtpAPIView.post",
                response_status_code=status.HTTP_400_BAD_REQUEST
            )
            return error.to_response()
        
        if entered_otp != found_user.last_sent_email_otp:
            error = CustomError(
                code="otp_invalid",
                caller_function="authentication.views.LoginWithEmailOtpAPIView.post",
                response_status_code=status.HTTP_401_UNAUTHORIZED
            )
            return error.to_response()
        
        if timezone.now() > found_user.last_sent_email_otp_expiration:
            error = CustomError(
                code="otp_expired",
                caller_function="authentication.views.LoginWithEmailOtpAPIView.post",
                response_status_code=status.HTTP_401_UNAUTHORIZED
            )
            return error.to_response()
        
        if found_user.last_sent_email_otp_used:
            error = CustomError(
                code="otp_already_used",
                caller_function="authentication.views.LoginWithEmailOtpAPIView.post",
                response_status_code=status.HTTP_401_UNAUTHORIZED
            )
            return error.to_response()
        
        refresh_token = RefreshToken.for_user(found_user)
        access_token = refresh_token.access_token

        found_user.last_sent_email_otp_used = True
        found_user.save()

        return Response({
            'tokens': {
                'refresh': str(refresh_token),
                'access': str(access_token),
            },
            'user': {
                'id': found_user.id,
                'type': found_user.user_type,
            }
        }, status=status.HTTP_200_OK)


@extend_schema(
    auth=[],
    request=CustomTokenRefreshSerializer,
    # need not provide responses
)
class CustomTokenRefreshView(TokenRefreshView):
    "Refresh Access token."

    permission_classes = [AllowAny]

    serializer_class = CustomTokenRefreshSerializer
