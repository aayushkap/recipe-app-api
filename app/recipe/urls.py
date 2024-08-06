"""
    URL Mapping for the Recipe API
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter

from recipe import views


# Default router provided by Django REST framework, to automatically generate URLs for our viewset # noqa
# Automatically generates Get, Post, Put, Patch and Delete URLs for our viewset
router = DefaultRouter()
router.register('recipes', views.RecipeViewSet) # Register the viewset with the router and provide a URL path # noqa

app_name = 'recipe'

urlpatterns = [
    path('', include(router.urls))  # Include the URLs generated by the router
]
