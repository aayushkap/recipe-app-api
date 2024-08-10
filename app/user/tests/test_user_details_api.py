"""
Test the user details API
"""

from django.urls import reverse
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APIClient
from core.models import UserDetails


ADD_USER_DETAILS_URL = reverse('user:details')
MANAGE_USER_DETAILS_URL = reverse('user:me_details')


def create_user(**params):
    return get_user_model().objects.create_user(**params)


class PublicUserDetailsApiTests(TestCase):
    """Test the public access to the UserDetails API"""

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        """Test that authentication is required to access UserDetails"""
        res = self.client.get(ADD_USER_DETAILS_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateUserDetailsApiTests(TestCase):
    """Test the authorized user details API"""

    def setUp(self):
        self.user = create_user(email='test@example.com', password='testpass123') # noqa
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_retrieve_user_details(self):
        """Test retrieving user details"""
        UserDetails.objects.create(user=self.user, age=32, country="Country", city="City", favorite_food="Pizza") # noqa

        res = self.client.get(MANAGE_USER_DETAILS_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        self.assertEqual(res.data['age'], 32)

    def test_create_user_details(self):
        """Test creating user details"""
        payload = {
            "age": 25,
            "country": "Country",
            "city": "City",
            "favorite_food": "Sushi",
        }
        res = self.client.post(ADD_USER_DETAILS_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        details = UserDetails.objects.get(user=self.user)
        self.assertEqual(details.age, 25)

    def test_partial_update_user_details(self):
        """Test updating user details with patch"""
        UserDetails.objects.create(user=self.user, age=32, country="Country", city="City", favorite_food="Pizza") # noqa

        payload = {
            "age": 30,
        }

        self.client.patch(MANAGE_USER_DETAILS_URL, payload)

        details = UserDetails.objects.get(user=self.user)
        self.assertEqual(details.age, 30)

    def test_create_user_details_when_already_exists(self):
        """Test updating user details when already exists"""
        UserDetails.objects.create(user=self.user, age=32, country="Country", city="City", favorite_food="Pizza") # noqa

        payload = {
            "age": 25,
            "country": "UAE",
            "city": "Dubai",
            "favorite_food": "Sushi",
        }

        res = self.client.post(ADD_USER_DETAILS_URL, payload)

        # Update the user details if already exists
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        details = UserDetails.objects.get(user=self.user)
        self.assertEqual(details.age, 25)
        self.assertEqual(details.favorite_food, "Sushi")
        self.assertEqual(details.city, "Dubai")
        self.assertEqual(details.country, "UAE")
