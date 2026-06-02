"""
Tests for the user API
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

# url map fro the create user
CREATE_USER_URL = reverse('user:create')
TOKEN_URL = reverse('user:token')
ME_URL = reverse('user:me')


def create_user(**params):
    return get_user_model().objects.create_user(**params)


class PublicUserAPiTests(TestCase):
    """Test the public features of the user api"""
    def setUp(self):
        self.client = APIClient()

    def test_create_user_success(self):
        """TEst creating a user in successful"""
        payload = {
            'email': 'test@example.com',
            'password': 'testpass123',
            'name': 'Test Name',
        }
        # call the create endpoint of api
        res = self.client.post(CREATE_USER_URL, payload)
        # ----------------------------------------------

        # check if status code is 201 created
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        # -----------------------------------------------

        # retrive user with given email and check pass with password payload
        user = get_user_model().objects.get(email=payload['email'])
        self.assertTrue(user.check_password(payload['password']))
        # -----------------------------------------------

        # test if hash password is not returned
        self.assertNotIn('password', res.data)
        # -----------------------------------------------

    def test_user_with_email_exists_error(self):
        """Test error returned if user with email exists"""
        payload = {
            'email': 'test@example.com',
            'password': 'testpass123',
            'name': 'Test Name',
        }
        # create a user with payload details
        create_user(**payload)
        # ----------------------------------

        # make a request to create a user with same payload
        res = self.client.post(CREATE_USER_URL, payload)
        # -------------------------------------------------

        # Test if return a 400 bad request
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        # -------------------------------------------------

    def test_password_too_short_error(self):
        """Test an error is returned if password il less then 5 chars"""
        payload = {
            'email': 'test@example.com',
            'password': 'pwsd',
            'name': 'Test Name',
        }

        # make request to create user
        res = self.client.post(CREATE_USER_URL, payload)
        # ---------------------------------------------------
        # test status code is 400 BAD REQUEST
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        # ---------------------------------------------------
        # test if user with given email exists
        user_exists = get_user_model().objects.filter(
            email=payload['email']
        ).exists()
        self.assertFalse(user_exists)
        # ---------------------------------------------------

    def test_create_token_for_user(self):
        """ test tken is created for user with valid credentials"""

        user_details = {
            'email': 'test@email.com',
            'password': 'password123',
            'name': 'Test Name',
            'is_active': True
        }
        create_user(**user_details)
        payload = {
            'email': user_details['email'],
            'password': user_details['password']
        }

        # make a request to create a token for user with cred
        res = self.client.post(TOKEN_URL, payload)
        # ----------------------------------------

        # test if token is present in returned data
        self.assertIn('token', res.data)
        # ----------------------------------------

        # test is returned 200 ok
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        # ----------------------------------------

    def test_create_token_bad_credentials(self):
        """test if if created a token with bad password"""
        # create user
        create_user(email='test@example.com', password='goodpass')
        # ----------------------------------------

        # make request with bad credentials
        payload = {'email': 'test@example.com',
                   'password': 'badpass'
                   }
        res = self.client.post(TOKEN_URL, payload)
        # ----------------------------------------

        # tet ilf token is not in returned data
        self.assertNotIn('token', res.data)
        # ----------------------------------------

        # test if returned 400 bad request
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

        # ----------------------------------------

    def test_create_token_blank_password(self):
        """Test if token is created with blank passowrd"""

        # make request with a blank password
        payload = {
            'email': 'test@emample.com',
            'password': ''
        }
        res = self.client.post(TOKEN_URL, payload)
        # ------------------------------------------

        # test if token is returned and 400 bad request
        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_retrive_user_unauthorized(self):
        """test authentication is required for users"""
        res = self.client.get(ME_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateUserApiTests(TestCase):
    """Test API requests that require authentication"""
    def setUp(self):
        self.user = create_user(
            email='test@example.com',
            password='test123',
            name='Test Name',
            is_active=True
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_retrive_profile_success(self):
        """Test retriving profile for logged user"""
        res = self.client.get(ME_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data,
                         {
                             'email': self.user.email,
                             'name': self.user.name
                         }
                         )

    def test_post_me_not_allowed(self):
        """Test POST is not allowed for the me endpoint"""
        res = self.client.post(ME_URL, {})

        self.assertEqual(res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_update_user_profile(self):
        """Test updating the user profile for the authenticated users"""
        payload = {'name': 'Updated name', 'password': 'newpassword123'}
        res = self.client.patch(ME_URL, payload)
        self.user.refresh_from_db()
        self.assertEqual(self.user.name, payload['name'])
        self.assertTrue(self.user.check_password(payload['password']))
        self.assertEqual(res.status_code, status.HTTP_200_OK)
