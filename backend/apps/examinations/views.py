"""
Views for the examinations app.
Provides both Web UI templates and API views.
"""
from django.urls import reverse_lazy, reverse
from django.shortcuts import redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, FormView, View, TemplateView
from django.contrib.auth import get_user_model
from django.db.models import Q, Sum

from .models import Exam, Marks, Result
from .forms import ExamForm, MarksForm, MarksEntryForm
from apps.classes.models import Class
from apps.students.models import Student
from apps.subjects.models import Subject

# DRF imports for API
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Sum

from .serializers import (
    ExamSerializer, MarksSerializer, ResultSerializer, BulkMarksEntrySerializer
)
from apps.accounts.permissions import IsAdminUser, IsAdminOrTeacher

User = get_user_model()


# ─────────────────────────────────────────────────────────────
# TEMPLATE-BASED VIEWS (Web UI) — Exam
# ─────────────────────────────────────────────────────────────

class ExamListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    """Renders list of exams."""
    model = Exam
    template_name = 'examinations/exam_list.html'
    context_object_name = 'exams'
    paginate_by = 10

    def test_func(self):
        return self.request.user.role in [User.Role.ADMIN, User.Role.TEACHER]

    def handle_no_permission(self):
        return redirect('unauthorized')

    def get_queryset(self):
        queryset = Exam.objects.select_related('subject', 'school_class', 'created_by')
        q = self.request.GET.get('q', '')
        if q:
            queryset = queryset.filter(Q(name__icontains=q) | Q(subject__name__icontains=q))
        class_id = self.request.GET.get('class_id', '')
        if class_id:
            queryset = queryset.filter(school_class_id=class_id)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['classes'] = Class.objects.filter(is_active=True)
        return context


class ExamDetailView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    """Renders detailed view of an exam."""
    model = Exam
    template_name = 'examinations/exam_detail.html'
    context_object_name = 'exam'

    def test_func(self):
        return self.request.user.role in [User.Role.ADMIN, User.Role.TEACHER]

    def handle_no_permission(self):
        return redirect('unauthorized')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['marks_list'] = Marks.objects.filter(exam=self.object).select_related('student__user', 'subject')
        return context


class ExamCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    """Form view to create a new exam."""
    model = Exam
    form_class = ExamForm
    template_name = 'examinations/exam_form.html'
    success_url = reverse_lazy('exam_list')

    def test_func(self):
        return self.request.user.role == User.Role.ADMIN

    def handle_no_permission(self):
        return redirect('unauthorized')

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        response = super().form_valid(form)
        messages.success(self.request, f'Exam "{self.object.name}" created successfully.')
        return response


class ExamUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """Form view to update an exam."""
    model = Exam
    form_class = ExamForm
    template_name = 'examinations/exam_form.html'
    success_url = reverse_lazy('exam_list')

    def test_func(self):
        return self.request.user.role == User.Role.ADMIN

    def handle_no_permission(self):
        return redirect('unauthorized')

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, f'Exam "{self.object.name}" updated successfully.')
        return response


class ExamDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    """Deletes an exam."""
    model = Exam
    template_name = 'examinations/exam_confirm_delete.html'
    success_url = reverse_lazy('exam_list')

    def test_func(self):
        return self.request.user.role == User.Role.ADMIN

    def handle_no_permission(self):
        return redirect('unauthorized')


# ─────────────────────────────────────────────────────────────
# TEMPLATE-BASED VIEWS (Web UI) — Marks Entry
# ─────────────────────────────────────────────────────────────

