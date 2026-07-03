"""
Views for the teachers app.
Mirrors the student ViewSet pattern with teacher-specific logic.
"""
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend

from .models import Teacher
from .serializers import (
    TeacherListSerializer,
    TeacherDetailSerializer,
    TeacherCreateSerializer,
    TeacherUpdateSerializer,
)
from apps.accounts.permissions import IsAdminUser, IsAdminOrTeacher


class TeacherViewSet(viewsets.ModelViewSet):
    """
    Complete CRUD ViewSet for Teacher management.

    Endpoints:
      GET    /api/v1/teachers/            → List all teachers
      POST   /api/v1/teachers/            → Create a teacher
      GET    /api/v1/teachers/{id}/       → Teacher detail
      PUT    /api/v1/teachers/{id}/       → Full update
      PATCH  /api/v1/teachers/{id}/       → Partial update
      DELETE /api/v1/teachers/{id}/       → Delete teacher

    Custom Endpoints:
      GET    /api/v1/teachers/stats/      → Summary stats
      GET    /api/v1/teachers/{id}/profile/ → Full profile
    """
    queryset = Teacher.objects.select_related('user').all()

    # ─── FILTERING & SEARCH ────────────────────────────────
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = [
        'user__first_name', 'user__last_name',
        'user__email', 'employee_id', 'department', 'specialization'
    ]
    filterset_fields = ['status', 'gender', 'department', 'employment_type']
    ordering_fields = ['employee_id', 'joining_date', 'experience_years']
    ordering = ['employee_id']

    # ─── PERMISSIONS ───────────────────────────────────────
    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes = [IsAdminUser]
        else:
            permission_classes = [IsAdminOrTeacher]
        return [permission() for permission in permission_classes]

    # ─── SERIALIZER SELECTION ──────────────────────────────
    def get_serializer_class(self):
        if self.action == 'create':
            return TeacherCreateSerializer
        if self.action in ['update', 'partial_update']:
            return TeacherUpdateSerializer
        if self.action == 'retrieve':
            return TeacherDetailSerializer
        return TeacherListSerializer

    # ─── CUSTOM CREATE ─────────────────────────────────────
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        teacher = serializer.save()

        detail_serializer = TeacherDetailSerializer(
            teacher, context={'request': request}
        )
        return Response(
            {
                'message': f'Teacher {teacher.full_name} created successfully.',
                'data': detail_serializer.data
            },
            status=status.HTTP_201_CREATED
        )

    # ─── CUSTOM ACTIONS ────────────────────────────────────
    @action(detail=False, methods=['get'], permission_classes=[IsAdminUser])
    def stats(self, request):
        """
        GET /api/v1/teachers/stats/
        Teacher summary statistics for the admin dashboard.
        """
        total = Teacher.objects.count()
        active = Teacher.objects.filter(status='ACTIVE').count()
        on_leave = Teacher.objects.filter(status='ON_LEAVE').count()
        inactive = Teacher.objects.filter(status='INACTIVE').count()

        # By employment type
        full_time = Teacher.objects.filter(employment_type='FULL_TIME').count()
        part_time = Teacher.objects.filter(employment_type='PART_TIME').count()

        return Response({
            'total_teachers': total,
            'active': active,
            'on_leave': on_leave,
            'inactive': inactive,
            'employment_breakdown': {
                'full_time': full_time,
                'part_time': part_time,
            }
        })

    @action(detail=True, methods=['get'], permission_classes=[IsAdminOrTeacher])
    def profile(self, request, pk=None):
        """
        GET /api/v1/teachers/{id}/profile/
        Full profile of a single teacher.
        """
        teacher = self.get_object()
        serializer = TeacherDetailSerializer(teacher, context={'request': request})
        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        """Delete teacher and their user account."""
        teacher = self.get_object()
        teacher_name = teacher.full_name
        teacher.user.delete()  # Cascade deletes teacher profile
        return Response(
            {'message': f'Teacher {teacher_name} and their account have been deleted.'},
            status=status.HTTP_200_OK
        )
