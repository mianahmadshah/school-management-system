"""
ViewSets for Account/User management.
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

from apps.accounts.models import CustomUser
from apps.accounts.serializers import (
    UserSerializer, UserCreateSerializer, UserUpdateSerializer
)
from apps.accounts.permissions import IsAdminUser, IsOwnerOrAdmin
from api.v1.pagination import StandardResultsSetPagination


class UserViewSet(viewsets.ModelViewSet):
    """
    ViewSet for User management.
    
    Endpoints:
    - GET    /api/v1/users/              - List users
    - POST   /api/v1/users/              - Create user (admin only)
    - GET    /api/v1/users/{id}/         - Get user details
    - PUT    /api/v1/users/{id}/         - Update user (admin or owner)
    - DELETE /api/v1/users/{id}/         - Delete user (admin only)
    - GET    /api/v1/users/me/           - Get current user profile
    - PUT    /api/v1/users/me/           - Update current user profile
    """
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer
    pagination_class = StandardResultsSetPagination
    
    filter_backends = [
        DjangoFilterBackend,
        SearchFilter,
        OrderingFilter
    ]
    filterset_fields = ['role', 'is_active', 'is_staff']
    search_fields = ['first_name', 'last_name', 'email', 'username']
    ordering_fields = ['date_joined', 'first_name', 'email']
    ordering = ['-date_joined']
    
    def get_permissions(self):
        """
        Override permissions per action.
        - list/retrieve: Authenticated users
        - create/update/destroy: Admin only
        - me: Authenticated user
        """
        if self.action in ['create', 'destroy']:
            permission_classes = [IsAdminUser]
        elif self.action == 'update' or self.action == 'partial_update':
            permission_classes = [IsAdminUser | IsOwnerOrAdmin]
        elif self.action == 'me':
            permission_classes = [IsAuthenticated]
        else:
            permission_classes = [IsAdminUser]
        
        return [permission() for permission in permission_classes]
    
    def get_serializer_class(self):
        """Use appropriate serializer for each action."""
        if self.action == 'create':
            return UserCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return UserUpdateSerializer
        elif self.action == 'me':
            return UserSerializer
        return UserSerializer
    
    @action(detail=False, methods=['get', 'put'], permission_classes=[IsAuthenticated])
    def me(self, request):
        """
        Get or update current authenticated user's profile.
        
        GET  /api/v1/users/me/  - Get own profile
        PUT  /api/v1/users/me/  - Update own profile
        """
        if request.method == 'PUT':
            serializer = UserUpdateSerializer(
                request.user,
                data=request.data,
                partial=True
            )
            if serializer.is_valid():
                serializer.save()
                return Response(UserSerializer(request.user).data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        serializer = UserSerializer(request.user)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'], permission_classes=[IsAdminUser])
    def set_password(self, request, pk=None):
        """Set password for a user (admin only)."""
        user = self.get_object()
        if 'password' in request.data:
            user.set_password(request.data['password'])
            user.save()
            return Response({'status': 'password set'}, status=status.HTTP_200_OK)
        return Response(
            {'error': 'password field required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    @action(detail=True, methods=['post'], permission_classes=[IsAdminUser])
    def deactivate(self, request, pk=None):
        """Deactivate a user account (admin only)."""
        user = self.get_object()
        user.is_active = False
        user.save()
        return Response({'status': 'user deactivated'}, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['post'], permission_classes=[IsAdminUser])
    def activate(self, request, pk=None):
        """Activate a deactivated user account (admin only)."""
        user = self.get_object()
        user.is_active = True
        user.save()
        return Response({'status': 'user activated'}, status=status.HTTP_200_OK)
