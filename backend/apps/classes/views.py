"""
Views for the classes app.
Provides full CRUD for both Class and Section models.
"""
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Count

from .models import Class, Section
from .serializers import (
    ClassSerializer,
    ClassListSerializer,
    ClassCreateUpdateSerializer,
    SectionSerializer,
)
from apps.accounts.permissions import IsAdminUser, IsAdminOrTeacher


class ClassViewSet(viewsets.ModelViewSet):
    """
    CRUD ViewSet for Class management.

    GET    /api/v1/classes/             → List all classes
    POST   /api/v1/classes/             → Create a class
    GET    /api/v1/classes/{id}/        → Class detail with sections
    PUT    /api/v1/classes/{id}/        → Update class
    DELETE /api/v1/classes/{id}/        → Delete class

    Custom:
    GET    /api/v1/classes/active/      → Only active classes
    GET    /api/v1/classes/{id}/sections/ → All sections of a class
    """
    # Annotate queryset with counts to avoid extra DB queries
    queryset = Class.objects.annotate(
        total_sections_count=Count('sections', distinct=True),
        total_students_count=Count('sections__enrollments', distinct=True),
    ).prefetch_related('sections').select_related('class_teacher__user')

    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description']
    filterset_fields = ['is_active']
    ordering_fields = ['numeric_grade', 'name', 'created_at']
    ordering = ['numeric_grade', 'name']

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAdminUser()]
        return [IsAdminOrTeacher()]

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return ClassSerializer          # With nested sections
        if self.action in ['create', 'update', 'partial_update']:
            return ClassCreateUpdateSerializer
        return ClassListSerializer          # For list views

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        school_class = serializer.save()
        return Response(
            {
                'message': f'Class "{school_class.name}" created successfully.',
                'data': ClassSerializer(school_class).data
            },
            status=status.HTTP_201_CREATED
        )

    @action(detail=False, methods=['get'], permission_classes=[IsAdminOrTeacher])
    def active(self, request):
        """
        GET /api/v1/classes/active/
        Returns only active classes — used for dropdowns in forms.
        """
        classes = self.queryset.filter(is_active=True)
        serializer = ClassListSerializer(classes, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'], permission_classes=[IsAdminOrTeacher])
    def sections(self, request, pk=None):
        """
        GET /api/v1/classes/{id}/sections/
        Returns all sections for a specific class.
        Useful for cascading dropdowns: choose class → load its sections.
        """
        school_class = self.get_object()
        sections = school_class.sections.filter(is_active=True).select_related(
            'section_teacher__user'
        )
        serializer = SectionSerializer(sections, many=True)
        return Response({
            'class': school_class.name,
            'total_sections': sections.count(),
            'sections': serializer.data
        })

    @action(detail=False, methods=['get'], permission_classes=[IsAdminUser])
    def stats(self, request):
        """
        GET /api/v1/classes/stats/
        Summary statistics for the admin dashboard.
        """
        total = Class.objects.count()
        active = Class.objects.filter(is_active=True).count()
        total_sections = Section.objects.count()
        active_sections = Section.objects.filter(is_active=True).count()

        return Response({
            'total_classes': total,
            'active_classes': active,
            'total_sections': total_sections,
            'active_sections': active_sections,
        })


class SectionViewSet(viewsets.ModelViewSet):
    """
    CRUD ViewSet for Section management.

    GET    /api/v1/classes/sections/           → List all sections
    POST   /api/v1/classes/sections/           → Create a section
    GET    /api/v1/classes/sections/{id}/      → Section detail
    PUT    /api/v1/classes/sections/{id}/      → Update
    DELETE /api/v1/classes/sections/{id}/      → Delete

    Filter:  ?school_class=1
    Search:  ?search=A
    """
    queryset = Section.objects.select_related(
        'school_class', 'section_teacher__user'
    ).all()

    serializer_class = SectionSerializer

    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'school_class__name', 'room_number']
    filterset_fields = ['school_class', 'is_active']
    ordering_fields = ['school_class', 'name']
    ordering = ['school_class', 'name']

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAdminUser()]
        return [IsAdminOrTeacher()]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        section = serializer.save()
        return Response(
            {
                'message': f'Section "{section}" created successfully.',
                'data': SectionSerializer(section).data
            },
            status=status.HTTP_201_CREATED
        )
