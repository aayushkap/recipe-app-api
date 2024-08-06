"""
    Serializers for recipe app
"""

from rest_framework import serializers

from core.models import Recipe


class RecipeSerializer(serializers.ModelSerializer):
    """Serializer for recipe objects"""

    class Meta:
        model = Recipe
        fields = ['id', 'title', 'time_minutes', 'price', 'link']
        read_only_fields = ['id', ]


# We extend RecipeSerializer as we want the base fields to be included in the detail view # noqa
class RecipeDetailSerializer(RecipeSerializer):
    """Serializer for recipe detail view"""

    class Meta(RecipeSerializer.Meta):
        model = Recipe
        fields = RecipeSerializer.Meta.fields + ['description']
