"""
ViewSets for Attendance management.
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from datetime import datetime, timedelta

from apps.attendance.models import Attendance
from apps.attendance.serializers import AttendanceSerializer, BulkAttendanceSerializer
from apps.accounts.permissions import IsAdminUser, IsTeacherUser, IsAdminOrTeacher
from api.v1.pagination import StandardResultsSetPagination


class AttendanceViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Attendance management.
    
    Endpoints:
    - GET    /api/v1/attendance/              - List attendance
    - POST   /api/v1/attendance/              - Mark attendance (teacher/admin)
    - POST   /api/v1/attendance/bulk_create/ - Mark bulk attendance
    - GET    /api/v1/attendance/{id}/         - Get attendance record
    - PUT    /api/v1/attendance/{id}/         - Update attendance (teacher/admin)
    - GET    /api/v1/attendance/report/       - Get attendance report
    """
    queryset = Attendance.objects.select_related(
        'student', 'class_obj', 'section', 'marked_by'
    ).all()
    serializer_class = AttendanceSerializer
    pagination_class = StandardResultsSetPagination
    
    filter_backends = [
        DjangoFilterBackend,
        SearchFilter,
        OrderingFilter
    ]
    filterset_fields = ['status', 'class_obj', 'section', 'attendance_date']
    search_fields = ['student__user__first_name', 'student__user__last_name']
    ordering_fields = ['attendance_date', 'student__user__first_name']
    ordering = ['-attendance_date']
    
    def get_permissions(self):
        """Override permissions per action."""
        if self.action in ['create', 'update', 'partial_update', 'bulk_create']:
            permission_classes = [IsAdminOrTeacher]
        else:
            permission_classes = [IsAuthenticated]
        
        return [permission() for permission in permission_classes]
    
    @action(detail=False, methods=['post'], permission_classes=[IsAdminOrTeacher])
    def bulk_create(self, request):
        """
        Mark attendance for multiple students at once.
        
        Expected format:
        {
            "class_id": 1,
            "section_id": 1,
            "attendance_date": "2024-01-15",
            "attendance_records": [
                {
                    "student_id": 1,
                    "status": "PRESENT"
                },
                {
                    "student_id": 2,
                    "status": "ABSENT"
                },
                ...
            ]
        }
        """
        # For now, manual attendance marking loop
        attendance_records = []
        for record_data in request.data.get('attendance_records', []):
            record_data['class_obj_id'] = request.data.get('class_id')
            record_data['section_id'] = request.data.get('section_id')
            record_data['attendance_date'] = request.data.get('attendance_date')
            record_data['marked_by_id'] = request.user.id if hasattr(request.user, 'teacher_profile') else None
            attendance = Attendance.objects.create(**record_data)
            attendance_records.append(attendance)
        
        return Response({
            'status': 'success',
            'created': len(attendance_records),
            'message': f'Attendance marked for {len(attendance_records)} students'
        }, status=status.HTTP_201_CREATED)
    
    @action(detail=False, methods=['get'])
    def report(self, request):
        """
        Get attendance report with summary statistics.
        
        Query parameters:
        - class_id: Filter by class
        - section_id: Filter by section
        - student_id: Filter by student
        - start_date: Start date (YYYY-MM-DD)
        - end_date: End date (YYYY-MM-DD)
        """
        queryset = self.get_queryset()
        
        # Apply filters
        class_id = request.query_params.get('class_id')
        if class_id:
            queryset = queryset.filter(class_obj_id=class_id)
        
        section_id = request.query_params.get('section_id')
        if section_id:
            queryset = queryset.filter(section_id=section_id)
        
        student_id = request.query_params.get('student_id')
        if student_id:
            queryset = queryset.filter(student_id=student_id)
        
        start_date = request.query_params.get('start_date')
        if start_date:
            queryset = queryset.filter(attendance_date__gte=start_date)
        
        end_date = request.query_params.get('end_date')
        if end_date:
            queryset = queryset.filter(attendance_date__lte=end_date)
        
        # Generate report
        total = queryset.count()
        present = queryset.filter(status='PRESENT').count()
        absent = queryset.filter(status='ABSENT').count()
        late = queryset.filter(status='LATE').count()
        half_day = queryset.filter(status='HALF_DAY').count()
        leave = queryset.filter(status='LEAVE').count()
        
        return Response({
            'summary': {
                'total_records': total,
                'present': present,
                'absent': absent,
                'late': late,
                'half_day': half_day,
                'leave': leave,
                'percentage': (present / total * 100) if total > 0 else 0
            }
        })
    
    @action(detail=True, methods=['get'])
    def history(self, request, pk=None):
        """Get attendance history for a specific student."""
        attendance = self.get_object()
        student = attendance.student
        
        # Get student's attendance for last 30 days
        thirty_days_ago = datetime.now().date() - timedelta(days=30)
        history = Attendance.objects.filter(
            student=student,
            attendance_date__gte=thirty_days_ago
        ).order_by('-attendance_date')
        
        serializer = AttendanceSerializer(history, many=True)
        return Response({
            'student': str(student),
            'period': '30 days',
            'records': serializer.data
        })
