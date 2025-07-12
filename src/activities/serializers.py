from rest_framework import serializers

from activities.models import Child, ActivityCategory, ActivityInstance, ActivitySession


class ChildSerializer(serializers.ModelSerializer):
    interested_in_activity_categories = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=ActivityCategory.objects.all(),
        required=False,
    )

    class Meta:
        model = Child
        fields = [
            'id',
            'full_name',
            'date_of_birth',
            'gender',
            'interested_in_activity_categories',
        ]


class ActivityInstanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = ActivityInstance
        fields = "__all__"


class ActivitySessionSerializer(serializers.ModelSerializer):
    activity_instance_name = serializers.SerializerMethodField()

    class Meta:
        model = ActivitySession
        fields = [
            "id",
            "activity_instance",
            "activity_instance_name",
            "start_date_time",
            "duration",
            "title",
            "description",
            "number",
        ]

    def get_activity_instance_name(self, obj):
        return str(obj.activity_instance)
