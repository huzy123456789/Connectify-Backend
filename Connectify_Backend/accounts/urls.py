from django.urls import path
from .views import LoginView, CustomTokenRefreshView, AdminOnlyView, UserOnlyView

app_name = 'accounts'

urlpatterns = [
    path('login/', LoginView.as_view(), name='login'),
    path('token/refresh/', CustomTokenRefreshView.as_view(), name='token_refresh'),
    path('admin-only/', AdminOnlyView.as_view(), name='admin_only'),
    path('user-only/', UserOnlyView.as_view(), name='user_only'),
] 