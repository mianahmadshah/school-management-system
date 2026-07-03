"""
ViewSets for Timetable management.
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

from apps.timetable.models import Period, Timetable
from apps.timetable.serializers import PeriodSerializer, TimetableSerializer
from apps.accounts.permissions import IsAdminUser
from api.v1.pagination import StandardResultsSetPagination


class PeriodViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Period management (class periods/time slots).
    
    Endpoints:
    - GET    /api/v1/periods/         - List periods
    - POST   /api/v1/periods/         - Create period (admin only)
    - GET    /api/v1/periods/{id}/    - Get period details
    - PUT    /api/v1/periods/{id}/    - Update period (admin only)
    - DELETE /api/v1/periods/{id}/    - Delete period (admin only)
    """
    queryset = Period.objects.all()
    serializer_class = PeriodSerializer
    pagination_class = StandardResultsSetPagination
    
    filter_backends = [OrderingFilter]
    ordering_fields = ['order', 'start_time']
    ordering = ['order']
    
    def get_permissions(self):
        """Override permissions per action."""
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes = [IsAdminUser]
        else:
            permission_classes = [IsAuthenticated]
        
        return [permission() for permission in permission_classes]


class TimetableViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Timetable management (class schedule).
    
    Endpoints:
    - GET    /api/v1/timetable/              - List timetable entries
    - POST   /api/v1/timetable/              - Create timetable entry (admin only)
    - GET    /api/v1/timetable/{id}/         - Get timetable entry details
    - PUT    /api/v1/timetable/{id}/         - Update timetable entry (admin only)
    - DELETE /api/v1/timetable/{id}/         - Delete timetable entry (admin only)
    - GET    /api/v1/timetable/class/{id}/   - Get class schedule
    - GET    /api/v1/timetable/section/{id}/ - Get section schedule
    """
    queryset = Timetable.objects.select_related(
        'class_obj', 'section', 'subject', 'teacher', 'period'
    ).all()
    serializer_class = TimetableSerializer
    pagination_class = StandardResultsSetPagination
    
    filter_backends = [
        DjangoFilterBackend,
        OrderingFilter
    ]
    filterset_fields = ['class_obj', 'section', 'day_of_week', 'subject', 'teacher']
    ordering_fields = ['day_of_week', 'period__order']
    ordering = ['day_of_week', 'period__order']
    
    def get_permissions(self):
        """Override permissions per action."""
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes = [IsAdminUser]
        else:
            permission_classes = [IsAuthenticated]
        
        return [permission() for permission in permission_classes]
    
    @action(detail=False, methods=['get'])
    def by_class(self, request):
        """Get timetable for a specific class."""
        class_id = request.query_params.get('class_id')
        if not class_id:
            return Response(
                {'error': 'class_id parameter required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        day_filter = request.query_params.get('day')  # Optional: filter by day
        
        timetable = Timetable.objects.filter(class_obj_id=class_id)
        if day_filter:
            timetable = timetable.filter(day_of_week=day_filter)
        
        timetable = timetable.order_by('day_of_week', 'period__order')
        serializer = TimetableSerializer(timetable, many=True)
        
        return Response({
            'class_id': class_id,
            'day': day_filter or 'all',
            'count': timetable.count(),
            'results': serializer.data
        })
    
    @action(detail=False, methods=['get'])
    def by_section(self, request):
        """Get timetable for a specific section."""
        section_id = request.query_params.get('section_id')
        if not section_id:
            return Response(
                {'error': 'section_id parameter required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        day_filter = request.query_params.get('day')  # Optional: filter by day
        
        timetable = Timetable.objects.filter(section_id=section_id)
        if day_filter:
            timetable = timetable.filter(day_of_week=day_filter)
        
        timetable = timetable.order_by('day_of_week', 'period__order')
        serializer = TimetableSerializer(timetable, many=True)
        
        return Response({
            'section_id': section_id,
            'day': day_filter or 'all',
            'count': timetable.count(),
            'results': serializer.data
        })
    
    @action(detail=False, methods=['get'])
    def by_teacher(self, request):
        """Get timetable for a specific teacher."""
        teacher_id = request.query_params.get('teacher_id')
        if not teacher_id:
            return Response(
                {'error': 'teacher_id parameter required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        timetable = Timetable.objects.filter(teacher_id=teacher_id).order_by('day_of_week', 'period__order')
        serializer = TimetableSerializer(timetable, many=True)
        
        return Response({
            'teacher_id': teacher_id,
            'count': timetable.count(),
            'results': serializer.data
        })
    
    @action(detail=False, methods=['get'])
    def by_subject(self, request):
        """Get timetable for a specific subject."""
        subject_id = request.query_params.get('subject_id')
        if not subject_id:
            return Response(
                {'error': 'subject_id parameter required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        timetable = Timetable.objects.filter(subject_id=subject_id).order_by('day_of_week', 'period__order')
        serializer = TimetableSerializer(timetable, many=True)
        
        return Response({
            'subject_id': subject_id,
            'count': timetable.count(),
            'results': serializer.data
        })
