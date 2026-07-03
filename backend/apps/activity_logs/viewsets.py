"""
ViewSets for Activity Logs management (audit trail).
"""
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

from apps.activity_logs.models import ActivityLog
from apps.activity_logs.serializers import ActivityLogSerializer
from apps.accounts.permissions import IsAdminUser
from api.v1.pagination import StandardResultsSetPagination


class ActivityLogViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for Activity Logs (read-only).
    
    Endpoints:
    - GET    /api/v1/logs/                     - List all activity logs (admin only)
    - GET    /api/v1/logs/{id}/                - Get activity log details (admin only)
    - GET    /api/v1/logs/user/{id}/           - Get user's activity (admin or own)
    - GET    /api/v1/logs/by_action/           - Filter by action type
    """
    queryset = ActivityLog.objects.all()
    serializer_class = ActivityLogSerializer
    pagination_class = StandardResultsSetPagination
    permission_classes = [IsAdminUser]
    
    filter_backends = [
        DjangoFilterBackend,
        SearchFilter,
        OrderingFilter
    ]
    filterset_fields = ['action', 'user', 'timestamp']
    search_fields = ['user__first_name', 'user__last_name', 'description']
    ordering_fields = ['timestamp', 'action']
    ordering = ['-timestamp']
    
    @action(detail=False, methods=['get'])
    def by_user(self, request):
        """Get activity logs for a specific user."""
        user_id = request.query_params.get('user_id')
        if not user_id:
            return Response(
                {'error': 'user_id parameter required'},
                status=400
            )
        
        # Users can only view their own activity unless they're admin
        from django.http import HttpResponseForbidden
        if request.user.role != 'ADMIN' and str(request.user.id) != user_id:
            return Response(
                {'error': 'You can only view your own activity'},
                status=403
            )
        
        logs = ActivityLog.objects.filter(user_id=user_id).order_by('-timestamp')
        serializer = ActivityLogSerializer(logs, many=True)
        
        return Response({
            'user_id': user_id,
            'count': logs.count(),
            'results': serializer.data
        })
    
    @action(detail=False, methods=['get'])
    def by_action(self, request):
        """Get activity logs filtered by action type."""
        action_type = request.query_params.get('action')
        if not action_type:
            return Response(
                {'error': 'action parameter required'},
                status=400
            )
        
        logs = ActivityLog.objects.filter(action=action_type).order_by('-timestamp')
        serializer = ActivityLogSerializer(logs, many=True)
        
        return Response({
            'action': action_type,
            'count': logs.count(),
            'results': serializer.data
        })
    
    @action(detail=False, methods=['get'])
    def by_model(self, request):
        """Get activity logs for a specific model."""
        model_name = request.query_params.get('model')
        if not model_name:
            return Response(
                {'error': 'model parameter required'},
                status=400
            )
        
        logs = ActivityLog.objects.filter(model_name=model_name).order_by('-timestamp')
        serializer = ActivityLogSerializer(logs, many=True)
        
        return Response({
            'model': model_name,
            'count': logs.count(),
            'results': serializer.data
        })
    
    @action(detail=False, methods=['get'])
    def summary(self, request):
        """Get summary of activities."""
        from django.db.models import Count
        
        # Count by action
        by_action = ActivityLog.objects.values('action').annotate(
            count=Count('id')
        ).order_by('-count')
        
        # Count by user (top users)
        from django.db.models import Count
        by_user = ActivityLog.objects.values('user__first_name', 'user__last_name').annotate(
            count=Count('id')
        ).order_by('-count')[:10]
        
        # Total logs
        total_logs = ActivityLog.objects.count()
        
        return Response({
            'total_logs': total_logs,
            'by_action': by_action,
            'top_users': by_user
        })
