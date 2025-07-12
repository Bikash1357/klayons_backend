from rest_framework import serializers

from authentication.models import CustomUser, ParentUser
from core.serializers import SocietySerializer


class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['full_name', 'phone_number', 'email', 'user_type']


class ParentUserSerializer(serializers.ModelSerializer):
    user = CustomUserSerializer()
    society = SocietySerializer()

    class Meta:
        model = ParentUser
        fields = ['user', 'society', 'house_number']


class CustomUserOtpSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['last_sent_email_otp', 'last_sent_email_otp_expiration', 'last_sent_email_otp_used']
