from rest_framework import serializers

from activities.models import ActivityInstance, ActivityBooking, Child


class ActivityInstanceAndChildrenPairSerializer(serializers.Serializer):
    activity_instance = serializers.PrimaryKeyRelatedField(
        queryset=ActivityInstance.objects.all()
    )
    children = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Child.objects.all()
    )


class CreateActivityBookingsOrderRequestSerializer(serializers.Serializer):
    activity_instance_and_children_pairs = ActivityInstanceAndChildrenPairSerializer(many=False)
