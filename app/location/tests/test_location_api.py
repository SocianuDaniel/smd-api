from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient
from core.models import Location
from location.serializers import (
    LocationSerializer, LocationDetailSerializer)


LOCATIONS_URL = reverse('location:location-list')


def detail_url(location_id):
    """create ad return a location detail"""
    return reverse('location:location-detail', args=[location_id])


def create_location(user, **params):
    """create and return location sample"""
    defaults = {
        'name': 'location name',
        'description': 'Sample description '
    }
    defaults.update(params)
    location = Location.objects.create(user=user, **defaults)
    return location


def create_user(**params):
    return get_user_model().objects.create_user(**params)


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
        self.user = create_user(
            email='user@example.com',
            password='testpass123'
        )
        self.client.force_authenticate(self.user)

    def test_retrive_locations(self):
        """test retrive a list of locations"""
        create_location(self.user)
        create_location(self.user)
        res = self.client.get(LOCATIONS_URL)

        locations = Location.objects.all().order_by('-id')
        serializer = LocationSerializer(locations, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_location_list_limited_to_user(self):
        """test list of locations is limited to authenticated user"""

        # todo create other user
        other_user = create_user(
            email='other@example.com',
            password='testpass1234'
        )

        create_location(user=other_user)
        create_location(user=self.user)

        res = self.client.get(LOCATIONS_URL)
        locations = Location.objects.filter(user=self.user)
        serializer = LocationSerializer(locations, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_get_location_detail(self):
        """Test get location detail"""
        location = create_location(user=self.user)
        url = detail_url(location.id)
        res = self.client.get(url)

        serializer = LocationDetailSerializer(location)
        self.assertEqual(res.data, serializer.data)

    def test_create_location(self):
        """Test creating a location"""
        payload = {
            'name': 'test name',
            'description': 'my test description'
        }
        res = self.client.post(LOCATIONS_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        location = Location.objects.get(id=res.data['id'])

        for k, v in payload.items():
            self.assertEqual(getattr(location, k), v)
        self.assertEqual(location.user, self.user)

    def test_partial_update(self):
        """test for partial update"""
        original_name = "original name"
        location = create_location(
            self.user,
            name=original_name,
            description="initial description"
        )
        payload = {
            'description': 'changed description'
        }
        url = detail_url(location.id)
        res = self.client.patch(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        location.refresh_from_db()
        self.assertEqual(location.description, payload['description'])
        self.assertEqual(location.name, original_name)

    def test_full_update(self):
        """test full update of a location"""
        location = create_location(
            user=self.user,
            name="test name",
            description="ytest description"
        )
        payload = {
            'name': 'new name',
            'description': 'new desription'
        }
        url = detail_url(location.id)
        res = self.client.put(url, payload)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        location.refresh_from_db()
        for k, v in payload.items():
            self.assertEqual(getattr(location, k), v)
        self.assertEqual(location.user, self.user)

    def test_return_eror_if_user_change(self):
        """test return error if user try to change"""
        location = create_location(self.user)
        new_user = create_user(
            email="newuser@example.com",
            password='testpass123'
        )
        url = detail_url(location.id)
        payload = {
            'user': new_user.id
        }
        self.client.patch(url, payload)
        location.refresh_from_db()
        self.assertEqual(location.user, self.user)

    def test_delete_object(self):
        """test location is deleted"""
        location = create_location(self.user)
        url = detail_url(location.id)

        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Location.objects.filter(id=location.id).exists())

    def test_other_user_location_error(self):
        """test if error is returned if try to delete aonother user location"""
        new_user = create_user(
            email="newuser@example.com",
            password="pass123"
        )
        location = create_location(new_user)
        url = detail_url(location.id)
        res = self.client.delete(url)
        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)
        self.assertTrue(Location.objects.filter(id=location.id).exists())
