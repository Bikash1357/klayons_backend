from django.utils import timezone
from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.serializers import TokenRefreshSerializer
from rest_framework_simplejwt.state import token_backend

from authentication.models import CustomUser, Society
from backend_main.datatypes import AppType
from backend_main.utils.orm_utils import try_get_object_by_unique_field


class RequestParentSignupEmailOtpRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()
    full_name = serializers.CharField(max_length=63)
    phone_number = serializers.CharField(max_length=15)
    society_id = serializers.PrimaryKeyRelatedField(queryset=Society.objects.all())
    house_number = serializers.CharField(max_length=31)

    def validate_email(self, value):
        found_user = try_get_object_by_unique_field(CustomUser, 'email', value)
        if found_user is not None:
            raise serializers.ValidationError("email_already_taken")
        
        return value

    def validate_phone_number(self, value):
        found_user = try_get_object_by_unique_field(CustomUser, 'phone_number', value)
        if found_user is not None:
            raise serializers.ValidationError("phone_number_already_taken")
        
        return value


class RequestLoginEmailOtpRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()
    app_type = serializers.ChoiceField(choices=[(tag.value, tag.name) for tag in AppType])


class VerifyLoginEmailOtpRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()
    entered_otp = serializers.CharField()
    app_type = serializers.ChoiceField(choices=[(tag.value, tag.name) for tag in AppType])

    # def validate(self, attrs):
    #     email = attrs.get('email')
    #     entered_otp = attrs.get('entered_otp')
    #     app_type = attrs.get('app_type')

    #     found_user = try_get_object_by_unique_field(CustomUser, "email", email)
    #     if found_user is None:
    #         raise serializers.ValidationError("user_not_found")
        
    #     if found_user.user_type != app_type:
    #         raise serializers.ValidationError("attempted_login_in_wrong_app")

    #     if entered_otp != found_user.last_sent_email_otp:
    #         raise serializers.ValidationError("otp_invalid")

    #     if timezone.now() > found_user.last_sent_email_otp_expiration:
    #         raise serializers.ValidationError("otp_expired")
        
    #     if found_user.last_sent_email_otp_used:
    #         raise serializers.ValidationError("otp_already_used")

    #     # Generate tokens
    #     refresh_token = RefreshToken.for_user(found_user)
    #     access_token = refresh_token.access_token

    #     return {
    #         'refresh': str(refresh_token),
    #         'access': str(access_token),
    #         'user': {
    #             'id': found_user.id,
    #             'type': found_user.user_type,
    #         }
    #     }


class CustomTokenRefreshSerializer(TokenRefreshSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        
        refresh_token_str = attrs['refresh']
        refresh_token = RefreshToken(refresh_token_str)

        decoded_payload = token_backend.decode(refresh_token_str, verify=True)
        user_id = decoded_payload['user_id']

        found_user = try_get_object_by_unique_field(CustomUser, 'id', user_id)
        if found_user is None:
            serializers.ValidationError("invalid_refresh_token")
        
        access_token = refresh_token.access_token

        data['access'] = str(access_token)

        return data

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        return token


class PatchParentProfileRequestSerializer(serializers.Serializer):
    phone_number = serializers.CharField(max_length=15, required=False, allow_blank=True)
    full_name = serializers.CharField(max_length=63, required=False, allow_blank=True)
    house_number = serializers.CharField(max_length=31, required=False, allow_blank=True)
