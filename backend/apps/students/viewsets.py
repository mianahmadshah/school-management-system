"""
ViewSets for Student management.
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

from apps.students.models import Student
from apps.students.serializers import StudentListSerializer, StudentDetailSerializer
from apps.accounts.permissions import IsAdminUser, IsStudentUser, IsAdminOrTeacher
from apps.attendance.serializers import AttendanceSerializer
from apps.examinations.serializers import ResultSerializer
from apps.fees.serializers import FeeInvoiceSerializer
from api.v1.pagination import StandardResultsSetPagination


class StudentViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Student management.
    
    Endpoints:
    - GET    /api/v1/students/                  - List students
    - POST   /api/v1/students/                  - Create student (admin only)
    - GET    /api/v1/students/{id}/             - Get student details
    - PUT    /api/v1/students/{id}/             - Update student (admin only)
    - DELETE /api/v1/students/{id}/             - Delete student (admin only)
    - GET    /api/v1/students/{id}/attendance/  - Get student's attendance
    - GET    /api/v1/students/{id}/results/     - Get student's results
    - GET    /api/v1/students/{id}/fees/        - Get student's fees
    """
    queryset = Student.objects.select_related(
        'user', 'current_class', 'current_section'
    ).all()
    serializer_class = StudentListSerializer
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return StudentDetailSerializer
        return StudentListSerializer
    pagination_class = StandardResultsSetPagination
    
    filter_backends = [
        DjangoFilterBackend,
        SearchFilter,
        OrderingFilter
    ]
    filterset_fields = ['status', 'current_class', 'gender']
    search_fields = [
        'user__first_name', 'user__last_name', 'admission_number',
        'user__email', 'roll_number'
    ]
    ordering_fields = ['admission_number', 'user__first_name', 'roll_number']
    ordering = ['admission_number']
    
    def get_permissions(self):
        """
        Override permissions per action.
        - list: Authenticated users
        - create/update/destroy: Admin only
        - retrieve: Authenticated users
        - attendance/results/fees: Authenticated users
        """
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes = [IsAdminUser]
        else:
            permission_classes = [IsAuthenticated]
        
        return [permission() for permission in permission_classes]
    
    @action(detail=True, methods=['get'])
    def attendance(self, request, pk=None):
        """Get student's attendance records."""
        student = self.get_object()
        attendance = student.attendance_records.all()
        
        # Add filters if provided
        status_filter = request.query_params.get('status')
        if status_filter:
            attendance = attendance.filter(status=status_filter)
        
        serializer = AttendanceSerializer(attendance, many=True)
        return Response({
            'count': attendance.count(),
            'results': serializer.data
        })
    
    @action(detail=True, methods=['get'])
    def results(self, request, pk=None):
        """Get student's results."""
        student = self.get_object()
        results = student.results.all()
        
        # Add filters if provided
        academic_year = request.query_params.get('academic_year')
        if academic_year:
            results = results.filter(academic_year=academic_year)
        
        serializer = ResultSerializer(results, many=True)
        return Response({
            'count': results.count(),
            'results': serializer.data
        })
    
    @action(detail=True, methods=['get'])
    def fees(self, request, pk=None):
        """Get student's fee invoices."""
        student = self.get_object()
        invoices = student.fee_invoices.all()
        
        # Add filters if provided
        status_filter = request.query_params.get('status')
        if status_filter:
            invoices = invoices.filter(status=status_filter)
        
        serializer = FeeInvoiceSerializer(invoices, many=True)
        return Response({
            'count': invoices.count(),
            'results': serializer.data
        })
    
    @action(detail=True, methods=['get'])
    def summary(self, request, pk=None):
        """Get student's academic summary."""
        student = self.get_object()
        
        attendance_total = student.attendance_records.count()
        attendance_present = student.attendance_records.filter(status='PRESENT').count()
        
        results = student.results.all()
        results_count = results.count()
        
        fees_due = student.fee_invoices.filter(status='PENDING').aggregate(
            total=models.Sum('balance_due')
        )['total'] or 0
        
        return Response({
            'student_id': student.id,
            'admission_number': student.admission_number,
            'full_name': student.full_name,
            'current_class': str(student.current_class),
            'current_section': str(student.current_section),
            'attendance': {
                'total': attendance_total,
                'present': attendance_present,
                'percentage': (attendance_present / attendance_total * 100) if attendance_total > 0 else 0
            },
            'academics': {
                'total_results': results_count
            },
            'fees': {
                'total_due': float(fees_due)
            }
        })
