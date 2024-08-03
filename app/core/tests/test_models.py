"""
Test cases for models
"""
from django.test import TestCase

# Helper function to get default user model
from django.contrib.auth import get_user_model


class ModelTests(TestCase):
    """Test models"""
    def test_create_user_with_email_successful(self):
        """Test creating a new user with an email is successful"""

        email = 'test@example.com'
        password = 'testpass123'
        user = get_user_model().objects.create_user(
            email=email,
            password=password
        )

        self.assertEqual(user.email, email)

        # Check password as password is hashed by default
        self.assertTrue(user.check_password(password))

    def test_new_user_email_normalized(self):
        """Test the email for a new user is normalized"""

        sample_emails = [
            ['test1@EXAMPLE.com', 'test1@example.com'],
            ['Test2@Example.com', 'Test2@example.com'],
            ['TEST3@EXAMPLE.COM', 'TEST3@example.com'],
            ['test4@example.COM', 'test4@example.com'],
            ]

        for email, expected in sample_emails:
            user = get_user_model().objects.create_user(email, 'sample123')

            self.assertEqual(user.email, expected)

    def test_new_user_without_email_raises_error(self):
        """Test creating user without email raises ValueError"""

        with self.assertRaises(ValueError):  # Check if ValueError is raised
            get_user_model().objects.create_user(None, 'sample123')

    def test_create_new_superuser(self):
        """Test creating a new superuser"""

        user = get_user_model().objects.create_superuser(
                'test@example.com', 'test123')

        # .is_superuser is included in PermissionsMixin
        self.assertTrue(user.is_superuser)

        # .is_staff allows access to Django admin. Also included in PermissionsMixin # noqa
        self.assertTrue(user.is_staff)