"""
URLs for the user API
"""

from django.urls import path

from user import views

app_name = "user"

# View which handles that what happens when a request is made to a URL.
# Here, we are mapping the URL to the view, which we defined in views.py
urlpatterns = [
    path("create/", views.CreateUserView.as_view(), name="create"),
    path("token/", views.CreateTokenView.as_view(), name="token"),
    path("me/", views.ManageUserView.as_view(), name="me"),
]
