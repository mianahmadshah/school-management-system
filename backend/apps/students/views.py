"""
Views for the students app.

Uses ModelViewSet for full CRUD with search, filter, and ordering built in.
Custom actions (@action) add extra endpoints like student statistics.
"""
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
try:
    try:
        from django_filters.rest_framework import DjangoFilterBackend
    except ImportError:  # pragma: no cover - optional dependency
        DjangoFilterBackend = None
except ImportError:  # pragma: no cover - optional dependency
    DjangoFilterBackend = None

from .models import Student
from .serializers import (
    StudentListSerializer,
    StudentDetailSerializer,
    StudentCreateSerializer,
    StudentUpdateSerializer,
)
from apps.accounts.permissions import IsAdminUser, IsAdminOrTeacher


class StudentViewSet(viewsets.ModelViewSet):
    """
    Complete CRUD ViewSet for Student management.

    Endpoints generated automatically by the router:
      GET    /api/v1/students/            → List all students
      POST   /api/v1/students/            → Create a student
      GET    /api/v1/students/{id}/       → Get student detail
      PUT    /api/v1/students/{id}/       → Full update
      PATCH  /api/v1/students/{id}/       → Partial update
      DELETE /api/v1/students/{id}/       → Delete student

    Custom Endpoints:
      GET    /api/v1/students/stats/      → Summary statistics
      GET    /api/v1/students/{id}/profile/ → Full profile
    """
    queryset = Student.objects.select_related('user', 'current_class', 'section').all()

    # ─── FILTERING & SEARCHING ─────────────────────────────
    # ?search=john  searches name and admission number
    filter_backends = [
        backend for backend in [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
        if backend is not None
    ]
    search_fields = [
        'user__first_name',
        'user__last_name',
        'user__email',
        'admission_number',
        'roll_number',
        'father_name',
    ]
    # ?status=ACTIVE&gender=MALE&current_class=Grade1
    filterset_fields = ['status', 'gender', 'current_class', 'section', 'blood_group']
    # ?ordering=admission_number or ?ordering=-created_at
    ordering_fields = ['admission_number', 'created_at', 'admission_date']
    ordering = ['admission_number']  # Default sort

    # ─── PERMISSIONS ───────────────────────────────────────
    def get_permissions(self):
        """
        Apply different permissions for different actions.
        - List/Retrieve: Admin or Teacher can view
        - Create/Update/Delete: Admin only
        """
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes = [IsAdminUser]
        else:
            permission_classes = [IsAdminOrTeacher]
        return [permission() for permission in permission_classes]

    # ─── SERIALIZER SELECTION ──────────────────────────────
    def get_serializer_class(self):
        """Use different serializers for different actions."""
        if self.action == 'create':
            return StudentCreateSerializer
        if self.action in ['update', 'partial_update']:
            return StudentUpdateSerializer
        if self.action == 'retrieve':
            return StudentDetailSerializer
        return StudentListSerializer  # For list and custom actions

    # ─── CUSTOM CREATE ─────────────────────────────────────
    def create(self, request, *args, **kwargs):
        """
        Override create to handle the StudentCreateSerializer
        which returns a Student object (not a dict).
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        student = serializer.save()

        # Return the full student detail after creation
        detail_serializer = StudentDetailSerializer(
            student, context={'request': request}
        )
        return Response(
            {
                'message': f'Student {student.full_name} created successfully.',
                'data': detail_serializer.data
            },
            status=status.HTTP_201_CREATED
        )

    # ─── CUSTOM ACTIONS ────────────────────────────────────
    @action(detail=False, methods=['get'], permission_classes=[IsAdminOrTeacher])
    def stats(self, request):
        """
        GET /api/v1/students/stats/
        Returns a summary of student statistics for the dashboard.
        """
        total = Student.objects.count()
        active = Student.objects.filter(status='ACTIVE').count()
        inactive = Student.objects.filter(status='INACTIVE').count()
        graduated = Student.objects.filter(status='GRADUATED').count()

        # Gender breakdown
        male = Student.objects.filter(gender='MALE').count()
        female = Student.objects.filter(gender='FEMALE').count()

        return Response({
            'total_students': total,
            'active': active,
            'inactive': inactive,
            'graduated': graduated,
            'gender_breakdown': {
                'male': male,
                'female': female,
            }
        })

    @action(detail=True, methods=['get'], permission_classes=[IsAdminOrTeacher])
    def profile(self, request, pk=None):
        """
        GET /api/v1/students/{id}/profile/
        Returns the complete profile of a single student.
        """
        student = self.get_object()
        serializer = StudentDetailSerializer(student, context={'request': request})
        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        """
        Override delete to also delete the associated user account.
        We also return a meaningful message instead of empty 204.
        """
        student = self.get_object()
        student_name = student.full_name
        user = student.user

        # Deleting user will cascade delete student via OneToOne
        user.delete()

        return Response(
            {'message': f'Student {student_name} and their account have been deleted.'},
            status=status.HTTP_200_OK
        )
