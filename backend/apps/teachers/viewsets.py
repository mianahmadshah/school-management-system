"""
ViewSets for Teacher management.
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

from apps.teachers.models import Teacher
from apps.teachers.serializers import TeacherListSerializer, TeacherDetailSerializer
from apps.accounts.permissions import IsAdminUser, IsTeacherUser, IsAdminOrTeacher
from api.v1.pagination import StandardResultsSetPagination


class TeacherViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Teacher management.
    
    Endpoints:
    - GET    /api/v1/teachers/         - List teachers
    - POST   /api/v1/teachers/         - Create teacher (admin only)
    - GET    /api/v1/teachers/{id}/    - Get teacher details
    - PUT    /api/v1/teachers/{id}/    - Update teacher (admin only)
    - DELETE /api/v1/teachers/{id}/    - Delete teacher (admin only)
    """
    queryset = Teacher.objects.select_related('user').all()
    serializer_class = TeacherListSerializer
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return TeacherDetailSerializer
        return TeacherListSerializer
    pagination_class = StandardResultsSetPagination
    
    filter_backends = [
        DjangoFilterBackend,
        SearchFilter,
        OrderingFilter
    ]
    filterset_fields = ['employment_status', 'employment_type', 'qualification']
    search_fields = [
        'user__first_name', 'user__last_name', 'employee_id',
        'user__email', 'specialization'
    ]
    ordering_fields = ['employee_id', 'user__first_name', 'date_of_joining']
    ordering = ['employee_id']
    
    def get_permissions(self):
        """
        Override permissions per action.
        - list/retrieve: Authenticated users
        - create/update/destroy: Admin only
        """
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes = [IsAdminUser]
        else:
            permission_classes = [IsAuthenticated]
        
        return [permission() for permission in permission_classes]
    
    @action(detail=True, methods=['get'])
    def subjects(self, request, pk=None):
        """Get subjects taught by this teacher."""
        teacher = self.get_object()
        subjects = teacher.subjects.all()
        
        from apps.subjects.serializers import SubjectSerializer
        serializer = SubjectSerializer(subjects, many=True)
        return Response({
            'count': subjects.count(),
            'results': serializer.data
        })
    
    @action(detail=True, methods=['get'])
    def classes(self, request, pk=None):
        """Get classes assigned to this teacher."""
        teacher = self.get_object()
        classes = teacher.class_assignments.all()
        
        from apps.classes.serializers import ClassSerializer
        serializer = ClassSerializer(classes, many=True)
        return Response({
            'count': classes.count(),
            'results': serializer.data
        })
    
    @action(detail=True, methods=['get'])
    def timetable(self, request, pk=None):
        """Get timetable for this teacher."""
        teacher = self.get_object()
        timetable_entries = teacher.timetable_entries.all()
        
        from apps.timetable.serializers import TimetableSerializer
        serializer = TimetableSerializer(timetable_entries, many=True)
        return Response({
            'count': timetable_entries.count(),
            'results': serializer.data
        })
