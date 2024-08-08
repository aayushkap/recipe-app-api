"""
Test the recipe API
"""
from decimal import Decimal
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient
from core.models import Recipe, Tag, Ingredient

from recipe.serializers import (
    RecipeSerializer,  # Recipe Preview Serializer
    RecipeDetailSerializer  # Recipe Detail Serializer
)

import tempfile
import os

from PIL import Image

RECIPES_URL = reverse('recipe:recipe-list')


# Each detail URL is different, depending on the recipe ID. Hence, we need a helper function to generate the URL # noqa
def detail_url(recipe_id):
    """Return recipe detail URL"""
    return reverse('recipe:recipe-detail', args=[recipe_id])


# Helper function to generate image upload URL
def image_upload_url(recipe_id):
    """Return URL for recipe image upload"""
    return reverse('recipe:recipe-upload-image', args=[recipe_id])


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

    def test_create_recipe_with_new_tags(self):
        """Test creating a recipe with new tags"""

        payload = {
            'title': 'Avocado lime cheesecake',
            'tags': [{'name': 'Vegan'}, {'name': 'Dessert'}],
            'time_minutes': 60,
            'price': Decimal('20.00'),
            'link': 'https://www.sample.com/recipe.pdf',
            'description': 'This sounds gross'
        }

        res = self.client.post(RECIPES_URL, payload, format='json') # Convert payload to JSON # noqa

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        recipes = Recipe.objects.filter(user=self.user)
        self.assertEqual(recipes.count(), 1)

        recipe = recipes[0]
        self.assertEqual(recipe.tags.count(), 2)

        for tag in payload['tags']:
            exists = recipe.tags.filter(name=tag['name'], user = self.user).exists() # noqa
            self.assertTrue(exists)

    def test_create_recipe_with_existing_tags(self):
        """ Test creating a recipe with an existing tag"""
        tag = Tag.objects.create(user=self.user, name='Vegan')
        payload = {
            'title': 'Avocado lime cheesecake',
            'tags': [{'name': 'Vegan'}, {'name': 'Dessert'}],
            'time_minutes': 60,
            'price': Decimal('20.00'),
            'link': 'https://www.sample.com/recipe.pdf',
            'description': 'This sounds gross'
        }

        res = self.client.post(RECIPES_URL, payload, format='json')  # Create new recipe # noqa

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        recipes = Recipe.objects.filter(user=self.user)
        self.assertEqual(recipes.count(), 1)

        recipe = recipes[0]
        tags = recipe.tags.all()

        self.assertEqual(recipe.tags.count(), 2)
        self.assertIn(tag, tags)

        for tag in payload['tags']:
            exists = recipe.tags.filter(name=tag['name'], user = self.user).exists() # noqa

    def test_create_tag_on_update(self):
        """ Creating tag when updating a recipe"""

        recipe = create_recipe(user=self.user)

        payload = {
            'tags': [{'name': 'Vegan'}, {'name': 'Dessert'}],
        }

        url = detail_url(recipe.id)
        res = self.client.patch(url, payload, format='json')  # Patch request # noqa

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        new_tag = Tag.objects.get(user=self.user, name='Vegan')
        self.assertIn(new_tag, recipe.tags.all())

    def test_update_recipe_assign_tag(self):
        """ testing assigning an existing tag to a recipe"""

        tag_breakfast = Tag.objects.create(user=self.user, name='Breakfast')  # New tag # noqa

        recipe = create_recipe(user=self.user)
        recipe.tags.add(tag_breakfast)

        tag_lunch = Tag.objects.create(user=self.user, name='Lunch')
        payload = {
            'tags': [{'name': 'Lunch'}],
        }

        url = detail_url(recipe.id)
        res = self.client.patch(url, payload, format='json')  # Patch request # noqa

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn(tag_lunch, recipe.tags.all())
        self.assertNotIn(tag_breakfast, recipe.tags.all())

    def test_clear_recipe_tags(self):
        """Test clearing tags from a recipe"""

        recipe = create_recipe(user=self.user)
        tag = Tag.objects.create(user=self.user, name='Dessert')
        recipe.tags.add(tag)

        payload = {
            'tags': []
        }

        url = detail_url(recipe.id)
        res = self.client.patch(url, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(recipe.tags.count(), 0)

    def test_create_recipe_with_ingredients(self):
        """Test creating a recipe with new ingredients"""

        payload = {
            'title': 'Thai prawn red curry',
            'ingredients': [{'name': 'Prawns'}, {'name': 'Red curry paste'}],
            'time_minutes': 20,
            'price': Decimal('7.00'),
            'link': 'https://www.sample.com/recipe.pdf',
            'description': 'This sounds gross'
        }

        res = self.client.post(RECIPES_URL, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        recipes = Recipe.objects.filter(user=self.user)
        self.assertEqual(recipes.count(), 1)

        recipe = recipes[0]

        self.assertEqual(recipe.ingredients.count(), 2)

        for ingredient in payload['ingredients']:
            exists = recipe.ingredients.filter(name=ingredient['name'], user=self.user).exists()  # noqa
            self.assertTrue(exists)

    def test_create_recipe_with_existing_ingredients(self):

        ingredient = Ingredient.objects.create(user=self.user, name='Lemon')

        payload = {
            'title': 'Thai prawn red curry',
            'ingredients': [{'name': 'Lemon'}, {'name': 'Red curry paste'}],
            'time_minutes': 20,
            'price': Decimal('7.00'),
            'link': 'https://www.sample.com/recipe.pdf',
            'description': 'This sounds gross'
        }

        res = self.client.post(RECIPES_URL, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        recipes = Recipe.objects.filter(user=self.user)

        self.assertEqual(recipes.count(), 1)

        recipe = recipes[0]

        self.assertEqual(recipe.ingredients.count(), 2)

        self.assertIn(ingredient, recipe.ingredients.all())

        for ingredient in payload['ingredients']:
            exists = recipe.ingredients.filter(name=ingredient['name'], user=self.user).exists()  # noqa
            self.assertTrue(exists)

    def test_create_ingredient_on_update(self):
        """Test updating a recipe with ingredients"""

        recipe = create_recipe(user=self.user)

        payload = {
            'ingredients': [{'name': 'Prawns'}, {'name': 'Red curry paste'}],
        }

        url = detail_url(recipe.id)
        res = self.client.patch(url, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_200_OK)

        new_ingredient = Ingredient.objects.get(user=self.user, name='Prawns')

        self.assertIn(new_ingredient, recipe.ingredients.all())

    def test_update_recipe_assign_ingredient(self):
        """Test assigning an existing ingredient to a recipe"""

        ingredient = Ingredient.objects.create(user=self.user, name='Pepper')
        recipe = create_recipe(user=self.user)
        recipe.ingredients.add(ingredient)

        ingredient2 = Ingredient.objects.create(user=self.user, name='Chili')

        payload = {
            'ingredients': [{'name': 'Chili'}],
        }

        url = detail_url(recipe.id)
        res = self.client.patch(url, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn(ingredient2, recipe.ingredients.all())
        self.assertNotIn(ingredient, recipe.ingredients.all())

    def test_clear_recipe_ingredients(self):
        """Test clearing ingredients from a recipe"""

        recipe = create_recipe(user=self.user)
        ingredient = Ingredient.objects.create(user=self.user, name='Garlic')
        recipe.ingredients.add(ingredient)

        payload = {
            'ingredients': []
        }

        url = detail_url(recipe.id)
        res = self.client.patch(url, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(recipe.ingredients.count(), 0)


class RecipeImageUploadTests(TestCase):
    """Tests for image upload api"""

    def setUp(self):
        self.client = APIClient()
        self.user = create_user(email="user@example.com", password="password123") # noqa

        self.client.force_authenticate(self.user)
        self.recipe = create_recipe(user=self.user)

    def tearDown(self):
        self.recipe.image.delete()

    def test_upload_image(self):
        """Test uploading an image to recipe"""

        # URL to upload image
        url = image_upload_url(self.recipe.id)

        # We create a named temporary file with a .jpg suffix, to test the image upload # noqa
        with tempfile.NamedTemporaryFile(suffix='.jpg') as image_file:

            # Create a 10x10 pixel image
            img = Image.new('RGB', (10, 10))

            # Save the image to the temporary file
            img.save(image_file, format='JPEG')

            # Reset the file pointer to the beginning of the file
            image_file.seek(0)

            payload = {'image': image_file}

            # Multi-part form data post request
            res = self.client.post(url, payload, format='multipart')

        self.recipe.refresh_from_db()
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn('image', res.data)
        self.assertTrue(os.path.exists(self.recipe.image.path))

    def test_upload_image_bad_request(self):
        """Test uploading an invalid image"""

        url = image_upload_url(self.recipe.id)

        res = self.client.post(url, {'image': 'notimage'}, format='multipart')

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
