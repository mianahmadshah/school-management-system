"""
Views for the assignments app.
"""
from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend

from .models import Assignment, Submission
from .serializers import AssignmentSerializer, SubmissionSerializer
from apps.accounts.permissions import IsAdminUser, IsAdminOrTeacher


class AssignmentViewSet(viewsets.ModelViewSet):
    """CRUD ViewSet for Assignments."""
    serializer_class = AssignmentSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'subject__name', 'school_class__name']
    filterset_fields = ['school_class', 'section', 'subject', 'teacher', 'is_active']
    ordering_fields = ['due_date', 'created_at']
    ordering = ['-due_date']

    def get_queryset(self):
        qs = Assignment.objects.select_related(
            'school_class', 'section', 'subject', 'teacher__user'
        ).filter(is_active=True)
        user = self.request.user

        if user.is_admin:
            return Assignment.objects.select_related(
                'school_class', 'section', 'subject', 'teacher__user'
            ).all()

        if user.is_teacher:
            teacher = getattr(user, 'teacher_profile', None)
            if teacher:
                return qs.filter(teacher=teacher)

        if user.is_student:
            student = getattr(user, 'student_profile', None)
            if student and student.current_class and student.section:
                return qs.filter(
                    school_class=student.current_class,
                    section=student.section
                )

        return qs.none()

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAdminOrTeacher()]
        return [IsAuthenticated()]

    def perform_create(self, serializer):
        # If the user is a teacher, assign them as the teacher automatically
        user = self.request.user
        if user.is_teacher and hasattr(user, 'teacher_profile'):
            serializer.save(teacher=user.teacher_profile)
        else:
            serializer.save()


class SubmissionViewSet(viewsets.ModelViewSet):
    """CRUD ViewSet for Submissions."""
    serializer_class = SubmissionSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['student__user__first_name', 'assignment__title']
    filterset_fields = ['assignment', 'student', 'status']
    ordering_fields = ['submission_date']
    ordering = ['-submission_date']

    def get_queryset(self):
        qs = Submission.objects.select_related(
            'assignment', 'student__user'
        )
        user = self.request.user

        if user.is_admin:
            return qs.all()

        if user.is_teacher:
            teacher = getattr(user, 'teacher_profile', None)
            if teacher:
                return qs.filter(assignment__teacher=teacher)

        if user.is_student:
            student = getattr(user, 'student_profile', None)
            if student:
                return qs.filter(student=student)

        return qs.none()

    def get_permissions(self):
        # Students submit; teachers grade; admins do anything
        return [IsAuthenticated()]

    def perform_create(self, serializer):
        user = self.request.user
        if user.is_student and hasattr(user, 'student_profile'):
            serializer.save(student=user.student_profile)
        else:
            serializer.save()

    @action(detail=True, methods=['patch'], permission_classes=[IsAdminOrTeacher])
    def grade(self, request, pk=None):
        """
        PATCH /api/v1/assignments/submissions/{id}/grade/
        Teacher grades a submission.
        """
        submission = self.get_object()
        obtained_marks = request.data.get('obtained_marks')
        teacher_feedback = request.data.get('teacher_feedback', '')

        if obtained_marks is None:
            return Response(
                {"error": "obtained_marks is required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        if float(obtained_marks) > float(submission.assignment.max_marks):
            return Response(
                {"error": f"Marks cannot exceed max marks ({submission.assignment.max_marks})."},
                status=status.HTTP_400_BAD_REQUEST
            )

        submission.obtained_marks = obtained_marks
        submission.teacher_feedback = teacher_feedback
        submission.status = Submission.Status.GRADED
        submission.save()

        return Response(
            {"message": "Submission graded successfully.", "data": SubmissionSerializer(submission).data}
        )
