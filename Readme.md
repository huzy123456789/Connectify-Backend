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

### Organization Roles

In this API, there are two types of administrative roles:

1. **System Admin**: Users with the role 'ADMIN' in their user profile. These users have system-wide privileges.

2. **Organization Admin**: Users who are designated as administrators of specific organizations. Any user can be an admin of an organization they belong to.

### Create Organization
Create a new organization. The authenticated user will automatically be added as a member and as an organization admin.

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
      "admins": [1],
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
Get all organizations the authenticated user is a member of or an admin of.

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
        "admins": [1],
        "created_at": "2023-10-03T12:00:00Z",
        "updated_at": "2023-10-03T12:00:00Z"
      }
    ]
    ```

### Get All Organizations (Admin Only)
Get all organizations in the system. Only accessible to system admin users (role='ADMIN').

- **URL**: `/api/organizations/all/`
- **Method**: `GET`
- **Authentication**: Required (System Admin only)
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
        "admins": [1],
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
      "error": "Only system administrators can access this endpoint"
    }
    ```

### Get Organization Detail
Get detailed information about a specific organization. User must be a member or an admin of the organization, or a system admin.

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
      "users": [{
        "id": 1,
        "username": "username",
        "email": "user@example.com",
        "role": "ADMIN",
        "first_name": "First",
        "last_name": "Last"
      }],
      "admins": [{
        "id": 1,
        "username": "username",
        "email": "user@example.com",
        "role": "USER",
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
  - **Code**: 403 FORBIDDEN
  - **Content**:
    ```json
    {
      "error": "You do not have permission to view this organization"
    }
    ```

### Update Organization
Update an existing organization. User must be an admin of the organization or a system admin.

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
      "admins": [1],
      "created_at": "2023-10-03T12:00:00Z",
      "updated_at": "2023-10-03T12:30:00Z"
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
  - **Code**: 403 FORBIDDEN
  - **Content**:
    ```json
    {
      "error": "Only organization administrators can update the organization"
    }
    ```

### Delete Organization
Delete an organization. User must be an admin of the organization or a system admin.

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
  - **Code**: 403 FORBIDDEN
  - **Content**:
    ```json
    {
      "error": "Only organization administrators can delete the organization"
    }
    ```

### Add Users to Organization
Add multiple users to an organization. User must be an admin of the organization or a system admin.

- **URL**: `/api/organizations/<id>/add-users/`
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
      "user_ids": ["This field is required."]
    }
    ```
  - **Code**: 403 FORBIDDEN
  - **Content**:
    ```json
    {
      "error": "Only organization administrators can add users to the organization"
    }
    ```

### Remove Users from Organization
Remove multiple users from an organization. User must be an admin of the organization or a system admin. Organization admins cannot be removed through this endpoint.

- **URL**: `/api/organizations/<id>/remove-users/`
- **Method**: `POST`
- **Authentication**: Required
- **Request Body**:
  ```json
  {
    "user_ids": [2]
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
  - **Code**: 400 BAD REQUEST
  - **Content**:
    ```json
    {
      "error": "Cannot remove all users from an organization"
    }
    ```
  - **Code**: 400 BAD REQUEST
  - **Content**:
    ```json
    {
      "error": "Cannot remove organization administrators"
    }
    ```

### Get Organization Admins
Get all administrators of an organization. User must be a member or an admin of the organization, or a system admin.

- **URL**: `/api/organizations/<id>/admins/`
- **Method**: `GET`
- **Authentication**: Required
- **Success Response**:
  - **Code**: 200 OK
  - **Content**:
    ```json
    [
      {
        "id": 1,
        "username": "admin_user",
        "email": "admin@example.com",
        "role": "USER",
        "first_name": "Admin",
        "last_name": "User"
      }
    ]
    ```
- **Error Response**:
  - **Code**: 403 FORBIDDEN
  - **Content**:
    ```json
    {
      "error": "You do not have permission to view this organization's administrators"
    }
    ```

### Add Organization Admins
Add administrators to an organization. User must be an admin of the organization or a system admin.

- **URL**: `/api/organizations/<id>/add-admins/`
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
  - **Content**: Detailed organization information with updated admins list
- **Error Response**:
  - **Code**: 403 FORBIDDEN
  - **Content**:
    ```json
    {
      "error": "Only organization administrators can add new administrators"
    }
    ```

### Remove Organization Admins
Remove administrators from an organization. User must be an admin of the organization or a system admin.

- **URL**: `/api/organizations/<id>/remove-admins/`
- **Method**: `POST`
- **Authentication**: Required
- **Request Body**:
  ```json
  {
    "user_ids": [2]
  }
  ```
- **Success Response**:
  - **Code**: 200 OK
  - **Content**: Detailed organization information with updated admins list
- **Error Response**:
  - **Code**: 400 BAD REQUEST
  - **Content**:
    ```json
    {
      "error": "Cannot remove all administrators from an organization"
    }
    ```
  - **Code**: 400 BAD REQUEST
  - **Content**:
    ```json
    {
      "error": "You cannot remove yourself as an administrator"
    }
    ```

### Search Organizations
Search for organizations by name or description. Returns organizations the user is a member of, an admin of, or all organizations for system admins.

- **URL**: `/api/organizations/search/?q=<query>`
- **Method**: `GET`
- **Authentication**: Required
- **Query Parameters**:
  - `q`: Search query string
- **Success Response**:
  - **Code**: 200 OK
  - **Content**: List of organizations matching the search query
- **Error Response**:
  - **Code**: 400 BAD REQUEST
  - **Content**:
    ```json
    {
      "error": "Search query parameter 'q' is required"
    }
    ```

### Get User's Organizations
Get organizations for the current user (both as a member and as an admin).

- **URL**: `/api/organizations/user/`
- **Method**: `GET`
- **Authentication**: Required
- **Success Response**:
  - **Code**: 200 OK
  - **Content**: List of organizations the user is a member of

### Get Another User's Organizations (Admin Only)
Get organizations for a specific user. For system admins, returns all of the user's organizations. For regular users, returns only organizations that both users share (either as members or where the requesting user is an admin).

- **URL**: `/api/organizations/user/<user_id>/`
- **Method**: `GET`
- **Authentication**: Required
- **Success Response**:
  - **Code**: 200 OK
  - **Content**: List of organizations the specified user is a member of
- **Error Response**:
  - **Code**: 403 FORBIDDEN
  - **Content**:
    ```json
    {
      "error": "You do not have permission to view this user's organizations"
    }
    ```

## Posts APIs

The Posts API provides endpoints for creating, reading, updating, and deleting posts, as well as interacting with posts through comments, reactions, shares, and tags.

### Post Model

Posts in the system have the following key attributes:
- Content (text)
- Media attachments (images and videos)
- Visibility (public or private)
- Organization association (optional)
- Reactions, comments, and shares
- User tags and hashtags

### Create Post
Create a new post with optional media files, hashtags, and user tags.

- **URL**: `/api/posts/create/`
- **Method**: `POST`
- **Authentication**: Required
- **Request Body**:
  ```json
  {
    "content": "This is a post with #hashtag",
    "organization_id": 1,
    "ispublic": true,
    "tagged_user_ids": [2, 3]
  }
  ```
- **Media Files**: Include media files in the request using multipart/form-data
- **Success Response**:
  - **Code**: 201 CREATED
  - **Content**: Detailed post information including media, hashtags, and tags
- **Error Response**:
  - **Code**: 400 BAD REQUEST
  - **Content**:
    ```json
    {
      "content": ["This field is required."]
    }
    ```

### Get Post Detail
Get detailed information about a specific post.

- **URL**: `/api/posts/<id>/`
- **Method**: `GET`
- **Authentication**: Required
- **Success Response**:
  - **Code**: 200 OK
  - **Content**: Detailed post information including media, comments, reactions, tags, and shares
- **Error Response**:
  - **Code**: 403 FORBIDDEN
  - **Content**:
    ```json
    {
      "error": "You do not have permission to view this post"
    }
    ```

### Update Post
Update an existing post.

- **URL**: `/api/posts/<id>/update/`
- **Method**: `PUT`
- **Authentication**: Required
- **Request Body**:
  ```json
  {
    "content": "Updated post content with #newtag",
    "ispublic": false
  }
  ```
- **Success Response**:
  - **Code**: 200 OK
  - **Content**: Updated post information
- **Error Response**:
  - **Code**: 403 FORBIDDEN
  - **Content**:
    ```json
    {
      "error": "You do not have permission to update this post"
    }
    ```

### Delete Post
Delete a post.

- **URL**: `/api/posts/<id>/delete/`
- **Method**: `DELETE`
- **Authentication**: Required
- **Success Response**:
  - **Code**: 204 NO CONTENT
- **Error Response**:
  - **Code**: 403 FORBIDDEN
  - **Content**:
    ```json
    {
      "error": "You do not have permission to delete this post"
    }
    ```

### Get Feed
Get a feed of posts for the current user.

- **URL**: `/api/posts/feed/`
- **Method**: `GET`
- **Authentication**: Required
- **Query Parameters**:
  - `page`: Page number (default: 1)
  - `page_size`: Number of posts per page (default: 10, max: 50)
- **Success Response**:
  - **Code**: 200 OK
  - **Content**: Paginated list of posts

### Get User Posts
Get posts created by a specific user or the current user.

- **URL**: `/api/posts/user/` (current user) or `/api/posts/user/<user_id>/` (specific user)
- **Method**: `GET`
- **Authentication**: Required
- **Query Parameters**:
  - `page`: Page number (default: 1)
  - `page_size`: Number of posts per page (default: 10, max: 50)
- **Success Response**:
  - **Code**: 200 OK
  - **Content**: Paginated list of posts

### Get Organization Posts
Get posts from a specific organization.

- **URL**: `/api/posts/organization/<org_id>/`
- **Method**: `GET`
- **Authentication**: Required
- **Query Parameters**:
  - `page`: Page number (default: 1)
  - `page_size`: Number of posts per page (default: 10, max: 50)
- **Success Response**:
  - **Code**: 200 OK
  - **Content**: Paginated list of posts

### Comment Operations

#### Create Comment
Create a comment on a post or reply to another comment.

- **URL**: `/api/posts/<post_id>/comments/create/`
- **Method**: `POST`
- **Authentication**: Required
- **Request Body**:
  ```json
  {
    "content": "This is a comment",
    "parent_comment_id": null
  }
  ```
- **Success Response**:
  - **Code**: 201 CREATED
  - **Content**: Comment information

#### Get Post Comments
Get all top-level comments for a post.

- **URL**: `/api/posts/<post_id>/comments/`
- **Method**: `GET`
- **Authentication**: Required
- **Query Parameters**:
  - `page`: Page number (default: 1)
  - `page_size`: Number of comments per page (default: 10, max: 50)
- **Success Response**:
  - **Code**: 200 OK
  - **Content**: Paginated list of comments

#### Get Comment Replies
Get all replies to a specific comment.

- **URL**: `/api/posts/comments/<comment_id>/replies/`
- **Method**: `GET`
- **Authentication**: Required
- **Query Parameters**:
  - `page`: Page number (default: 1)
  - `page_size`: Number of replies per page (default: 10, max: 50)
- **Success Response**:
  - **Code**: 200 OK
  - **Content**: Paginated list of replies

#### Update Comment
Update a comment.

- **URL**: `/api/posts/comments/<comment_id>/update/`
- **Method**: `PUT`
- **Authentication**: Required
- **Request Body**:
  ```json
  {
    "content": "Updated comment content"
  }
  ```
- **Success Response**:
  - **Code**: 200 OK
  - **Content**: Updated comment information

#### Delete Comment
Delete a comment.

- **URL**: `/api/posts/comments/<comment_id>/delete/`
- **Method**: `DELETE`
- **Authentication**: Required
- **Success Response**:
  - **Code**: 204 NO CONTENT

### Reaction Operations

#### Get Reaction Types
Get all available reaction types.

- **URL**: `/api/posts/reaction-types/`
- **Method**: `GET`
- **Authentication**: Required
- **Success Response**:
  - **Code**: 200 OK
  - **Content**: List of reaction types

#### React to Post
React to a post or change an existing reaction.

- **URL**: `/api/posts/<post_id>/react/`
- **Method**: `POST`
- **Authentication**: Required
- **Request Body**:
  ```json
  {
    "reaction_type_id": 1
  }
  ```
- **Success Response**:
  - **Code**: 200 OK
  - **Content**:
    ```json
    {
      "message": "Reaction added",
      "reaction_type": "like"
    }
    ```

#### Remove Post Reaction
Remove a reaction from a post.

- **URL**: `/api/posts/<post_id>/unreact/`
- **Method**: `DELETE`
- **Authentication**: Required
- **Success Response**:
  - **Code**: 200 OK
  - **Content**:
    ```json
    {
      "message": "Reaction removed"
    }
    ```

#### React to Comment
React to a comment or change an existing reaction.

- **URL**: `/api/posts/comments/<comment_id>/react/`
- **Method**: `POST`
- **Authentication**: Required
- **Request Body**:
  ```json
  {
    "reaction_type_id": 1
  }
  ```
- **Success Response**:
  - **Code**: 200 OK
  - **Content**:
    ```json
    {
      "message": "Reaction added",
      "reaction_type": "like"
    }
    ```

#### Remove Comment Reaction
Remove a reaction from a comment.

- **URL**: `/api/posts/comments/<comment_id>/unreact/`
- **Method**: `DELETE`
- **Authentication**: Required
- **Success Response**:
  - **Code**: 200 OK
  - **Content**:
    ```json
    {
      "message": "Reaction removed"
    }
    ```

### Share Operations

#### Share Post
Share a post.

- **URL**: `/api/posts/<post_id>/share/`
- **Method**: `POST`
- **Authentication**: Required
- **Request Body**:
  ```json
  {
    "additional_content": "Check out this post!"
  }
  ```
- **Success Response**:
  - **Code**: 201 CREATED
  - **Content**: Share information

### Search Operations

#### Search Posts
Search for posts by content, hashtags, or user.

- **URL**: `/api/posts/search/?q=<query>`
- **Method**: `GET`
- **Authentication**: Required
- **Query Parameters**:
  - `q`: Search query
  - `page`: Page number (default: 1)
  - `page_size`: Number of posts per page (default: 10, max: 50)
- **Success Response**:
  - **Code**: 200 OK
  - **Content**: Paginated list of matching posts

#### Get Posts by Hashtag
Get posts with a specific hashtag.

- **URL**: `/api/posts/hashtag/<hashtag_name>/`
- **Method**: `GET`
- **Authentication**: Required
- **Query Parameters**:
  - `page`: Page number (default: 1)
  - `page_size`: Number of posts per page (default: 10, max: 50)
- **Success Response**:
  - **Code**: 200 OK
  - **Content**: Paginated list of posts with the hashtag

#### Get Trending Hashtags
Get trending hashtags based on recent post activity.

- **URL**: `/api/posts/trending-hashtags/`
- **Method**: `GET`
- **Authentication**: Required
- **Success Response**:
  - **Code**: 200 OK
  - **Content**: List of trending hashtags with post counts

### Tag Operations

#### Tag User in Post
Tag a user in a post.

- **URL**: `/api/posts/<post_id>/tag-user/`
- **Method**: `POST`
- **Authentication**: Required
- **Request Body**:
  ```json
  {
    "user_id": 2,
    "x_position": 0.5,
    "y_position": 0.5
  }
  ```
- **Success Response**:
  - **Code**: 201 CREATED
  - **Content**: Tag information

#### Remove User Tag
Remove a user tag from a post.

- **URL**: `/api/posts/<post_id>/untag-user/<user_id>/`
- **Method**: `DELETE`
- **Authentication**: Required
- **Success Response**:
  - **Code**: 200 OK
  - **Content**:
    ```json
    {
      "message": "Tag removed"
    }
    ```

#### Get Trends
Get trending hashtags and their associated posts.

- **URL**: `/api/posts/trends/`
- **Method**: `GET`
- **Authentication**: Required
- **Success Response**:
  - **Code**: 200 OK
  - **Content**:  
    ```json
    [
      {
        "hashtag": "python",
        "post_count": 3,
        "posts": [
          {
            "id": 1,
            "content": "Learning #python is fun!",
            // ...other post fields...
          }
          // ...up to 5 posts per trend...
        ]
      }
      // ...other trends...
    ]
    ```
- **Description**:  
  Returns a list of the top 10 trending hashtags, each with the number of posts and up to 5 recent posts for that hashtag.


#### Get Trend Posts
Get all posts associated with a specific trend/hashtag with pagination.

- **URL**: `/api/posts/trend/<hashtag_name>/`
- **Method**: `GET`
- **Authentication**: Required
- **URL Parameters**:
  - `hashtag_name`: Name of the hashtag (case insensitive)
- **Query Parameters**:
  - `page`: Page number (default: 1)
  - `page_size`: Number of posts per page (default: 10)
- **Success Response**:
  - **Code**: 200 OK
  - **Content**:
    ```json
    {
      "count": 25,
      "next": "http://api.example.com/api/posts/trends/python/posts/?page=2",
      "previous": null,
      "results": [
        {
          "id": 1,
          "content": "Learning #python today!",
          "created_at": "2024-03-15T10:30:00Z",
          // ...other post fields...
        }
        // ...more posts...
      ]
    }
    ```
- **Error Response**:
  - **Code**: 404 NOT FOUND
  - **Content**:
    ```json
    {
      "error": "Trend not found"
    }
    ```
