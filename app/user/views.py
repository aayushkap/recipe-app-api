"""
This file contains the views for the user API. Views are the endpoints that are exposed to the client. # noqa
"""

from rest_framework import generics, authentication, permissions
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.settings import api_settings

from user.serializer import (
    UserSerializer,
    AuthTokenSerializer,
    UserDetailsSerializer
)

from core.models import UserDetails


#   CreateAPIView is a generic view that provides a simple way to create a new user in the system. # noqa
class CreateUserView(generics.CreateAPIView):
    """Create a new user in the system"""

    serializer_class = UserSerializer


#  ObtainAuthToken is a generic view that provides a simple way to create a new auth token for the user. # noqa
class CreateTokenView(ObtainAuthToken):
    """Create a new auth token for user"""

    serializer_class = AuthTokenSerializer
    renderer_classes = api_settings.DEFAULT_RENDERER_CLASSES


#   ManageUserView is a generic view that provides a simple way to manage the authenticated user. # noqa
class ManageUserView(generics.RetrieveUpdateAPIView):
    """Manage the authenticated user"""

    serializer_class = UserSerializer
    authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)

    # Overriding the get_object function to get the authenticated user object. Called when we make a get request to the endpoint. # noqa
    def get_object(self):
        """Get Authenticated User Object, and run it through the serializer and return"""  # noqa
        return self.request.user


# UserDetailsView is a generic view that provides a simple way to create a new User Details record. # noqa
# Since we're using CreateAPIView, we are only allowing POST requests to this endpoint, to create a new User Details record. # noqa
class UserDetailsView(generics.CreateAPIView):
    """Create or update a Users Details record"""
    serializer_class = UserDetailsSerializer
    authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)

    def perform_create(self, serializer):
        user_details, created = UserDetails.objects.update_or_create(
            user=self.request.user,
            defaults=serializer.validated_data
        )
        return user_details


# ManageUserDetailsView is a generic view that provides a simple way to manage the authenticated user's details. # noqa
# Since we're using RetrieveUpdateAPIView, we are allowing GET and PATCH requests to this endpoint, to retrieve and update a user's details. # noqa
class ManageUserDetailsView(generics.RetrieveUpdateAPIView):
    """Retrieve or update authenticated user's details"""
    serializer_class = UserDetailsSerializer
    authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)

    # Overriding the get_object function to get the authenticated user's details object. Called when we make a get request to the endpoint. # noqa
    def get_object(self):
        return UserDetails.objects.get(user=self.request.user)
