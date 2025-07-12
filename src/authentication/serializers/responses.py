from rest_framework import serializers

from backend_main.datatypes import AppType


class VerifyLoginEmailOtpResponseSerializer(serializers.Serializer):
    class TokensSerializer(serializers.Serializer):
        access = serializers.CharField()
        refresh = serializers.CharField()

    class UserSerializer(serializers.Serializer):
        id = serializers.IntegerField()
        type = serializers.ChoiceField(choices=[(e.value, e.name) for e in AppType])

    tokens = TokensSerializer()
    base_user = UserSerializer()
    derived_user = UserSerializer()


class ParentProfileResponseSerializer(serializers.Serializer):
    pass
