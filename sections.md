**Section 9**

1.  Created a custom User Model and Manager `(core/models.py)`
2.  Configured Django to use it `(app/settings.py)`
3.  Created and Ran Migration `(core/migrations.py -> AUTH_USER_MODEL)`
4.  Normalized Emails & Encrypted Passwords

**Section 10**

1.  Added Admin Portal Features For Custom User Model `(core/admin.py)`

**Section 11**

1.  Added Swagger View For APIs by installing drf_spectacular and updating app URLs.

**Section 12**

1.  Created new app for Users API.
2.  Designed User API. `(user/views.py)`
3.  Implemented Create User API `(user/views -> CreateUserView)`
4.  Token Authentication for Users `(user/views -> CreateTokenView)`
5.  Manage / Update User information API `(user/views -> ManageUserView)`

**Section 13**

1.  CRUD Recipe APIs

**Section 14**

1.  Implemented Tags Model for Recipies.
2.  Implemented CRUD Operations for Tags.
3.  Created Serializers for Tag Operations.
4.  Created Test cases for Tags.

**Section 15**

1.  Implemented Ingredients Model for Recipies.
2.  Implemented CRUD Operations for Ingredients.
3.  Created Serializers for Tag Operations.
4.  Created Test cases for Ingredients.
5.  Refactored code for Tags and Ingredients.

**Section 16**

1.  Added image upload feature to the API.
2.  Configured Docker Volumes to Store Static and Media files.

**Section 17**

1.  Added filtering recipies by tags/ingredients.
2.  Add filtering tags/ingredients by those assigned recipies
3.  Customized OpenAPI Schema.

**Section 18**

1.  Created docker-compose-deploy for deployment.
2.  Created proxy dir for Nginx setup.
3.  Set up sample .env file for deployment.
