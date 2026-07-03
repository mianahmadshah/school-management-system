"""
ViewSets for Announcements management.
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

from apps.announcements.models import Announcement
from apps.announcements.serializers import AnnouncementSerializer
from apps.accounts.permissions import IsAdminUser, IsAdminOrTeacher
from api.v1.pagination import StandardResultsSetPagination


class AnnouncementViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Announcement management.
    
    Endpoints:
    - GET    /api/v1/announcements/         - List announcements
    - POST   /api/v1/announcements/         - Create announcement (teacher/admin)
    - GET    /api/v1/announcements/{id}/    - Get announcement details
    - PUT    /api/v1/announcements/{id}/    - Update announcement (owner/admin)
    - DELETE /api/v1/announcements/{id}/    - Delete announcement (owner/admin)
    """
    queryset = Announcement.objects.select_related(
        'published_by', 'target_class', 'target_section'
    ).all()
    serializer_class = AnnouncementSerializer
    pagination_class = StandardResultsSetPagination
    
    filter_backends = [
        DjangoFilterBackend,
        SearchFilter,
        OrderingFilter
    ]
    filterset_fields = ['target_audience', 'target_class', 'target_section']
    search_fields = ['title', 'content']
    ordering_fields = ['published_date', 'title']
    ordering = ['-published_date']
    
    def get_permissions(self):
        """Override permissions per action."""
        if self.action in ['create']:
            permission_classes = [IsAdminOrTeacher]
        elif self.action in ['update', 'partial_update', 'destroy']:
            permission_classes = [IsAdminUser]
        else:
            permission_classes = [IsAuthenticated]
        
        return [permission() for permission in permission_classes]
    
    def perform_create(self, serializer):
        """Set the published_by user to the current user."""
        serializer.save(published_by=self.request.user)
    
    @action(detail=False, methods=['get'])
    def active(self, request):
        """Get active (published) announcements."""
        active_announcements = Announcement.objects.filter(
            is_published=True
        )
        
        # Filter by user role if student
        if request.user.role == 'STUDENT':
            from django.db.models import Q
            active_announcements = active_announcements.filter(
                Q(target_audience='ALL') |
                Q(target_audience='STUDENTS') |
                Q(target_audience='SPECIFIC_CLASS', target_class=request.user.student_profile.current_class) |
                Q(target_audience='SPECIFIC_SECTION', target_section=request.user.student_profile.current_section)
            )
        elif request.user.role == 'TEACHER':
            active_announcements = active_announcements.filter(
                target_audience__in=['ALL', 'TEACHERS']
            )
        
        serializer = AnnouncementSerializer(active_announcements, many=True)
        return Response({
            'count': active_announcements.count(),
            'results': serializer.data
        })
    
    @action(detail=False, methods=['get'])
    def for_me(self, request):
        """Get announcements relevant to the current user."""
        from django.db.models import Q
        
        if request.user.role == 'STUDENT':
            # Student sees announcements for ALL, STUDENTS, or their specific class/section
            announcements = Announcement.objects.filter(
                is_published=True,
                target_audience__in=['ALL', 'STUDENTS']
            ) | Announcement.objects.filter(
                is_published=True,
                target_audience='SPECIFIC_CLASS', target_class=request.user.student_profile.current_class
            ) | Announcement.objects.filter(
                is_published=True,
                target_audience='SPECIFIC_SECTION', target_section=request.user.student_profile.current_section
            )
        elif request.user.role == 'TEACHER':
            # Teachers see announcements for ALL and TEACHERS
            announcements = Announcement.objects.filter(
                is_published=True,
                target_audience__in=['ALL', 'TEACHERS']
            )
        else:
            # Admins see all announcements
            announcements = Announcement.objects.all()
        
        announcements = announcements.order_by('-id')
        serializer = AnnouncementSerializer(announcements, many=True)
        return Response({
            'count': announcements.count(),
            'results': serializer.data
        })
