"""
ViewSets for Assignment and Submission management.
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

from apps.assignments.models import Assignment, Submission
from apps.assignments.serializers import AssignmentSerializer, SubmissionSerializer
from apps.accounts.permissions import IsAdminUser, IsAdminOrTeacher, IsStudentUser
from api.v1.pagination import StandardResultsSetPagination


class AssignmentViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Assignment management.
    
    Endpoints:
    - GET    /api/v1/assignments/              - List assignments
    - POST   /api/v1/assignments/              - Create assignment (teacher/admin)
    - GET    /api/v1/assignments/{id}/         - Get assignment details
    - PUT    /api/v1/assignments/{id}/         - Update assignment (owner/admin)
    - DELETE /api/v1/assignments/{id}/         - Delete assignment (owner/admin)
    - GET    /api/v1/assignments/{id}/submissions/ - Get submissions
    """
    queryset = Assignment.objects.select_related(
        'class_obj', 'section', 'subject', 'created_by'
    ).all()
    serializer_class = AssignmentSerializer
    pagination_class = StandardResultsSetPagination
    
    filter_backends = [
        DjangoFilterBackend,
        SearchFilter,
        OrderingFilter
    ]
    filterset_fields = ['class_obj', 'section', 'subject', 'status']
    search_fields = ['title', 'description']
    ordering_fields = ['due_date', 'created_at']
    ordering = ['-due_date']
    
    def get_permissions(self):
        """Override permissions per action."""
        if self.action in ['create']:
            permission_classes = [IsAdminOrTeacher]
        elif self.action in ['update', 'partial_update', 'destroy']:
            permission_classes = [IsAdminUser]
        else:
            permission_classes = [IsAuthenticated]
        
        return [permission() for permission in permission_classes]
    
    def perform_create(self, serializer):
        """Set created_by to the current user."""
        serializer.save(created_by=self.request.user)
    
    @action(detail=True, methods=['get'])
    def submissions(self, request, pk=None):
        """Get all submissions for an assignment."""
        assignment = self.get_object()
        submissions = assignment.submissions.all()
        
        serializer = SubmissionSerializer(submissions, many=True)
        return Response({
            'assignment': str(assignment),
            'count': submissions.count(),
            'results': serializer.data
        })
    
    @action(detail=False, methods=['get'])
    def pending(self, request):
        """Get pending assignments (due date not yet passed)."""
        from datetime import datetime
        pending = Assignment.objects.filter(
            due_date__gte=datetime.now().date()
        )
        
        serializer = AssignmentSerializer(pending, many=True)
        return Response({
            'count': pending.count(),
            'results': serializer.data
        })


class SubmissionViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Submission management.
    
    Endpoints:
    - GET    /api/v1/submissions/              - List submissions
    - POST   /api/v1/submissions/              - Submit assignment (student)
    - GET    /api/v1/submissions/{id}/         - Get submission details
    - PUT    /api/v1/submissions/{id}/         - Update submission (student/admin)
    - POST   /api/v1/submissions/{id}/grade/   - Grade submission (teacher/admin)
    - GET    /api/v1/submissions/student/{id}/ - Get student submissions
    """
    queryset = Submission.objects.select_related(
        'assignment', 'student', 'graded_by'
    ).all()
    serializer_class = SubmissionSerializer
    pagination_class = StandardResultsSetPagination
    
    filter_backends = [
        DjangoFilterBackend,
        SearchFilter,
        OrderingFilter
    ]
    filterset_fields = ['assignment', 'status']
    search_fields = ['student__user__first_name', 'student__user__last_name']
    ordering_fields = ['submission_date', 'graded_at']
    ordering = ['-submission_date']
    
    def get_permissions(self):
        """Override permissions per action."""
        if self.action in ['create', 'update', 'partial_update']:
            permission_classes = [IsAuthenticated]
        elif self.action in ['grade']:
            permission_classes = [IsAdminOrTeacher]
        else:
            permission_classes = [IsAuthenticated]
        
        return [permission() for permission in permission_classes]
    
    def perform_create(self, serializer):
        """Set student to the current user."""
        serializer.save(student=self.request.user.student_profile)
    
    @action(detail=True, methods=['post'], permission_classes=[IsAdminOrTeacher])
    def grade(self, request, pk=None):
        """
        Grade a submission.
        
        Expected body:
        {
            "marks_obtained": 85,
            "feedback": "Good work!"
        }
        """
        submission = self.get_object()
        
        marks = request.data.get('marks_obtained')
        feedback = request.data.get('feedback', '')
        
        if marks is None:
            return Response(
                {'error': 'marks_obtained required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        submission.marks_obtained = marks
        submission.feedback = feedback
        submission.status = 'GRADED'
        submission.graded_by = request.user.teacher_profile
        submission.graded_at = datetime.now()
        submission.save()
        
        serializer = SubmissionSerializer(submission)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['get'])
    def by_student(self, request):
        """Get submissions for a specific student."""
        student_id = request.query_params.get('student_id')
        if not student_id:
            return Response(
                {'error': 'student_id parameter required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        submissions = Submission.objects.filter(student_id=student_id)
        serializer = SubmissionSerializer(submissions, many=True)
        return Response({
            'student_id': student_id,
            'count': submissions.count(),
            'results': serializer.data
        })
    
    @action(detail=False, methods=['get'])
    def pending_grading(self, request):
        """Get submissions pending grading (teacher/admin only)."""
        if request.user.role not in ['TEACHER', 'ADMIN']:
            return Response(
                {'error': 'Only teachers and admins can view this'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        pending = Submission.objects.filter(status='SUBMITTED')
        serializer = SubmissionSerializer(pending, many=True)
        return Response({
            'count': pending.count(),
            'results': serializer.data
        })


from datetime import datetime
