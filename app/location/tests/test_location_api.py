from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient
from core.models import Location
from location.serializers import LocationSerializer


LOCATIONS_URL = reverse('location:location-list')


def create_location(user, **params):
    """create and return location sample"""
    defaults = {
        'name': 'location name',
        'description': 'Sample description '
    }
    defaults.update(params)
    location = Location.objects.create(user=user, **defaults)
    return location


class PublicLocationApi(TestCase):
    """Test unauthenticated api requests"""
    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        """Test auth is required to call API"""
        res = self.client.get(LOCATIONS_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateLocationApiTests(TestCase):
    """ Test authenticated API requests"""
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            'user@example.com',
            'testpass123'
        )
        self.client.force_authenticate(self.user)

    def test_retrive_locations(self):
        """test retrive a list of locations"""
        create_location(self.user)
        create_location(self.user)
        res = self.client.get(LOCATIONS_URL)

        locations = Location.objects.all().order('-id')
        serializer = LocationSerializer(locations, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_location_list_limited_to_user(self):
        """test list of locations is limited to authenticated user"""

        # todo create other user
        other_user = get_user_model().objects.create_user(
            'other@example.com',
            'testpass1234'
        )

        create_location(user=other_user)
        create_location(user=self.user)

        res = self.client.get(LOCATIONS_URL)
        locations = Location.objects.filter(user=self.user)
        serializer = LocationSerializer(locations, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)
