"""
    Serializers for recipe app
"""

from rest_framework import serializers

from core.models import Recipe, Tag, Ingredient


# We put TagSerialzier on top as RecipeSerializer depends on it # noqa
class TagSerializer(serializers.ModelSerializer):
    """Serializer for tag objects"""

    class Meta:
        model = Tag
        fields = ['id', 'name']  # Convert only the ID and name fields to JSON # noqa
        read_only_fields = ['id']


class IngredientSerializer(serializers.ModelSerializer):
    """Serializer for ingredient objects"""

    class Meta:
        model = Ingredient
        fields = ['id', 'name']  # Convert only the ID and name fields to JSON # noqa
        read_only_fields = ['id']


class RecipeSerializer(serializers.ModelSerializer):
    """Serializer for recipe objects"""
    tags = TagSerializer(many=True, required = False)  # Convert tags to JSON # noqa
    ingredients = IngredientSerializer(many=True, required = False)  # Convert ingredients to JSON # noqa

    class Meta:
        model = Recipe
        fields = ['id', 'title', 'time_minutes', 'price', 'link', 'tags', 'ingredients']  # noqa
        read_only_fields = ['id', ]

    def _get_or_create_tags(self, tags, instance):
        """ Get or create tags for a recipe """

        auth_user = self.context['request'].user  # We assign the ingredient to the authenticated user # noqa

        for tag in tags:
            tag_obj, created = Tag.objects.get_or_create(user=auth_user, **tag)
            instance.tags.add(tag_obj)

    def _get_or_create_ingredients(self, ingredients, instance):
        """ Get or create ingredients for a recipe """

        auth_user = self.context['request'].user

        for ingredient in ingredients:
            ingredient_obj, created = Ingredient.objects.get_or_create(user=auth_user, **ingredient)  # noqa
            instance.ingredients.add(ingredient_obj)

    def create(self, validated_data):
        """ Override the create method to handle tags """

        tags = validated_data.pop('tags', [])  # Pop tags from validated data # noqa

        ingredients = validated_data.pop('ingredients', [])  # Pop ingredients from validated data # noqa

        recipe = Recipe.objects.create(**validated_data) # Create a new recipe # noqa

        if tags:
            self._get_or_create_tags(tags, recipe)

        if ingredients:
            self._get_or_create_ingredients(ingredients, recipe)

        return recipe

    def update(self, instance, validated_data):
        """ Override the update method to handle tags """

        # Change how an exisiting instance of a recipe is updated

        tags = validated_data.pop('tags', None)  # Explicitly set tags to None, as empty list means clear all tags # noqa
        ingredients = validated_data.pop('ingredients', None)  # Explicitly set ingredients to None, as empty list means clear all ingredients # noqa

        if ingredients is not None:
            instance.ingredients.clear()

            self._get_or_create_ingredients(ingredients, instance)

        if tags is not None:
            instance.tags.clear()

            self._get_or_create_tags(tags, instance)

        for key, value in validated_data.items():
            setattr(instance, key, value)

        instance.save()

        return instance


# We extend RecipeSerializer as we want the base fields to be included in the detail view # noqa
class RecipeDetailSerializer(RecipeSerializer):
    """Serializer for recipe detail view"""

    class Meta(RecipeSerializer.Meta):
        model = Recipe
        fields = RecipeSerializer.Meta.fields + ['description']
