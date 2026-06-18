"""
Tests for the models
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from core import models


class TestModels(TestCase):
    """Unit test for testing models"""

    def test_create_user_with_email_succesful(self):
        """test create user with given email"""
        email = "user@example.com"
        password = "pass123"
        user = get_user_model().objects.create_user(
            email=email,
            password=password
        )
        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))

    def test_new_user_normalized_email(self):
        """Test email is normalised for new users"""
        sample_emails = [
            ['test@EXAMPLE.com', 'test@example.com'],
            ['Test1@Example.com', 'Test1@example.com'],
            ['TEST2@EXAMPLE.COM', 'TEST2@example.com'],
            ['test4@example.COM', 'test4@example.com']
        ]
        for email, expected in sample_emails:
            user = get_user_model().objects.create_user(email, "pass123")
            self.assertEqual(user.email, expected)

    def test_raise_error_without_email(self):
        """test raise error if email is not present"""
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user(
                '', 'pass123'
            )

    def test_create_superuser(self):
        """Ttest for creating superusers"""
        user = get_user_model().objects.create_superuser(
            "test@emaple.com", "pass123"
        )
        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)

    def test_create_location(self):
        """Test creatinga location successful"""

        user = get_user_model().objects.create_user(
            'email@example.com',
            'test123'
        )

        location = models.Location.objects.create(
            user=user,
            name='location name',

        )

        self.assertEqual(str(location), location.name)
