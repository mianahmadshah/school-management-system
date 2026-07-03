"""
ViewSets for Class and Section management.
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

from apps.classes.models import Class, Section
from apps.classes.serializers import ClassListSerializer, ClassSerializer, SectionListSerializer, SectionSerializer
from apps.accounts.permissions import IsAdminUser
from api.v1.pagination import StandardResultsSetPagination


class ClassViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Class management.
    
    Endpoints:
    - GET    /api/v1/classes/              - List classes
    - POST   /api/v1/classes/              - Create class (admin only)
    - GET    /api/v1/classes/{id}/         - Get class details
    - PUT    /api/v1/classes/{id}/         - Update class (admin only)
    - DELETE /api/v1/classes/{id}/         - Delete class (admin only)
    - GET    /api/v1/classes/{id}/sections/ - Get sections in class
    """
    queryset = Class.objects.select_related('class_teacher').all()
    serializer_class = ClassListSerializer
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return ClassSerializer
        return ClassListSerializer
    pagination_class = StandardResultsSetPagination
    
    filter_backends = [
        DjangoFilterBackend,
        SearchFilter,
        OrderingFilter
    ]
    filterset_fields = ['numeric_grade']
    search_fields = ['name', 'numeric_grade']
    ordering_fields = ['numeric_grade', 'name']
    ordering = ['numeric_grade']
    
    def get_permissions(self):
        """Override permissions per action."""
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes = [IsAdminUser]
        else:
            permission_classes = [IsAuthenticated]
        
        return [permission() for permission in permission_classes]
    
    @action(detail=True, methods=['get'])
    def sections(self, request, pk=None):
        """Get all sections in this class."""
        class_obj = self.get_object()
        sections = class_obj.sections.all()
        
        serializer = SectionSerializer(sections, many=True)
        return Response({
            'class_id': class_obj.id,
            'class_name': str(class_obj),
            'count': sections.count(),
            'results': serializer.data
        })
    
    @action(detail=True, methods=['get'])
    def students(self, request, pk=None):
        """Get all students in this class."""
        class_obj = self.get_object()
        students = class_obj.students.all()
        
        from apps.students.serializers import StudentSerializer
        serializer = StudentSerializer(students, many=True)
        return Response({
            'count': students.count(),
            'results': serializer.data
        })


class SectionViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Section management.
    
    Endpoints:
    - GET    /api/v1/sections/              - List sections
    - POST   /api/v1/sections/              - Create section (admin only)
    - GET    /api/v1/sections/{id}/         - Get section details
    - PUT    /api/v1/sections/{id}/         - Update section (admin only)
    - DELETE /api/v1/sections/{id}/         - Delete section (admin only)
    - GET    /api/v1/sections/{id}/students/ - Get enrolled students
    """
    queryset = Section.objects.select_related('class_obj').all()
    serializer_class = SectionListSerializer
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return SectionSerializer
        return SectionListSerializer
    pagination_class = StandardResultsSetPagination
    
    filter_backends = [
        DjangoFilterBackend,
        SearchFilter,
        OrderingFilter
    ]
    filterset_fields = ['class_obj', 'is_full']
    search_fields = ['name', 'class_obj__name']
    ordering_fields = ['name', 'current_strength']
    ordering = ['class_obj__numeric_grade', 'name']
    
    def get_permissions(self):
        """Override permissions per action."""
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes = [IsAdminUser]
        else:
            permission_classes = [IsAuthenticated]
        
        return [permission() for permission in permission_classes]
    
    @action(detail=True, methods=['get'])
    def students(self, request, pk=None):
        """Get all students in this section."""
        section = self.get_object()
        students = section.students.all()
        
        from apps.students.serializers import StudentSerializer
        serializer = StudentSerializer(students, many=True)
        return Response({
            'section': str(section),
            'class': str(section.class_obj),
            'count': students.count(),
            'current_strength': section.current_strength,
            'available_seats': section.available_seats,
            'results': serializer.data
        })
    
    @action(detail=True, methods=['get'])
    def timetable(self, request, pk=None):
        """Get timetable for this section."""
        section = self.get_object()
        timetable = section.timetable_entries.all()
        
        from apps.timetable.serializers import TimetableSerializer
        serializer = TimetableSerializer(timetable, many=True)
        return Response({
            'section': str(section),
            'count': timetable.count(),
            'results': serializer.data
        })
