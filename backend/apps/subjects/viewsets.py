"""
ViewSets for Subject and Enrollment management.
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

from apps.subjects.models import Subject, Enrollment
from apps.subjects.serializers import SubjectSerializer, EnrollmentSerializer
from apps.accounts.permissions import IsAdminUser
from api.v1.pagination import StandardResultsSetPagination


class SubjectViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Subject management.
    
    Endpoints:
    - GET    /api/v1/subjects/         - List subjects
    - POST   /api/v1/subjects/         - Create subject (admin only)
    - GET    /api/v1/subjects/{id}/    - Get subject details
    - PUT    /api/v1/subjects/{id}/    - Update subject (admin only)
    - DELETE /api/v1/subjects/{id}/    - Delete subject (admin only)
    """
    queryset = Subject.objects.select_related('class_obj', 'teacher').all()
    serializer_class = SubjectSerializer
    pagination_class = StandardResultsSetPagination
    
    filter_backends = [
        DjangoFilterBackend,
        SearchFilter,
        OrderingFilter
    ]
    filterset_fields = ['class_obj', 'teacher']
    search_fields = ['name', 'code', 'teacher__user__first_name']
    ordering_fields = ['name', 'code']
    ordering = ['name']
    
    def get_permissions(self):
        """Override permissions per action."""
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes = [IsAdminUser]
        else:
            permission_classes = [IsAuthenticated]
        
        return [permission() for permission in permission_classes]


class EnrollmentViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Student Enrollment management.
    
    Endpoints:
    - GET    /api/v1/enrollments/              - List enrollments
    - POST   /api/v1/enrollments/              - Enroll student (admin only)
    - POST   /api/v1/enrollments/bulk_create/ - Bulk enroll students
    - GET    /api/v1/enrollments/{id}/         - Get enrollment details
    - PUT    /api/v1/enrollments/{id}/         - Update enrollment (admin only)
    - DELETE /api/v1/enrollments/{id}/         - Cancel enrollment (admin only)
    """
    queryset = Enrollment.objects.select_related(
        'student', 'class_obj', 'section'
    ).all()
    serializer_class = EnrollmentSerializer
    pagination_class = StandardResultsSetPagination
    
    filter_backends = [
        DjangoFilterBackend,
        SearchFilter,
        OrderingFilter
    ]
    filterset_fields = ['class_obj', 'section', 'academic_year']
    search_fields = ['student__user__first_name', 'student__user__last_name']
    ordering_fields = ['academic_year', 'enrollment_date']
    ordering = ['-academic_year', 'enrollment_date']
    
    def get_permissions(self):
        """Override permissions per action."""
        if self.action in ['create', 'update', 'partial_update', 'destroy', 'bulk_create']:
            permission_classes = [IsAdminUser]
        else:
            permission_classes = [IsAuthenticated]
        
        return [permission() for permission in permission_classes]
    
    @action(detail=False, methods=['post'], permission_classes=[IsAdminUser])
    def bulk_create(self, request):
        """
        Bulk enroll multiple students.
        
        Expected format:
        {
            "enrollments": [
                {
                    "student_id": 1,
                    "class_id": 1,
                    "section_id": 1,
                    "academic_year": "2024-2025"
                },
                ...
            ]
        }
        """
        # For now, manual enrollment loop
        enrollments = []
        for enrollment_data in request.data.get('enrollments', []):
            enrollment = Enrollment.objects.create(**enrollment_data)
            enrollments.append(enrollment)
        
        return Response({
            'status': 'success',
            'created': len(enrollments),
            'message': f'Successfully enrolled {len(enrollments)} students'
        }, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=['get'])
    def subjects(self, request, pk=None):
        """Get subjects for enrolled student in academic year."""
        enrollment = self.get_object()
        subjects = enrollment.class_obj.subjects.all()
        
        from apps.subjects.serializers import SubjectSerializer
        serializer = SubjectSerializer(subjects, many=True)
        return Response({
            'enrollment_id': enrollment.id,
            'student': str(enrollment.student),
            'class': str(enrollment.class_obj),
            'academic_year': enrollment.academic_year,
            'count': subjects.count(),
            'results': serializer.data
        })
