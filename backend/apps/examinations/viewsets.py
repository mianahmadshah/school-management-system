"""
ViewSets for Examination, Marks, and Results management.
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

from apps.examinations.models import Exam, Marks, Result
from apps.examinations.serializers import (
    ExamSerializer, MarksSerializer, ResultSerializer
)
from apps.accounts.permissions import IsAdminUser, IsAdminOrTeacher
from api.v1.pagination import StandardResultsSetPagination


class ExamViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Exam management.
    
    Endpoints:
    - GET    /api/v1/exams/         - List exams
    - POST   /api/v1/exams/         - Create exam (admin only)
    - GET    /api/v1/exams/{id}/    - Get exam details
    - PUT    /api/v1/exams/{id}/    - Update exam (admin only)
    - DELETE /api/v1/exams/{id}/    - Delete exam (admin only)
    """
    queryset = Exam.objects.select_related(
        'subject', 'class_obj', 'creator'
    ).all()
    serializer_class = ExamSerializer
    pagination_class = StandardResultsSetPagination
    
    filter_backends = [
        DjangoFilterBackend,
        SearchFilter,
        OrderingFilter
    ]
    filterset_fields = ['subject', 'class_obj', 'exam_date']
    search_fields = ['name', 'subject__name']
    ordering_fields = ['exam_date', 'name']
    ordering = ['-exam_date']
    
    def get_permissions(self):
        """Override permissions per action."""
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes = [IsAdminUser]
        else:
            permission_classes = [IsAuthenticated]
        
        return [permission() for permission in permission_classes]


class MarksViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Marks management.
    
    Endpoints:
    - GET    /api/v1/marks/              - List marks
    - POST   /api/v1/marks/              - Enter marks (teacher/admin)
    - POST   /api/v1/marks/bulk_create/ - Bulk enter marks
    - GET    /api/v1/marks/{id}/         - Get mark record
    - PUT    /api/v1/marks/{id}/         - Update mark (teacher/admin)
    """
    queryset = Marks.objects.select_related(
        'exam', 'student', 'subject', 'entered_by'
    ).all()
    serializer_class = MarksSerializer
    pagination_class = StandardResultsSetPagination
    
    filter_backends = [
        DjangoFilterBackend,
        SearchFilter,
        OrderingFilter
    ]
    filterset_fields = ['exam', 'subject', 'is_passed']
    search_fields = ['student__user__first_name', 'student__user__last_name']
    ordering_fields = ['marks_obtained', 'exam__exam_date']
    ordering = ['-exam__exam_date']
    
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
        Bulk enter marks for multiple students.
        
        Expected format:
        {
            "exam_id": 1,
            "subject_id": 1,
            "marks": [
                {
                    "student_id": 1,
                    "marks_obtained": 85
                },
                {
                    "student_id": 2,
                    "marks_obtained": 92
                },
                ...
            ]
        }
        """
        # For now, manual marks entry loop
        marks_records = []
        for record_data in request.data.get('marks', []):
            record_data['exam_id'] = request.data.get('exam_id')
            record_data['subject_id'] = request.data.get('subject_id')
            record_data['entered_by_id'] = request.user.id
            mark = Marks.objects.create(**record_data)
            marks_records.append(mark)
        
        return Response({
            'status': 'success',
            'created': len(marks_records),
            'message': f'Marks entered for {len(marks_records)} students'
        }, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=['get'])
    def details(self, request, pk=None):
        """Get detailed mark information including grade and status."""
        mark = self.get_object()
        serializer = MarksSerializer(mark)
        return Response({
            'exam': str(mark.exam),
            'subject': str(mark.subject),
            'student': str(mark.student),
            'marks_obtained': mark.marks_obtained,
            'total_marks': mark.exam.total_marks,
            'percentage': (mark.marks_obtained / mark.exam.total_marks * 100) if mark.exam.total_marks > 0 else 0,
            'grade': mark.grade,
            'is_passed': mark.is_passed,
            'entered_by': str(mark.entered_by),
            'entered_at': mark.entered_at
        })


class ResultViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Results management.
    
    Endpoints:
    - GET    /api/v1/results/                 - List results
    - GET    /api/v1/results/{id}/            - Get result details
    - GET    /api/v1/results/student/{id}/    - Get student's results
    """
    queryset = Result.objects.select_related(
        'student', 'class_obj'
    ).all()
    serializer_class = ResultSerializer
    pagination_class = StandardResultsSetPagination
    
    filter_backends = [
        DjangoFilterBackend,
        SearchFilter,
        OrderingFilter
    ]
    filterset_fields = ['class_obj', 'status', 'academic_year']
    search_fields = ['student__user__first_name', 'student__user__last_name']
    ordering_fields = ['academic_year', 'student__user__first_name']
    ordering = ['-academic_year']
    
    def get_permissions(self):
        """Override permissions per action."""
        permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]
    
    @action(detail=False, methods=['get'])
    def by_student(self, request):
        """Get results for a specific student."""
        student_id = request.query_params.get('student_id')
        if not student_id:
            return Response(
                {'error': 'student_id parameter required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        results = Result.objects.filter(student_id=student_id)
        serializer = ResultSerializer(results, many=True)
        return Response({
            'student_id': student_id,
            'count': results.count(),
            'results': serializer.data
        })
    
    @action(detail=False, methods=['get'])
    def by_class(self, request):
        """Get results for a specific class."""
        class_id = request.query_params.get('class_id')
        if not class_id:
            return Response(
                {'error': 'class_id parameter required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        results = Result.objects.filter(class_obj_id=class_id)
        
        # Add filtering by academic year if provided
        academic_year = request.query_params.get('academic_year')
        if academic_year:
            results = results.filter(academic_year=academic_year)
        
        serializer = ResultSerializer(results, many=True)
        return Response({
            'class_id': class_id,
            'academic_year': academic_year or 'all',
            'count': results.count(),
            'results': serializer.data
        })
