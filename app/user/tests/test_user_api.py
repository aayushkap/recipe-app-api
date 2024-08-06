"""
Test cases for user api
"""

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status


# Reverse converts a URL pattern name into an actual URL.(looks like /api/before_the_:/after_the_:/) # noqa
CREATE_USER_URL = reverse("user:create")
TOKEN_URL = reverse("user:token")
ME_URL = reverse("user:me")


def create_user(**params):
    """Create a new s user"""
    return get_user_model().objects.create_user(**params)


# Public -> Unauthenticated user
class PublicUserApiTests(TestCase):
    """Test the users API (public)"""

    # Client for testing API
    def setUp(self):
        self.client = APIClient()

    def test_create_user_success(self):
        """Test creating user with valid payload is successful"""

        payload = {
            "email": "test@example.com",
            "password": "testpass",
            "name": "Test Name",
        }

        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        user = get_user_model().objects.get(email=res.data["email"])

        # If user is created successfully, check if password is correct
        self.assertTrue(user.check_password(payload["password"]))

        # Check if password is not returned in response
        self.assertNotIn("password", res.data)

    def test_user_with_email_exists_error(self):
        """Test creating a user that already exists fails"""

        payload = {
            "email": "test@example.com",
            "password": "testpass",
            "name": "Test Name",
        }

        create_user(**payload)

        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_too_short_error(self):
        """Test that the password must be more than 5 characters"""

        payload = {"email": "test@example.com", "password": "pw", "name": "Test Name"} # noqa

        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

        user_exists = get_user_model().objects.filter(email=payload["email"]).exists() # noqa

        self.assertFalse(user_exists)

    def test_create_token_for_user(self):
        """Test that a token is created for the user"""

        user_details = {
            "name": "Test Name",
            "email": "test@example.com",
            "password": "test-user-pass123",
        }

        create_user(**user_details)

        payload = {"email": user_details["email"], "password": user_details["password"]} # noqa

        res = self.client.post(TOKEN_URL, payload)

        self.assertIn("token", res.data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_create_token_bad_credentials(self):
        """Test that token is not created for invalid credentials"""

        user_details = {
            "name": "Test Name",
            "email": "test@example.com",
            "password": "test-user-pass123",
        }

        create_user(**user_details)

        payload = {"email": user_details["email"], "password": "wrong-password"} # noqa

        res = self.client.post(TOKEN_URL, payload)

        self.assertNotIn("token", res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_token_blank_password(self):
        """Test that token is not created if password is blank"""

        user_details = {
            "name": "Test Name",
            "email": "test@example.com",
            "password": "test-user-pass123",
        }

        create_user(**user_details)

        payload = {"email": user_details["email"], "password": ""}

        res = self.client.post(TOKEN_URL, payload)

        self.assertNotIn("token", res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_retrieve_user_unauthorized(self):
        """Test that authentication is required for users"""

        # Making an unauthorized request to ME_URL
        res = self.client.get(ME_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


# Endpoints that require authentication are tested here
# Private -> Authenticated user
class PrivateUserApiTests(TestCase):
    """Test API requests that require authentication"""

    def setUp(self):
        self.user = create_user(
            email="test@example.com", password="testpass", name="Test Name"
        )

        # API Test Client provided by test framework
        self.client = APIClient()

        # Force authenticate the user
        self.client.force_authenticate(user=self.user)

    def test_retrieve_profile_success(self):
        """Test retrieving profile for logged in user"""

        # Here .get is used to make a GET request to ME_URL
        res = self.client.get(ME_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, {"name": self.user.name, "email": self.user.email}) # noqa

    def test_post_me_not_allowed(self):
        """Test that POST is not allowed on the me URL"""

        # Here .post is used to make a POST request to ME_URL
        res = self.client.post(ME_URL, {})

        self.assertEqual(res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_update_user_profile(self):
        """Test updating the user profile for authenticated user"""

        payload = {"name": "New Name", "password": "newpassword123"}

        # Here .patch is used to make a PATCH request to ME_URL
        res = self.client.patch(ME_URL, payload)

        # Refresh the user object with the latest data from the database
        self.user.refresh_from_db()

        self.assertEqual(self.user.name, payload["name"])
        self.assertTrue(self.user.check_password(payload["password"]))
        self.assertEqual(res.status_code, status.HTTP_200_OK)
