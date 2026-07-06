"""
Views for the location files
"""

from rest_framework import viewsets
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from core.models import Location
from location import serializers


class LocationViewSet(viewsets.ModelViewSet):
    """View for manage recipe APIs"""

    serializer_class = serializers.LocationDetailSerializer
    queryset = Location.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Retrive locations for the authenticated user"""
        return self.queryset.filter(user=self.request.user).order_by('-id')

    def get_serializer_class(self):
        """Return the serializer class for request"""
        if self.action == "list":
            return serializers.LocationSerializer
        return self.serializer_class

    def perform_create(self, serializer):
        """Create a new location"""
        serializer.save(user=self.request.user)
