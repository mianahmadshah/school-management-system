"""
Views for the announcements app.
"""
from rest_framework import viewsets, filters, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q

from .models import Announcement
from .serializers import AnnouncementSerializer
from apps.accounts.permissions import IsAdminUser, IsAdminOrTeacher


class AnnouncementViewSet(viewsets.ModelViewSet):
    """CRUD ViewSet for Announcements."""
    serializer_class = AnnouncementSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'content']
    filterset_fields = ['target_audience', 'is_active']
    ordering_fields = ['created_at']
    ordering = ['-created_at']

    def get_queryset(self):
        qs = Announcement.objects.select_related('created_by', 'target_class').filter(is_active=True)
        user = self.request.user

        if user.is_admin:
            # Admins see everything, including inactive
            return Announcement.objects.select_related('created_by', 'target_class').all()

        if user.is_teacher:
            # Teachers see ALL and TEACHERS
            return qs.filter(Q(target_audience='ALL') | Q(target_audience='TEACHERS'))

        if user.is_student:
            student = getattr(user, 'student_profile', None)
            if student and student.current_class:
                # Students see ALL, STUDENTS, and SPECIFIC_CLASS (if it matches theirs)
                return qs.filter(
                    Q(target_audience='ALL') | 
                    Q(target_audience='STUDENTS') | 
                    Q(target_audience='SPECIFIC_CLASS', target_class=student.current_class)
                )
            return qs.filter(Q(target_audience='ALL') | Q(target_audience='STUDENTS'))

        return qs.none()

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            # Only Admins and Teachers can create announcements
            return [IsAdminOrTeacher()]
        return [IsAuthenticated()]

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
