"""
    Views for the recipe app.
    Since Tags and Ingredients views are similar, we can use mixins to reduce code duplication. # noqa
"""

from rest_framework import (
    viewsets,
    mixins, # Mixins are classes that provide functionality to be inherited (mixed-in) by a subclass # noqa
    status  # Status is a module that contains standard HTTP status codes # noqa
)
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response

from core.models import Recipe, Tag, Ingredient
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
        elif self.action == 'upload_image':  # If the action is upload_image, return the image serializer # noqa
            return serializers.RecipeImageSerializer

        return self.serializer_class

    # Override the perform_create method to save the user field
    def perform_create(self, serializer):
        """Create a new recipe with the current authenticated user"""
        serializer.save(user=self.request.user)

    # Custom action to upload an image to a recipe. Detail=True means that the action is for a specific recipe # noqa
    @action(methods=['POST'], detail=True, url_path='upload-image')
    def upload_image(self, request, pk=None):
        # pk is the primary key of the recipe # noqa
        """upload an image to a recipe"""

        recipe = self.get_object()  # Get the recipe object # noqa
        serializer = self.get_serializer(recipe, data=request.data)

        if serializer.is_valid():
            serializer.save()   # Save the serializer # noqa
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class BaseRecipeAttrViewSet(mixins.UpdateModelMixin,  # UpdateModelMixin is a mixin that provides an update() method # noqa
                 mixins.ListModelMixin,  # ListModelMixin is a mixin that provides a list() method # noqa
                 mixins.DestroyModelMixin,  # DestroyModelMixin is a mixin that provides a destroy() method # noqa
                 viewsets.GenericViewSet  # GenericViewSet is a viewset that provides default create(), retrieve(), update(), and destroy() actions # noqa
                            ):
    """Base viewset for user owned recipe attributes"""

    #  This class is used to reduce code duplication in the Tag and Ingredient viewsets # noqa

    # User must be authenticated to access the API
    authentication_classes = [TokenAuthentication]  # Authentication classes to be used # noqa
    permission_classes = [IsAuthenticated]  # Permission classes to be used # noqa

    def get_queryset(self):
        """Return objects for the current authenticated user only"""
        return self.queryset.filter(user=self.request.user).order_by('-name')


class TagViewSet(BaseRecipeAttrViewSet):
    """Manage tags in the database. Extends the BaseRecipeAttrViewSet."""
    serializer_class = serializers.TagSerializer
    queryset = Tag.objects.all()


class IngredientViewSet(BaseRecipeAttrViewSet):
    """ Manage Ingredients in the Database. Extends the BaseRecipeAttrViewSet.""" # noqa

    """Manage tags in the database"""
    serializer_class = serializers.IngredientSerializer
    queryset = Ingredient.objects.all()
