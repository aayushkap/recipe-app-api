"""
    Serializer for user API Views
    Serializers help in translating data between different formats (like Python objects and JSON), # noqa
    so that they can be easily transmitted over a network.
"""

from django.contrib.auth import get_user_model, authenticate
from django.utils.translation import gettext_lazy as _

from rest_framework import serializers

from core.models import UserDetails


class UserSerializer(serializers.ModelSerializer):
    """Serializer for the users object"""

    # Meta class is used to configure the serializer. It tells the serializer what model to base the serializer on. # noqa
    class Meta:
        model = get_user_model()
        fields = ("email", "password", "name")
        extra_kwargs = {"password": {"write_only": True, "min_length": 5}}

    # Overriding the create function to create a new user with encrypted password # noqa
    def create(self, validated_data):
        """Create a new user with encrypted password and return it"""
        return get_user_model().objects.create_user(**validated_data)

    # Overriding the update function to update the user with encrypted password
    def update(self, instance, validated_data):
        """Update a user, setting the password correctly and return it"""
        password = validated_data.pop(
            "password", None
        )  # Remove password from validated data # noqa
        user = super().update(
            instance, validated_data
        )  # Update the user with the validated data # noqa

        if password:  # If password is provided, hash it and set it to the user # noqa
            user.set_password(password)
            user.save()

        return user


class AuthTokenSerializer(serializers.Serializer):
    """Serializer for the user authentication object"""

    # Define a serializer with email and password fields
    email = serializers.EmailField()
    password = serializers.CharField(
        style={"input_type": "password"}, trim_whitespace=False
    )

    def validate(self, attrs):
        """Validate and authenticate the user"""
        email = attrs.get("email")
        password = attrs.get("password")

        # Authenticate the user with the provided email and password
        user = authenticate(
            request=self.context.get("request"), username=email, password=password # noqa
        )

        if not user:
            msg = _("Unable to authenticate with provided credentials")

            # Will raise HTTP 400 error in the response
            raise serializers.ValidationError(msg, code="authentication")

        # If user authenticated successfully, set the user in the attrs and return it # noqa
        attrs["user"] = user
        return attrs


class UserDetailsSerializer(serializers.ModelSerializer):

    age = serializers.IntegerField(default=0)

    class Meta:
        model = UserDetails
        fields = ['id', 'age', 'country', 'city', 'favorite_food']
        read_only_fields = ['id']
