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

