from rest_framework import serializers


class UserFriendlyMessageSerializer(serializers.Serializer):
        title = serializers.CharField()
        content = serializers.CharField()


class ErrorResponseSerializer(serializers.Serializer):
    code = serializers.CharField()
    detail = serializers.CharField()
    user_friendly_message = UserFriendlyMessageSerializer(required=False, allow_null=True)
    detail_object = serializers.DictField(required=False, allow_null=True)


class MessageResponseSerializer(serializers.Serializer):
    message = serializers.CharField()
