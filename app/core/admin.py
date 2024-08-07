"""
Django Admin is a powerful tool that allows you to manage your application's data. # noqa
It is a built-in feature of Django that allows you to create, read, update, and delete data from your database using a web interface. # noqa
Here, we inherit the UserAdmin class from the BaseUserAdmin class and customize the admin pages for the custom User model. # noqa
"""

from django.contrib import admin  # noqa

# Default User
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin  # noqa

# Translating the strings, if you want to support multiple languages
from django.utils.translation import gettext as _

from core import models


class UserAdmin(BaseUserAdmin):
    """Define the admin pages for the custom User model"""

    # Order the fields in the User model by id
    ordering = ["id"]

    # List the fields that will be displayed in the User model
    list_display = ["email", "name", "is_superuser"]

    # Define the fieldsets for the User model
    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("Personal Info", {"fields": ("name",)}),
        (_("Permissions"), {"fields": ("is_active", "is_staff", "is_superuser")}), # noqa
        (_("Important dates"), {"fields": ("last_login",)}),
    )

    readonly_fields = ("last_login",)

    # Define the add_fieldsets for the User model. Fields that will be displayed when adding a new user # noqa
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "email",
                    "password1",
                    "password2",
                    "name",
                    "is_active",
                    "is_staff",
                    "is_superuser",
                ),
            },
        ),
    )


admin.site.register(models.User, UserAdmin)
admin.site.register(models.Recipe)
admin.site.register(models.Tag)
admin.site.register(models.Ingredient)
