import logging

from drf_spectacular.utils import extend_schema
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from authentication.permissions import IsParentUser
from authentication.serializers.models import ParentUserSerializer
from authentication.serializers.requests import PatchParentProfileRequestSerializer
from authentication.auth_classes import DerivedUserJWTAuthentication


logger = logging.getLogger('all_apps_logger')


class ParentProfileAPIView(APIView):
    "Obtain Access and Refresh tokens from email and OTP."

    permission_classes = [IsAuthenticated, IsParentUser]
    authentication_classes = [DerivedUserJWTAuthentication]

    def get(self, request):
        logger.debug("enter_view__authentication.views.ParentProfileAPIView.get")
        response_body_serilizer = ParentUserSerializer(request.derived_user)
        return Response({
            'parent_user': response_body_serilizer.data,
        }, status=status.HTTP_200_OK)

    @extend_schema(request=PatchParentProfileRequestSerializer)
    def patch(self, request, *args, **kwargs):
        logger.debug("enter_view__authentication.views.ParentProfileAPIView.patch")

        request_body_serializer = PatchParentProfileRequestSerializer(data=request.data)
        if not request_body_serializer.is_valid():
            logger.debug(f"request_body_validation_error__error_code")
            return Response({
                'validation_errors': request_body_serializer.errors,
            }, status=status.HTTP_400_BAD_REQUEST)
        
        new_phone_number = request_body_serializer.validated_data.get('phone_number', None)
        new_full_name = request_body_serializer.validated_data.get('full_name', None)
        new_house_number = request_body_serializer.validated_data.get('house_number', None)

        user_updated = False
        if new_phone_number is not None:
            request.user.phone_number = new_phone_number
            user_updated = True
        if new_full_name is not None:
            request.user.full_name = new_full_name
            user_updated = True
        
        derived_user_updated = False
        if new_house_number is not None:
            request.derived_user.house_number = new_house_number
            derived_user_updated = True

        if user_updated:
            try:
                request.user.save()
                print(request.user)
            except:
                # TODO: more specific error
                logger.debug("failed to save user")

        if derived_user_updated:
            try:
                request.derived_user.save()
                print(request.derived_user)
            except:
                # TODO: more specific error
                logger.debug("failed to save derived user")

        response_body_serilizer = ParentUserSerializer(request.derived_user)
        return Response({
            'parent_user': response_body_serilizer.data,
        }, status=status.HTTP_200_OK)
