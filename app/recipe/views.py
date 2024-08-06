"""
    Views for the recipe app
"""

from rest_framework import viewsets
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from core.models import Recipe
from recipe import serializers


class RecipeViewSet(viewsets.ModelViewSet):
    """View for Manage recipe APIs in the database"""
    serializer_class = serializers.RecipeDetailSerializer  # Serializer class to be used # noqa

    queryset = Recipe.objects.all()  # Models to be queried from the database # noqa

    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    # Override the get_queryset method to return objects for the current authenticated user only # noqa
    def get_queryset(self):
        """Return objects for the current authenticated user only"""
        return self.queryset.filter(user=self.request.user).order_by('-id')

    def get_serializer_class(self):
        """Return aserializer class for Request"""
        if self.action == 'list':  # If the action is list, return the preview serializer # noqa
            return serializers.RecipeSerializer
        else:
            return self.serializer_class  # Otherwise, return the detail serializer # noqa

    # Override the perform_create method to save the user field
    def perform_create(self, serializer):
        """Create a new recipe with the current authenticated user"""
        serializer.save(user=self.request.user)
