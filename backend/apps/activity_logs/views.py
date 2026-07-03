"""
Views for the activity_logs app.
"""
from rest_framework import viewsets, filters
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from .models import ActivityLog
from .serializers import ActivityLogSerializer
from apps.accounts.permissions import IsAdminUser


class ActivityLogViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ReadOnlyViewSet for viewing activity logs.
    Only accessible to Admins.
    """
    queryset = ActivityLog.objects.select_related('user').all()
    serializer_class = ActivityLogSerializer
    permission_classes = [IsAdminUser]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['description', 'model_name', 'user__first_name', 'user__last_name']
    filterset_fields = ['action', 'model_name', 'user']
    ordering_fields = ['timestamp']
    ordering = ['-timestamp']
