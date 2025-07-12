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


@extend_schema(
    auth=[],
    request=None,
    responses={
        200: SocietySerializer(many=True)
    },
)
class SocietyListView(generics.ListAPIView):
    "Get all registered societies."

    permission_classes = [AllowAny]
    
    queryset = Society.objects.all()
    serializer_class = SocietySerializer


class GetOtpForUserAPIView(APIView):
    def get(self, request):
        db_access_secret_validation_result = validate_db_access_secret(request)
        if not db_access_secret_validation_result['success']:
            if db_access_secret_validation_result['error']['code'] == "invalid_db_access_secret":
                response_status = status.HTTP_401_UNAUTHORIZED
            elif db_access_secret_validation_result['error']['code'] == "no_db_access_secret_header_provided":
                response_status = status.HTTP_401_UNAUTHORIZED
            elif db_access_secret_validation_result['error']['code'] == "not_in_the_mood_for_this":
                response_status = status.HTTP_418_IM_A_TEAPOT
            else:
                response_status = status.HTTP_400_BAD_REQUEST
            
            response_body_serializer = ErrorResponseSerializer(db_access_secret_validation_result['error'])
            return Response(response_body_serializer.data, status=response_status)

        user_email = request.query_params.get("user_email", None)
        if user_email is None:
            response_body_serializer = ErrorResponseSerializer({
                'code': "validation_error__query",
                'detail': "query_param__user_email__not_provided",
            })
            return Response(response_body_serializer.data, status=status.HTTP_400_BAD_REQUEST)

        found_user = try_get_object_by_unique_field(CustomUser, 'email', user_email)
        if found_user is None:
            response_body_serializer = ErrorResponseSerializer({
                'code': "user_not_found",
                'detail': f"user_not_found_for_email__{user_email}",
            })
            return Response(response_body_serializer.data, status=status.HTTP_400_BAD_REQUEST)
        
        return Response({
            'last_sent_email_otp': found_user.last_sent_email_otp,
            'last_sent_email_otp_expiration': found_user.last_sent_email_otp_expiration,
            'last_sent_email_otp_used': found_user.last_sent_email_otp_used,
        }, status=status.HTTP_200_OK)
