"""
Views for the accounts app.

Handles: Login, Logout, Register, Profile, Password Change.
Uses DRF Generic Views and ViewSets for clean, reusable code.
"""
from rest_framework import generics, status, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model

from .serializers import (
    CustomTokenObtainPairSerializer,
    UserSerializer,
    UserCreateSerializer,
    UserUpdateSerializer,
    ChangePasswordSerializer,
)
from .permissions import IsAdminUser
from apps.activity_logs.models import ActivityLog

User = get_user_model()


# ─────────────────────────────────────────────────────────────
# AUTHENTICATION VIEWS
# ─────────────────────────────────────────────────────────────
class LoginView(TokenObtainPairView):
    """
    POST /api/v1/auth/login/
    Authenticates user with email + password.
    Returns: access token, refresh token, user info.
    """
    serializer_class = CustomTokenObtainPairSerializer
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        if response.status_code == status.HTTP_200_OK:
            email = request.data.get('email')
            user = User.objects.filter(email=email).first()
            if user:
                ActivityLog.log(
                    user=user,
                    action=ActivityLog.ActionType.LOGIN,
                    model_name='CustomUser',
                    object_id=user.id,
                    description=f"User {user.email} logged in via JWT.",
                    request=request
                )
        return response


class LogoutView(APIView):
    """
    POST /api/v1/auth/logout/
    Invalidates the refresh token to log the user out.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data.get('refresh_token')
            if not refresh_token:
                return Response(
                    {'error': 'Refresh token is required.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            # Blacklist (invalidate) the refresh token
            token = RefreshToken(refresh_token)
            token.blacklist()

            ActivityLog.log(
                user=request.user,
                action=ActivityLog.ActionType.LOGOUT,
                model_name='CustomUser',
                object_id=request.user.id,
                description=f"User {request.user.email} logged out.",
                request=request
            )

            return Response(
                {'message': 'Successfully logged out.'},
                status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )


# ─────────────────────────────────────────────────────────────
# PROFILE VIEWS
# ─────────────────────────────────────────────────────────────
class ProfileView(generics.RetrieveUpdateAPIView):
    """
    GET  /api/v1/auth/profile/   → View own profile
    PUT  /api/v1/auth/profile/   → Update own profile
    PATCH /api/v1/auth/profile/  → Partial update
    """
    permission_classes = [IsAuthenticated]

    def get_object(self):
        # Always return the currently logged-in user's profile
        return self.request.user

    def get_serializer_class(self):
        # Use different serializers for reading vs writing
        if self.request.method == 'GET':
            return UserSerializer
        return UserUpdateSerializer


class ChangePasswordView(APIView):
    """
    POST /api/v1/auth/change-password/
    Allows authenticated users to change their password.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data)

        if serializer.is_valid():
            user = request.user

            # Check if old password is correct
            if not user.check_password(serializer.validated_data['old_password']):
                return Response(
                    {'old_password': 'Incorrect old password.'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Set and save new password (Django hashes it automatically)
            user.set_password(serializer.validated_data['new_password'])
            user.save()

            return Response(
                {'message': 'Password changed successfully.'},
                status=status.HTTP_200_OK
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ─────────────────────────────────────────────────────────────
# USER MANAGEMENT (Admin Only)
# ─────────────────────────────────────────────────────────────
class UserViewSet(viewsets.ModelViewSet):
    """
    Admin-only ViewSet for managing all users.

    GET    /api/v1/auth/users/          → List all users
    POST   /api/v1/auth/users/          → Create a user
    GET    /api/v1/auth/users/{id}/     → Get specific user
    PUT    /api/v1/auth/users/{id}/     → Update user
    DELETE /api/v1/auth/users/{id}/     → Delete user
    """
    queryset = User.objects.all().order_by('-created_at')
    permission_classes = [IsAdminUser]

    # Search by name, email, role
    search_fields = ['email', 'first_name', 'last_name', 'role']
    filterset_fields = ['role', 'is_active', 'gender']
    ordering_fields = ['created_at', 'first_name', 'email']

    def get_serializer_class(self):
        if self.action == 'create':
            return UserCreateSerializer
        if self.action in ['update', 'partial_update']:
            return UserUpdateSerializer
        return UserSerializer

    def destroy(self, request, *args, **kwargs):
        """
        Override delete to prevent admin from deleting themselves.
        """
        user = self.get_object()
        if user == request.user:
            return Response(
                {'error': 'You cannot delete your own account.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        self.perform_destroy(user)
        return Response(
            {'message': 'User deleted successfully.'},
            status=status.HTTP_204_NO_CONTENT
        )
