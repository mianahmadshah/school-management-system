"""
Views for the examinations app.
"""
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Sum

from .models import Exam, Marks, Result
from .serializers import (
    ExamSerializer, MarksSerializer, ResultSerializer, BulkMarksEntrySerializer
)
from apps.accounts.permissions import IsAdminUser, IsAdminOrTeacher
from apps.students.models import Student


class ExamViewSet(viewsets.ModelViewSet):
    """CRUD ViewSet for Exams."""
    queryset = Exam.objects.all()
    serializer_class = ExamSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description']
    filterset_fields = ['exam_type', 'is_active']
    ordering_fields = ['start_date', 'name']
    ordering = ['-start_date']

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAdminUser()]
        return [IsAuthenticated()]


class MarksViewSet(viewsets.ModelViewSet):
    """CRUD ViewSet for Marks."""
    serializer_class = MarksSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['student__user__first_name', 'student__user__last_name', 'student__admission_number', 'subject__name']
    filterset_fields = ['exam', 'student', 'subject', 'grade', 'is_passed']
    ordering_fields = ['student__user__first_name', 'subject__name', 'obtained_marks']
    ordering = ['exam', 'student', 'subject']

    def get_queryset(self):
        qs = Marks.objects.select_related('exam', 'student__user', 'subject')
        user = self.request.user
        if user.is_student:
            return qs.filter(student__user=user)
        return qs.all()

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy', 'bulk_entry']:
            return [IsAdminOrTeacher()]
        return [IsAuthenticated()]

    @action(detail=False, methods=['post'], permission_classes=[IsAdminOrTeacher])
    def bulk_entry(self, request):
        """
        POST /api/v1/examinations/marks/bulk_entry/
        Bulk upload marks for an exam and subject.
        """
        serializer = BulkMarksEntrySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        result = serializer.save()
        return Response({
            "message": "Marks entered successfully.",
            "details": result
        }, status=status.HTTP_200_OK)


class ResultViewSet(viewsets.ModelViewSet):
    """CRUD ViewSet for Results."""
    serializer_class = ResultSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['student__user__first_name', 'student__user__last_name', 'student__admission_number']
    filterset_fields = ['exam', 'student', 'passed', 'overall_grade']
    ordering_fields = ['percentage', 'student__user__first_name']
    ordering = ['exam', '-percentage']

    def get_queryset(self):
        qs = Result.objects.select_related('exam', 'student__user', 'student__current_class')
        user = self.request.user
        if user.is_student:
            return qs.filter(student__user=user)
        return qs.all()

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy', 'generate']:
            return [IsAdminUser()]
        return [IsAuthenticated()]

    @action(detail=False, methods=['post'], permission_classes=[IsAdminUser])
    def generate(self, request):
        """
        POST /api/v1/examinations/results/generate/
        Body: {"exam": 1, "school_class": 1}
        Calculates and generates overall results for all students in a class for a specific exam based on Marks.
        """
        exam_id = request.data.get('exam')
        class_id = request.data.get('school_class')

        if not exam_id or not class_id:
            return Response({"error": "exam and school_class are required."}, status=status.HTTP_400_BAD_REQUEST)

        students = Student.objects.filter(current_class_id=class_id, status='ACTIVE')
        generated_count = 0

        for student in students:
            # Aggregate marks for this student and exam
            student_marks = Marks.objects.filter(exam_id=exam_id, student=student)
            
            if not student_marks.exists():
                continue # Skip if no marks entered
                
            agg = student_marks.aggregate(
                obtained=Sum('obtained_marks'),
                total=Sum('total_marks')
            )
            
            obtained = agg['obtained'] or 0
            total = agg['total'] or 0
            percentage = (obtained / total) * 100 if total > 0 else 0
            
            # Simple overall grade calculation
            if percentage >= 90: grade = 'A+'
            elif percentage >= 80: grade = 'A'
            elif percentage >= 70: grade = 'B'
            elif percentage >= 60: grade = 'C'
            elif percentage >= 50: grade = 'D'
            else: grade = 'F'
            
            # Check if student failed any subject
            failed_subjects = student_marks.filter(is_passed=False).exists()
            passed = not failed_subjects and percentage >= 50

            Result.objects.update_or_create(
                exam_id=exam_id,
                student=student,
                defaults={
                    'total_marks_obtained': obtained,
                    'total_maximum_marks': total,
                    'percentage': percentage,
                    'overall_grade': grade,
                    'passed': passed,
                    'remarks': 'Failed in one or more subjects' if failed_subjects else 'Passed'
                }
            )
            generated_count += 1

        return Response({
            "message": f"Generated results for {generated_count} students.",
        }, status=status.HTTP_200_OK)
