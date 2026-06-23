"""
Serializers for Location API
"""

from rest_framework import serializers

from core.models import Location


class LocationSerializer(serializers.ModelSerializer):
    """Serializer for location"""

    class Meta:
        model = Location
        fields = ['id', 'name', 'description']
        read_only_fields = ['id']
