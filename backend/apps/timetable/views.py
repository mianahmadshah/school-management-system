"""
Views for the timetable app.
"""
from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend

from .models import Period, Timetable
from .serializers import PeriodSerializer, TimetableSerializer
from apps.accounts.permissions import IsAdminUser, IsAdminOrTeacher


class PeriodViewSet(viewsets.ModelViewSet):
    """CRUD ViewSet for Periods (Time slots)."""
    queryset = Period.objects.all()
    serializer_class = PeriodSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name']
    ordering = ['order', 'start_time']

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAdminUser()]
        return [IsAuthenticated()]


class TimetableViewSet(viewsets.ModelViewSet):
    """CRUD ViewSet for Timetable entries."""
    serializer_class = TimetableSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['school_class__name', 'section__name', 'subject__name', 'teacher__user__first_name']
    filterset_fields = ['school_class', 'section', 'day_of_week', 'teacher']
    ordering_fields = ['day_of_week', 'period__order']
    ordering = ['day_of_week', 'period__order']

    def get_queryset(self):
        qs = Timetable.objects.select_related(
            'school_class', 'section', 'period', 'subject', 'teacher__user'
        )
        user = self.request.user
        
        # Role-based filtering
        if user.is_student:
            student = getattr(user, 'student_profile', None)
            if student and student.current_class and student.section:
                return qs.filter(school_class=student.current_class, section=student.section)
            return qs.none()
            
        if user.is_teacher:
            # Teachers can see the whole school's timetable if needed, but often just theirs.
            # We'll allow them to see all, and they can filter by teacher ID in the frontend.
            return qs.all()
            
        return qs.all()

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAdminUser()]
        return [IsAuthenticated()]

    @action(detail=False, methods=['get'])
    def my_schedule(self, request):
        """
        GET /api/v1/timetable/schedule/my_schedule/
        Returns the schedule for the currently logged-in user.
        - If Student: returns their class/section timetable.
        - If Teacher: returns timetable where they are the assigned teacher.
        """
        user = request.user
        qs = self.get_queryset()

        if user.is_student:
            student = getattr(user, 'student_profile', None)
            if student:
                qs = qs.filter(school_class=student.current_class, section=student.section)
        elif user.is_teacher:
            teacher = getattr(user, 'teacher_profile', None)
            if teacher:
                qs = qs.filter(teacher=teacher)

        serializer = self.get_serializer(qs, many=True)
        return Response(serializer.data)
