from channels.middleware import BaseMiddleware
from channels.db import database_sync_to_async
from django.contrib.auth.models import AnonymousUser
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from django.contrib.auth import get_user_model
import logging

User = get_user_model()
logger = logging.getLogger(__name__)

@database_sync_to_async
def get_user(user_id):
    try:
        return User.objects.get(id=user_id)
    except User.DoesNotExist:
        return AnonymousUser()

class TokenAuthMiddleware(BaseMiddleware):
    async def __call__(self, scope, receive, send):
        # Extract query parameters
        query_string = scope.get('query_string', b'').decode()
        query_params = dict(item.split('=') for item in query_string.split('&') if item and '=' in item)
        
        # Get token from query string
        token = query_params.get('token')
        
        # Set anonymous user as default
        scope['user'] = AnonymousUser()
        
        if token:
            try:
                # Verify token and extract user ID
                access_token = AccessToken(token)
                user_id = access_token.get('user_id')
                
                # Get and set authenticated user
                scope['user'] = await get_user(user_id)
                logger.info(f"Authenticated WebSocket user: {scope['user'].username}")
            except (InvalidToken, TokenError) as e:
                logger.error(f"Token authentication failed: {str(e)}")
            except Exception as e:
                logger.error(f"WebSocket auth error: {str(e)}")
        
        return await super().__call__(scope, receive, send)

def TokenAuthMiddlewareStack(inner):
    return TokenAuthMiddleware(inner)
