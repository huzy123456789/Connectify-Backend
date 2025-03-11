# DONT TOUCH OR CHANGE ANYTHING OR I AM GONNA KILL YOU

steps to start:

open the fkin terminal in the requirements.txt folder then type the following random ass commands:

1- python -m venv venv

2- venv/scripts/activate

3- pip install -r requirements.txt (plz let it run completely or bad stuff will happen)

4- cd Connectify_Backend

5- python manage.py runserver


If I am correct and haven't forgotten the basic commands then BOOM the server will be running on the default ip and port.
EZ init?

Contact Yours Truly Huzaifa Riaz on whatsapp if any issue occurs

# APIS DOCUMENTATION

## Authentication APIs

### Login
Authenticate a user with either username or email and password.

- **URL**: `/api/auth/login/`
- **Method**: `POST`
- **Authentication**: None
- **Request Body**:
  ```json
  {
    "login": "username_or_email",
    "password": "user_password"
  }
  ```
- **Success Response**:
  - **Code**: 200 OK
  - **Content**:
    ```json
    {
      "refresh": "refresh_token_string",
      "access": "access_token_string",
      "user": {
        "id": 1,
        "username": "username",
        "email": "user@example.com",
        "role": "USER or ADMIN",
        "first_name": "First",
        "last_name": "Last"
      }
    }
    ```
- **Error Response**:
  - **Code**: 401 UNAUTHORIZED
  - **Content**:
    ```json
    {
      "error": "Unable to log in with provided credentials."
    }
    ```

### Token Refresh
Refresh an expired access token using a valid refresh token.

- **URL**: `/api/auth/token/refresh/`
- **Method**: `POST`
- **Authentication**: None
- **Request Body**:
  ```json
  {
    "refresh": "refresh_token_string"
  }
  ```
- **Success Response**:
  - **Code**: 200 OK
  - **Content**:
    ```json
    {
      "access": "new_access_token_string"
    }
    ```
- **Error Response**:
  - **Code**: 401 UNAUTHORIZED
  - **Content**:
    ```json
    {
      "error": "Token is invalid or expired"
    }
    ```

## Authentication Usage

### Making Authenticated Requests
To access protected endpoints, include the access token in the Authorization header:

```
Authorization: Bearer <access_token>
```

### Token Lifetimes
- Access Token: 30 minutes
- Refresh Token: 1 day

When the access token expires, use the refresh token to get a new access token without requiring the user to log in again.

### Role-Based Access
The API uses role-based permissions:
- Users with `ADMIN` role can access admin-specific endpoints
- Users with `USER` role can access user-specific endpoints

## Test Users

For testing purposes, the following users are available:

### Admin User
- Username: `admin_test`
- Email: `admin@example.com`
- Password: `admin123`
- Role: `ADMIN`

### Regular User
- Username: `user_test`
- Email: `user@example.com`
- Password: `user123`
- Role: `USER`

## Organization APIs

### Create Organization
Create a new organization. The authenticated user will automatically be added as a member.

- **URL**: `/api/organizations/create/`
- **Method**: `POST`
- **Authentication**: Required
- **Request Body**:
  ```json
  {
    "name": "Organization Name",
    "description": "Organization Description"
  }
  ```
- **Success Response**:
  - **Code**: 201 CREATED
  - **Content**:
    ```json
    {
      "id": 1,
      "name": "Organization Name",
      "description": "Organization Description",
      "users": [1],
      "created_at": "2023-10-03T12:00:00Z",
      "updated_at": "2023-10-03T12:00:00Z"
    }
    ```
- **Error Response**:
  - **Code**: 400 BAD REQUEST
  - **Content**:
    ```json
    {
      "name": ["This field is required."]
    }
    ```

### Get User's Organizations
Get all organizations the authenticated user is a member of.

- **URL**: `/api/organizations/`
- **Method**: `GET`
- **Authentication**: Required
- **Success Response**:
  - **Code**: 200 OK
  - **Content**:
    ```json
    [
      {
        "id": 1,
        "name": "Organization Name",
        "description": "Organization Description",
        "users": [1, 2],
        "created_at": "2023-10-03T12:00:00Z",
        "updated_at": "2023-10-03T12:00:00Z"
      }
    ]
    ```

### Get All Organizations (Admin Only)
Get all organizations in the system. Only accessible to admin users.