class MarksEntryView(LoginRequiredMixin, UserPassesTestMixin, FormView):
    """Form view to enter marks for students in an exam."""
    template_name = 'examinations/marks_entry.html'
    form_class = MarksEntryForm
    success_url = reverse_lazy('exam_list')

    def test_func(self):
        return self.request.user.role in [User.Role.ADMIN, User.Role.TEACHER]

    def handle_no_permission(self):
        return redirect('unauthorized')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['exams'] = Exam.objects.filter(is_active=True).select_related('subject', 'school_class')
        context['classes'] = Class.objects.filter(is_active=True)
        
        exam_id = self.request.GET.get('exam_id', '')
        class_id = self.request.GET.get('class_id', '')
        subject_id = self.request.GET.get('subject_id', '')
        
        context['selected_exam'] = exam_id
        context['selected_class'] = class_id
        context['selected_subject'] = subject_id
        
        if exam_id and class_id and subject_id:
            exam = get_object_or_404(Exam, pk=exam_id)
            students = Student.objects.filter(current_class_id=class_id, status='ACTIVE').select_related('user').order_by('roll_number')
            
            # Get existing marks
            existing_marks = {}
            for m in Marks.objects.filter(exam_id=exam_id, subject_id=subject_id):
                existing_marks[m.student_id] = m
            
            context['students'] = students
            context['existing_marks'] = existing_marks
            context['exam_obj'] = exam
        
        return context

    def form_valid(self, form):
        exam_id = form.cleaned_data['exam']
        subject_id = form.cleaned_data['subject']
        student_ids = self.request.POST.getlist('student_ids')
        obtained_marks = self.request.POST.getlist('obtained_marks')
        practical_marks = self.request.POST.getlist('practical_marks')
        remarks_list = self.request.POST.getlist('remarks_list')
        
        count = 0
        for i, student_id in enumerate(student_ids):
            obt = obtained_marks[i] if i < len(obtained_marks) else None
            if obt == '' or obt is None:
                continue
            pract = practical_marks[i] if i < len(practical_marks) else 0
            remarks = remarks_list[i] if i < len(remarks_list) else ''
            
            Marks.objects.update_or_create(
                exam_id=exam_id,
                student_id=student_id,
                subject_id=subject_id,
                defaults={
                    'obtained_marks': obt,
                    'practical_marks': pract or 0,
                    'remarks': remarks,
                    'submitted_by': getattr(self.request.user, 'teacher_profile', None),
                }
            )
            count += 1
        
        messages.success(self.request, f'Marks entered/updated for {count} student(s).')
        return redirect(self.success_url)


class MarksListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    """Renders list of marks records."""
    model = Marks
    template_name = 'examinations/marks_list.html'
    context_object_name = 'marks_list'
    paginate_by = 20

    def test_func(self):
        return self.request.user.role in [User.Role.ADMIN, User.Role.TEACHER]

    def handle_no_permission(self):
        return redirect('unauthorized')

    def get_queryset(self):
        queryset = Marks.objects.select_related('exam', 'student__user', 'subject')
        exam_id = self.request.GET.get('exam_id', '')
        if exam_id:
            queryset = queryset.filter(exam_id=exam_id)
        class_id = self.request.GET.get('class_id', '')
        if class_id:
            queryset = queryset.filter(student__current_class_id=class_id)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['exams'] = Exam.objects.filter(is_active=True).select_related('subject', 'school_class')
        context['classes'] = Class.objects.filter(is_active=True)
        return context


# ─────────────────────────────────────────────────────────────
# TEMPLATE-BASED VIEWS — Results
# ─────────────────────────────────────────────────────────────

class ResultListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    """Renders list of results."""
    model = Result
    template_name = 'examinations/result_list.html'
    context_object_name = 'results'
    paginate_by = 20

    def test_func(self):
        return self.request.user.role in [User.Role.ADMIN, User.Role.TEACHER, User.Role.STUDENT]

    def handle_no_permission(self):
        return redirect('unauthorized')

    def get_queryset(self):
        queryset = Result.objects.select_related('exam', 'student__user', 'student__current_class')
        user = self.request.user
        if user.is_student:
            student = getattr(user, 'student_profile', None)
            if student:
                queryset = queryset.filter(student=student)
        
        exam_id = self.request.GET.get('exam_id', '')
        if exam_id:
            queryset = queryset.filter(exam_id=exam_id)
        class_id = self.request.GET.get('class_id', '')
        if class_id:
            queryset = queryset.filter(student__current_class_id=class_id)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['exams'] = Exam.objects.filter(is_active=True).select_related('subject', 'school_class')
        context['classes'] = Class.objects.filter(is_active=True)
        return context


