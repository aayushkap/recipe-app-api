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
