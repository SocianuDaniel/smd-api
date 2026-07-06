from django.contrib.auth import get_user_model
from core.models import (Location, Room)


from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient
from room.serializers import RoomSerializer

ROOMS_URL = reverse('room:room-list')


def user_rooms():
    return f"{ROOMS_URL}?grouped=true"


def rooms_by_location(location_id, **params):

    return f"{ROOMS_URL}?location={location_id}"


def room_detail(room_id):
    """url for room detail"""
    return reverse('room:room-detail', args=[room_id])


def create_location(user, **params):
    """create location for testing"""
    defaults = {
        'name': 'location name',
        'description': 'location description'
    }
    defaults.update(params)
    location = Location.objects.create(user=user, **defaults)

    return location


def create_user(**params):
    return get_user_model().objects.create_user(**params)


def create_room(location, **params):
    """create room for testing"""
    defaults = {
        'name': 'default name'
    }
    defaults.update(params)
    room = Room.objects.create(location=location, **defaults)
    return room


class PublicRoomTestAPI(TestCase):
    """TEsts for unauthenticated api"""
    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        res = self.client.get(ROOMS_URL)
        self .assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateRoomTestAPI(TestCase):
    """TEsts for authenticated user"""
    def setUp(self):
        self.client = APIClient()
        self.user = create_user(
            email='testemail@example.com',
            password='pass123'
        )
        self.location = create_location(user=self.user)
        self.client.force_authenticate(self.user)

    def test_retrive_location_rooms(self):
        """test retrive location by rooms"""
        create_room(self.location)
        create_room(self.location, name='second room name')
        url = rooms_by_location(self.location.id)
        res = self.client.get(url)
        rooms = Room.objects.filter(location=self.location).order_by('-id')
        serialiser = RoomSerializer(rooms, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serialiser.data)

    def test_retrive_rooms_for_specific_location(self):
        """test retrive only the given location"""
        location_2 = create_location(user=self.user, name='second location')
        create_room(self.location)
        create_room(location=location_2, name="my second room")
        url = rooms_by_location(self.location.id)
        res = self.client.get(url)
        rooms = Room.objects.filter(location=self.location)
        serializer = RoomSerializer(rooms, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_retrive_all_rooms_of_logged_user(self):
        location_2 = location_2 = create_location(
            user=self.user, name='second location asders'
        )
        create_room(self.location)
        create_room(location_2, name="this is the other room")
        res = self.client.get(ROOMS_URL)
        user_locations_ids = self.user.user_locations.values_list(
            'id', flat=True
        )
        rooms = Room.objects.filter(
            location_id__in=user_locations_ids
        ).order_by('-id')
        serializer = RoomSerializer(rooms, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_cant_retrive_other_user_rooms(self):
        """test doesn't retrive ayher user rooms"""
        new_user = create_user(
            email="newuser@example.com",
            password="passw123"
        )
        other_user_loc = create_location(user=new_user)
        # res = self.client.get(rooms_by_location(other_user_loc.id))
        rooms = Room.objects.filter(location=other_user_loc)
        serializer = RoomSerializer(rooms, many=True)
        print(serializer.data)
        self.assertEqual(len(serializer.data), 0)