- **URL**: `/api/organizations/all/`
- **Method**: `GET`
- **Authentication**: Required (Admin only)
- **Success Response**:
  - **Code**: 200 OK
  - **Content**:
    ```json
    [
      {
        "id": 1,
        "name": "Organization Name",
        "description": "Organization Description",
        "users": [1, 2],
        "created_at": "2023-10-03T12:00:00Z",
        "updated_at": "2023-10-03T12:00:00Z"
      }
    ]
    ```
- **Error Response**:
  - **Code**: 403 FORBIDDEN
  - **Content**:
    ```json
    {
      "detail": "You do not have permission to perform this action."
    }
    ```

### Get Organization Detail
Get detailed information about a specific organization.

- **URL**: `/api/organizations/<id>/`
- **Method**: `GET`
- **Authentication**: Required
- **Success Response**:
  - **Code**: 200 OK
  - **Content**:
    ```json
    {
      "id": 1,
      "name": "Organization Name",
      "description": "Organization Description",
      "users": [
        {
          "id": 1,
          "username": "username",
          "email": "user@example.com",
          "role": "ADMIN",
          "first_name": "First",
          "last_name": "Last"
        }
      ],
      "created_at": "2023-10-03T12:00:00Z",
      "updated_at": "2023-10-03T12:00:00Z"
    }
    ```
- **Error Response**:
  - **Code**: 404 NOT FOUND
  - **Content**:
    ```json
    {
      "detail": "Not found."
    }
    ```

### Update Organization
Update an existing organization.

- **URL**: `/api/organizations/<id>/update/`
- **Method**: `PUT`
- **Authentication**: Required
- **Request Body**:
  ```json
  {
    "name": "Updated Organization Name",
    "description": "Updated Organization Description"
  }
  ```
- **Success Response**:
  - **Code**: 200 OK
  - **Content**:
    ```json
    {
      "id": 1,
      "name": "Updated Organization Name",
      "description": "Updated Organization Description",
      "users": [1, 2],
      "created_at": "2023-10-03T12:00:00Z",
      "updated_at": "2023-10-03T12:30:00Z"
    }
    ```
- **Error Response**:
  - **Code**: 404 NOT FOUND
  - **Content**:
    ```json
    {
      "detail": "Not found."
    }
    ```

### Delete Organization
Delete an organization.

- **URL**: `/api/organizations/<id>/delete/`
- **Method**: `DELETE`
- **Authentication**: Required
- **Success Response**:
  - **Code**: 204 NO CONTENT
- **Error Response**:
  - **Code**: 404 NOT FOUND
  - **Content**:
    ```json
    {
      "detail": "Not found."
    }
    ```

### Add Users to Organization
Add multiple users to an organization.

- **URL**: `/api/organizations/<id>/add-users/`
- **Method**: `POST`
- **Authentication**: Required
- **Request Body**:
  ```json
  {
    "user_ids": [2, 3, 4]
  }
  ```
- **Success Response**:
  - **Code**: 200 OK
  - **Content**: Detailed organization information with updated users list
- **Error Response**:
  - **Code**: 400 BAD REQUEST
  - **Content**:
    ```json
    {
      "user_ids": ["This field is required."]
    }
    ```

### Remove Users from Organization
Remove multiple users from an organization.

- **URL**: `/api/organizations/<id>/remove-users/`
- **Method**: `POST`
- **Authentication**: Required
- **Request Body**:
  ```json
  {
    "user_ids": [2, 3]
  }
  ```
- **Success Response**:
  - **Code**: 200 OK
  - **Content**: Detailed organization information with updated users list
- **Error Response**:
  - **Code**: 400 BAD REQUEST
  - **Content**:
    ```json
    {
      "error": "Cannot remove all users from an organization"
    }
    ```

### Search Organizations
Search for organizations by name or description.

- **URL**: `/api/organizations/search/?q=<query>`
- **Method**: `GET`
- **Authentication**: Required
- **Success Response**:
  - **Code**: 200 OK
  - **Content**: List of matching organizations
- **Error Response**:
  - **Code**: 400 BAD REQUEST
  - **Content**:
    ```json
    {
      "error": "Search query parameter 'q' is required"
    }
    ```

### Get User's Organizations
Get organizations for the current user.

- **URL**: `/api/organizations/user/`
- **Method**: `GET`
- **Authentication**: Required
- **Success Response**:
  - **Code**: 200 OK
  - **Content**: List of organizations the user is a member of

### Get Another User's Organizations (Admin Only)
Get organizations for a specific user. Only accessible to admin users.

- **URL**: `/api/organizations/user/<user_id>/`
- **Method**: `GET`
- **Authentication**: Required (Admin only)
- **Success Response**:
  - **Code**: 200 OK
  - **Content**: List of organizations the specified user is a member of

