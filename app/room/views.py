from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.response import Response

from core.models import Room
from room.serializers import RoomSerializer


class RoomViewSet(viewsets.ModelViewSet):
    """Viewset for room model"""
    serializer_class = RoomSerializer
    queryset = Room.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        qs = super().get_queryset()
        user_locations_ids = self.request.user.user_locations.values_list(
            'id', flat=True
        )
        qs = qs.filter(location_id__in=user_locations_ids).order_by('-id')

        location_id = self.request.query_params.get('location')
        if location_id:
            qs = qs.filter(location_id=location_id)
        return qs

    def perform_create(self, serializer):
        location = serializer.validated_data.get("location")

        if location is None:
            raise ValidationError({"location": "Questo campo è obbligatorio."})

        user_location_ids = self.request.user.user_locations.values_list("id", flat=True)

        if location.id not in user_location_ids:
            raise PermissionDenied("Non puoi creare una room in una location che non è tua.")

        serializer.save()

    def list(self, request, *args, **kwargs):
        """list location rooms or list all locations with their rooms"""

        location_id = request.query_params.get('location')

        if location_id:
            return super().list(request, *args, **kwargs)

        qs = self.get_queryset()

        if request.query_params.get("grouped") == "true":
            grouped = {}
            for room in qs:
                loc = str(room.location_id)
                grouped.setdefault(loc, []).append({
                    'id': room.id,
                    'name': room.name
                })
            return Response(grouped)

        return super().list(request, *args, **kwargs)

    def perform_update(self, serializer):
        if "location" in serializer.validated_data:
            raise PermissionDenied("Non si puo cambiare la location di una room")

