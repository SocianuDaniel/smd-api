from rest_framework import serializers

from core.models import Room


class RoomSerializer(serializers.ModelSerializer):
    """Serialiser for model serializer"""

    class Meta:
        model = Room
        fields = ['id', 'name', 'location']
        read_only_fields = ['id', 'location']

