"""
    Serializers for recipe app
"""

from rest_framework import serializers

from core.models import Recipe, Tag


# We put TagSerialzier on top as RecipeSerializer depends on it # noqa
class TagSerializer(serializers.ModelSerializer):
    """Serializer for tag objects"""

    class Meta:
        model = Tag
        fields = ['id', 'name']  # Convert only the ID and name fields to JSON # noqa
        read_only_fields = ['id']


class RecipeSerializer(serializers.ModelSerializer):
    """Serializer for recipe objects"""
    tags = TagSerializer(many=True, required = False)  # Convert tags to JSON # noqa

    class Meta:
        model = Recipe
        fields = ['id', 'title', 'time_minutes', 'price', 'link', 'tags']
        read_only_fields = ['id', ]

    def _get_or_create_tags(self, tags, instance):
        """ Get or create tags for a recipe """

        auth_user = self.context['request'].user

        for tag in tags:
            tag_obj, created = Tag.objects.get_or_create(user=auth_user, **tag)
            instance.tags.add(tag_obj)

    def create(self, validated_data):
        """ Override the create method to handle tags """

        tags = validated_data.pop('tags', [])  # Pop tags from validated data # noqa

        recipe = Recipe.objects.create(**validated_data) # Create a new recipe # noqa

        if tags:
            self._get_or_create_tags(tags, recipe)

        return recipe

    def update(self, instance, validated_data):
        """ Override the update method to handle tags """

        # Change how an exisiting instance of a recipe is updated

        tags = validated_data.pop('tags', [])

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
