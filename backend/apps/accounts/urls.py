"""
URL patterns for the accounts app.
All routes are prefixed with /api/v1/auth/ from config/urls.py
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView

from .views import (
    LoginView,
    LogoutView,
    ProfileView,
    ChangePasswordView,
    UserViewSet,
)

# Router automatically generates CRUD URLs for ViewSets
router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')

urlpatterns = [
    # ─── JWT Auth Endpoints ────────────────────────────────
    # POST  /api/v1/auth/login/
    path('login/', LoginView.as_view(), name='token_obtain_pair'),

    # POST  /api/v1/auth/token/refresh/
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # POST  /api/v1/auth/logout/
    path('logout/', LogoutView.as_view(), name='logout'),

    # ─── Profile Endpoints ─────────────────────────────────
    # GET/PUT/PATCH  /api/v1/auth/profile/
    path('profile/', ProfileView.as_view(), name='profile'),

    # POST  /api/v1/auth/change-password/
    path('change-password/', ChangePasswordView.as_view(), name='change_password'),

    # ─── Admin User Management ─────────────────────────────
    # Generates: /api/v1/auth/users/, /api/v1/auth/users/{id}/
    path('', include(router.urls)),
]
