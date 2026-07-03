"""
Views for the subjects app.
Handles Subject and Enrollment models.
"""
from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Count

from .models import Subject, Enrollment
from .serializers import SubjectSerializer, EnrollmentSerializer
from apps.accounts.permissions import IsAdminUser, IsAdminOrTeacher


class SubjectViewSet(viewsets.ModelViewSet):
    """
    CRUD ViewSet for Subjects.
    """
    queryset = Subject.objects.select_related('school_class', 'teacher__user').all()
    serializer_class = SubjectSerializer

    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'code', 'school_class__name']
    filterset_fields = ['school_class', 'subject_type', 'is_active', 'teacher']
    ordering_fields = ['name', 'code', 'school_class']
    ordering = ['school_class', 'name']

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAdminUser()]
        return [IsAdminOrTeacher()]

    @action(detail=False, methods=['get'], permission_classes=[IsAdminUser])
    def stats(self, request):
        total = Subject.objects.count()
        active = Subject.objects.filter(is_active=True).count()
        return Response({
            'total_subjects': total,
            'active_subjects': active,
        })


class EnrollmentViewSet(viewsets.ModelViewSet):
    """
    CRUD ViewSet for Enrollments.
    """
    queryset = Enrollment.objects.select_related(
        'student__user', 'school_class', 'section'
    ).all()
    serializer_class = EnrollmentSerializer

    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['student__user__first_name', 'student__user__last_name', 'student__admission_number', 'roll_number']
    filterset_fields = ['school_class', 'section', 'academic_year', 'is_active']
    ordering_fields = ['academic_year', 'school_class', 'student__user__first_name']
    ordering = ['-academic_year', 'school_class', 'section']

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAdminUser()]
        return [IsAdminOrTeacher()]

    def create(self, request, *args, **kwargs):
        # When creating an enrollment, also optionally update the student's current_class and section
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        enrollment = serializer.save()
        
        # Update student current class and section if active
        if enrollment.is_active:
            student = enrollment.student
            student.current_class = enrollment.school_class
            student.section = enrollment.section
            student.roll_number = enrollment.roll_number or student.roll_number
            student.save()
            
        return Response(
            {
                'message': f'Student enrolled successfully in {enrollment.school_class.name} {enrollment.section.name}.',
                'data': EnrollmentSerializer(enrollment).data
            },
            status=status.HTTP_201_CREATED
        )
