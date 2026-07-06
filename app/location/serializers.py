"""
Serializers for Location API
"""

from rest_framework import serializers

from core.models import Location


class LocationSerializer(serializers.ModelSerializer):
    """Serializer for location"""

    class Meta:
        model = Location
        fields = ['id', 'name',]
        read_only_fields = ['id']


class LocationDetailSerializer(LocationSerializer):
    """Serializer for location detail view"""
    class Meta(LocationSerializer.Meta):
        fields = LocationSerializer.Meta.fields + ['description']
