# recipe-app-api
Recipe API Project with Python Django

Deployed Here: http://ec2-54-211-199-101.compute-1.amazonaws.com/api/docs/

# Endpoints:

## User Endpoints:

1.  Create a User Account via */api/user/create*.
2.  Authnticate your user via */api/user/token*.
3.  Optionally add more User information using the */api/user/details/me* endpoint.

## Recipe Endpoints:

1.  To fetch all recipies created, make a GET request to the */api/recipe/recipies* endpoint.
2.  To add a recipe to the system, make a POST request to */api/recipe/recipies*.
3.  Add or update recipe tags through the */api/recipe/tags* endpoints.
4.  Attach recipe ingredients to each recipe via the */api/recipe/ingredients* endpoints.
5.  Add an image for your recipe via the */api/recipe/recipies/{id}/upload-image/* endpoint.
