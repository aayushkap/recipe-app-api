"""
Database models for the core app
"""
from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin)


class UserManager(BaseUserManager):
    """This is a custom user manager class
    which is created by extending the BaseUserManager"""
    def create_user(self, email, password=None, **extra_fields):
        """Create, save and return a new user"""
        if not email:
            raise ValueError('Users must have an email address')

        # self.model is a reference to the model that the manager is for.
        user = self.model(email=self.normalize_email(email), **extra_fields)

        # set_password is a built-in function of the AbstractBaseUser class which hashes the password # noqa
        user.set_password(password)

        # save(using=self._db) is used to save the user to the User table in the database # noqa
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None):
        """Create and return a super user"""

        if not email:
            raise ValueError('Super user must have an email address')

        user = self.create_user(email, password)

        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)

        return User


class User(AbstractBaseUser, PermissionsMixin):
    """This is a custom user model which is created by extending the AbstractBaseUser and PermissionsMixin # noqa
       AbstractBaseUser contains the functionality for the Authentication system # noqa
       PermissionsMixin contains the functionality for the Permissions system # noqa"""
    email = models.EmailField(max_length=255, unique=True)
    name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UserManager() # This is used to tell Django that UserManager is the manager for the User model # noqa

    USERNAME_FIELD = 'email'