class GenerateResultView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    """Generate results for an exam."""
    template_name = 'examinations/generate_result.html'

    def test_func(self):
        return self.request.user.role == User.Role.ADMIN

    def handle_no_permission(self):
        return redirect('unauthorized')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['exams'] = Exam.objects.filter(is_active=True).select_related('subject', 'school_class')
        context['classes'] = Class.objects.filter(is_active=True)
        return context

    def post(self, request, *args, **kwargs):
        exam_id = request.POST.get('exam_id')
        class_id = request.POST.get('class_id')
        
        if not exam_id or not class_id:
            messages.error(request, 'Please select both exam and class.')
            return redirect('generate_result')
        
        students = Student.objects.filter(current_class_id=class_id, status='ACTIVE')
        generated_count = 0
        
        for student in students:
            student_marks = Marks.objects.filter(exam_id=exam_id, student=student)
            if not student_marks.exists():
                continue
            
            agg = student_marks.aggregate(obtained=Sum('obtained_marks'), total=Sum('total_marks'))
            obtained = agg['obtained'] or 0
            total = agg['total'] or 0
            percentage = (obtained / total) * 100 if total > 0 else 0
            
            if percentage >= 90: grade = 'A+'
            elif percentage >= 80: grade = 'A'
            elif percentage >= 70: grade = 'B'
            elif percentage >= 60: grade = 'C'
            elif percentage >= 50: grade = 'D'
            else: grade = 'F'
            
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
        
        messages.success(request, f'Results generated for {generated_count} student(s).')
        return redirect('result_list')


# ─────────────────────────────────────────────────────────────
# Student Exam View
# ─────────────────────────────────────────────────────────────

class StudentResultView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    """Student views their own exam results with marks breakdown."""
    model = Result
    template_name = 'examinations/my_results.html'
    context_object_name = 'results'

    def test_func(self):
        return self.request.user.role == User.Role.STUDENT

    def handle_no_permission(self):
        return redirect('unauthorized')

    def get_queryset(self):
        student = getattr(self.request.user, 'student_profile', None)
        if not student:
            return Result.objects.none()
        return Result.objects.filter(student=student).select_related('exam', 'exam__subject')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        student = getattr(self.request.user, 'student_profile', None)
        if student:
            for result in context['results']:
                result.marks_details = Marks.objects.filter(exam=result.exam, student=student).select_related('subject')
        return context


# ─────────────────────────────────────────────────────────────
# DRF VIEWSETS (API) — Keep existing API code intact
# ─────────────────────────────────────────────────────────────

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
        serializer = BulkMarksEntrySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        result = serializer.save()
        return Response({"message": "Marks entered successfully.", "details": result}, status=status.HTTP_200_OK)


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
        exam_id = request.data.get('exam')
        class_id = request.data.get('school_class')
        if not exam_id or not class_id:
            return Response({"error": "exam and school_class are required."}, status=status.HTTP_400_BAD_REQUEST)
        students = Student.objects.filter(current_class_id=class_id, status='ACTIVE')
        generated_count = 0
        for student in students:
            student_marks = Marks.objects.filter(exam_id=exam_id, student=student)
            if not student_marks.exists():
                continue
            agg = student_marks.aggregate(obtained=Sum('obtained_marks'), total=Sum('total_marks'))
            obtained = agg['obtained'] or 0
            total = agg['total'] or 0
            percentage = (obtained / total) * 100 if total > 0 else 0
            if percentage >= 90: grade = 'A+'
            elif percentage >= 80: grade = 'A'
            elif percentage >= 70: grade = 'B'
            elif percentage >= 60: grade = 'C'
            elif percentage >= 50: grade = 'D'
            else: grade = 'F'
            failed_subjects = student_marks.filter(is_passed=False).exists()
            passed = not failed_subjects and percentage >= 50
            Result.objects.update_or_create(
                exam_id=exam_id, student=student,
                defaults={'total_marks_obtained': obtained, 'total_maximum_marks': total, 'percentage': percentage, 'overall_grade': grade, 'passed': passed, 'remarks': 'Failed in one or more subjects' if failed_subjects else 'Passed'}
            )
            generated_count += 1
        return Response({"message": f"Generated results for {generated_count} students."}, status=status.HTTP_200_OK)