"""
Views for the attendance app.
"""
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
import datetime

from .models import Attendance
from .serializers import AttendanceSerializer, BulkAttendanceSerializer
from apps.accounts.permissions import IsAdminUser, IsAdminOrTeacher


class AttendanceViewSet(viewsets.ModelViewSet):
    """
    CRUD ViewSet for Attendance.
    """
    serializer_class = AttendanceSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['student__user__first_name', 'student__user__last_name', 'student__admission_number']
    filterset_fields = ['school_class', 'section', 'date', 'status', 'student']
    ordering_fields = ['date', 'student__user__first_name']
    ordering = ['-date', 'school_class', 'section', 'student__user__first_name']

    def get_permissions(self):
        # Students can view their own attendance, Teachers and Admins can do more
        return [IsAuthenticated()]

    def get_queryset(self):
        """
        Filter queryset based on user role.
        Admins/Teachers see all attendance.
        Students see only their own.
        """
        user = self.request.user
        qs = Attendance.objects.select_related(
            'student__user', 'school_class', 'section', 'marked_by'
        )

        if user.is_student:
            return qs.filter(student__user=user)
        return qs.all()

    def create(self, request, *args, **kwargs):
        """
        Create a single attendance record. Requires Admin or Teacher role.
        """
        if not (request.user.is_admin or request.user.is_teacher):
            return Response(
                {"detail": "You do not have permission to mark attendance."},
                status=status.HTTP_403_FORBIDDEN
            )
            
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        # Assign marked_by automatically
        serializer.save(marked_by=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        if not (request.user.is_admin or request.user.is_teacher):
            return Response({"detail": "Forbidden."}, status=status.HTTP_403_FORBIDDEN)
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        if not request.user.is_admin:
            return Response(
                {"detail": "Only admins can delete attendance records."},
                status=status.HTTP_403_FORBIDDEN
            )
        return super().destroy(request, *args, **kwargs)

    @action(detail=False, methods=['post'], permission_classes=[IsAdminOrTeacher])
    def bulk_mark(self, request):
        """
        POST /api/v1/attendance/bulk_mark/
        Allows marking attendance for an entire section at once.
        """
        serializer = BulkAttendanceSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        result = serializer.save()
        
        return Response({
            "message": "Attendance marked successfully.",
            "details": result
        }, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'], permission_classes=[IsAdminOrTeacher])
    def today_stats(self, request):
        """
        GET /api/v1/attendance/today_stats/
        Returns today's attendance summary for the school.
        """
        today = datetime.date.today()
        qs = Attendance.objects.filter(date=today)
        
        total_marked = qs.count()
        present = qs.filter(status='PRESENT').count()
        absent = qs.filter(status='ABSENT').count()
        late = qs.filter(status='LATE').count()
        half_day = qs.filter(status='HALF_DAY').count()
        on_leave = qs.filter(status='LEAVE').count()

        return Response({
            "date": today,
            "total_marked": total_marked,
            "present": present,
            "absent": absent,
            "late": late,
            "half_day": half_day,
            "on_leave": on_leave
        })
