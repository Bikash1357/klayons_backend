from rest_framework import serializers

from core.models import Society


class SocietySerializer(serializers.ModelSerializer):
    class Meta:
        model = Society
        fields = ['id', 'name', 'city', 'state', 'zip_code']
