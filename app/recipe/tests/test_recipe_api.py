"""
Test the recipe API
"""
from decimal import Decimal
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient
from core.models import Recipe

from recipe.serializers import (
    RecipeSerializer,  # Recipe Preview Serializer
    RecipeDetailSerializer  # Recipe Detail Serializer
)

RECIPES_URL = reverse('recipe:recipe-list')


# Each detail URL is different, depending on the recipe ID. Hence, we need a helper function to generate the URL # noqa
def detail_url(recipe_id):
    """Return recipe detail URL"""
    return reverse('recipe:recipe-detail', args=[recipe_id])


# Helper function to generate recipe URL
def create_recipe(user, **params):
    """Create and return a sample recipe"""
    defaults = {
        'title': 'Sample recipe',
        'time_minutes': 10,
        'price': Decimal('5.00'),
        'description': 'Sample description',
        'link': 'https://www.sample.com'
    }
    defaults.update(params)

    return Recipe.objects.create(user=user, **defaults)


def create_user(**params):
    return get_user_model().objects.create_user(**params)


class PublicRecipeApiTests(TestCase):
    """Test unauthenticated recipe API access"""

    def setUp(self):
        self.client = APIClient()  # Client to make requests

    def test_auth_required(self):
        """Test that authentication is required"""
        res = self.client.get(RECIPES_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateRecipeApiTests(TestCase):
    """Test authenticated recipe API access"""

    def setUp(self):
        self.client = APIClient()
        self.user = create_user(
            email='test@example.com',
            password='password123'
        )

        self.client.force_authenticate(self.user)

    def test_retrieve_recipes(self):
        """Test retrieving a list of recipes"""
        create_recipe(user=self.user)  # User is a required field
        create_recipe(user=self.user)

        res = self.client.get(RECIPES_URL)

        recipes = Recipe.objects.all().order_by('-id')  # Reverse order, latest first # noqa
        serializer = RecipeSerializer(recipes, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)  # Compare the data in the response to the serializer data # noqa

    def test_recipe_list_limited_to_user(self):
        """Test that recipes for the authenticated user are returned"""
        other_user = create_user(
            email='test2@example.com',
            password='testpass'
        )

        create_recipe(user=other_user)
        create_recipe(user=self.user)

        res = self.client.get(RECIPES_URL)  # Get the list of recipes

        recipes = Recipe.objects.filter(user=self.user)  # Filter the recipes to only include those for the authenticated user # noqa
        serializer = RecipeSerializer(recipes, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_get_recipe_detail(self):
        """Test getting a recipe detail"""
        recipe = create_recipe(user=self.user)

        url = detail_url(recipe.id)
        res = self.client.get(url)

        serializer = RecipeDetailSerializer(recipe)
        self.assertEqual(res.data, serializer.data)

    def test_create_recipe(self):
        """Test creating a basic recipe"""
        payload = {
            'title': 'Sample recipe',
            'time_minutes': 30,
            'price': Decimal('5.00')
        }

        res = self.client.post(RECIPES_URL, payload)  # Post the payload to the URL # noqa
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        recipe = Recipe.objects.get(id=res.data['id'])
        for key, value in payload.items():
            self.assertEqual(getattr(recipe, key), value)

        self.assertEqual(recipe.user, self.user)

    def test_partial_update(self):
        """Test updating a recipe with patch"""
        original_link = 'https://www.sample.com/recipe.pdf'
        recipe = create_recipe(
            user=self.user,
            title='Sample recipe',
            time_minutes=30,
            price=Decimal('5.00'),
            link=original_link,
            )

        payload = {
            'title': 'New recipe title'
        }

        url = detail_url(recipe.id)
        res = self.client.patch(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)

        recipe.refresh_from_db()

        self.assertEqual(recipe.title, payload['title'])
        self.assertEqual(recipe.link, original_link)
        self.assertEqual(recipe.user, self.user)

    def test_full_update(self):
        """Test updating a recipe with put"""

        recipe = create_recipe(
            user=self.user,
            title='Sample recipe',
            time_minutes=30,
            price=Decimal('5.00'),
            description='Sample description',
        )

        payload = {
            'title': 'Updated recipe',
            'time_minutes': 25,
            'price': Decimal('10.00'),
            'description': 'Updated description'
        }

        url = detail_url(recipe.id)
        res = self.client.put(url, payload)  # Put Request

        self.assertEqual(res.status_code, status.HTTP_200_OK)

        recipe.refresh_from_db()

        for key, value in payload.items():
            self.assertEqual(getattr(recipe, key), value)

        self.assertEqual(recipe.user, self.user)

    def test_update_user_returns_error(self):
        """Test that updating the user field in an recipe object returns an error""" # noqa
        new_user = create_user(
            email='user2@example.com',
            password='password123'
        )

        payload = {
            'user': new_user.id
        }

        recipe = create_recipe(user=self.user)

        url = detail_url(recipe.id)
        self.client.put(url, payload)

        recipe.refresh_from_db()
        self.assertEqual(recipe.user, self.user)  # User should not have changed # noqa

    def test_delete_recipe(self):
        """Test deleting a recipe"""
        recipe = create_recipe(user=self.user)

        url = detail_url(recipe.id)
        res = self.client.delete(url)  # Delete request

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)

        self.assertFalse(Recipe.objects.filter(id=recipe.id).exists())

    def test_recipe_other_users_recipe_error(self):
        """Test that users cannot delete other users' recipes"""
        other_user = create_user(
            email='user2@example.com',
            password='password123'
        )

        recipe = create_recipe(user=other_user)

        url = detail_url(recipe.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)
        self.assertTrue(Recipe.objects.filter(id=recipe.id).exists())
