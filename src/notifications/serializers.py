from rest_framework import serializers

from notifications.models import Notification


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ['id', 'is_read', 'created_at', 'title', 'content', 'navigate_to_type', 'navigate_to_id']
