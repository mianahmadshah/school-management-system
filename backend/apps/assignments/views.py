"""
Views for the assignments app.
"""
from django.urls import reverse_lazy
from django.shortcuts import redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, FormView
from django.contrib.auth import get_user_model
from django.utils import timezone

from .models import Assignment, Submission
from .forms import AssignmentForm, SubmissionGradeForm
from apps.classes.models import Class, Section
from apps.subjects.models import Subject
from apps.teachers.models import Teacher
from apps.students.models import Student

from rest_framework import viewsets, filters
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from .serializers import AssignmentSerializer, SubmissionSerializer
from apps.accounts.permissions import IsAdminUser, IsAdminOrTeacher

User = get_user_model()


class AssignmentListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = Assignment
    template_name = 'assignments/assignment_list.html'
    context_object_name = 'assignments'
    paginate_by = 15

    def test_func(self):
        return self.request.user.role in [User.Role.ADMIN, User.Role.TEACHER, User.Role.STUDENT]

    def handle_no_permission(self):
        return redirect('unauthorized')

    def get_queryset(self):
        qs = Assignment.objects.filter(is_active=True).select_related('school_class', 'section', 'subject', 'teacher')
        user = self.request.user
        if user.is_student:
            student = getattr(user, 'student_profile', None)
            if student:
                qs = qs.filter(school_class=student.current_class, section=student.section)
        elif user.is_teacher:
            teacher = getattr(user, 'teacher_profile', None)
            if teacher:
                qs = qs.filter(teacher=teacher)
        class_id = self.request.GET.get('class_id', '')
        if class_id:
            qs = qs.filter(school_class_id=class_id)
        subject_id = self.request.GET.get('subject_id', '')
        if subject_id:
            qs = qs.filter(subject_id=subject_id)
        return qs.order_by('-assigned_date')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['classes'] = Class.objects.filter(is_active=True)
        context['subjects'] = Subject.objects.filter(is_active=True)
        user = self.request.user
        if user.is_student:
            student = getattr(user, 'student_profile', None)
            if student:
                context['my_submissions'] = {
                    s.assignment_id: s 
                    for s in Submission.objects.filter(student=student)
                }
        return context


class AssignmentDetailView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    model = Assignment
    template_name = 'assignments/assignment_detail.html'
    context_object_name = 'assignment'

    def test_func(self):
        return self.request.user.role in [User.Role.ADMIN, User.Role.TEACHER, User.Role.STUDENT]

    def handle_no_permission(self):
        return redirect('unauthorized')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        if user.is_student:
            student = getattr(user, 'student_profile', None)
            if student:
                context['my_submission'] = Submission.objects.filter(
                    assignment=self.object, student=student
                ).first()
        elif user.is_teacher:
            teacher = getattr(user, 'teacher_profile', None)
            if teacher and self.object.teacher == teacher:
                context['submissions'] = Submission.objects.filter(
                    assignment=self.object
                ).select_related('student__user')
        return context


class AssignmentCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = Assignment
    form_class = AssignmentForm
    template_name = 'assignments/assignment_form.html'
    success_url = reverse_lazy('assignment_list')

    def test_func(self):
        return self.request.user.role in [User.Role.ADMIN, User.Role.TEACHER]

    def handle_no_permission(self):
        return redirect('unauthorized')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['classes'] = Class.objects.filter(is_active=True)
        return context

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Assignment created.')
        return response


class AssignmentUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Assignment
    form_class = AssignmentForm
    template_name = 'assignments/assignment_form.html'
    success_url = reverse_lazy('assignment_list')

    def test_func(self):
        return self.request.user.role in [User.Role.ADMIN, User.Role.TEACHER]

    def handle_no_permission(self):
        return redirect('unauthorized')

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Assignment updated.')
        return response


class AssignmentDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Assignment
    template_name = 'assignments/assignment_confirm_delete.html'
    success_url = reverse_lazy('assignment_list')

    def test_func(self):
        return self.request.user.role in [User.Role.ADMIN, User.Role.TEACHER]

    def handle_no_permission(self):
        return redirect('unauthorized')


class GradeSubmissionView(LoginRequiredMixin, UserPassesTestMixin, FormView):
    template_name = 'assignments/grade_submission.html'
    form_class = SubmissionGradeForm

    def test_func(self):
        return self.request.user.role in [User.Role.ADMIN, User.Role.TEACHER]

    def handle_no_permission(self):
        return redirect('unauthorized')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        submission = get_object_or_404(Submission, pk=self.kwargs.get('pk'))
        context['submission'] = submission
        return context

    def form_valid(self, form):
        submission = get_object_or_404(Submission, pk=self.kwargs.get('pk'))
        submission.marks_obtained = form.cleaned_data['marks_obtained']
        submission.teacher_remarks = form.cleaned_data['teacher_remarks']
        submission.graded_by = self.request.user.teacher_profile
        submission.graded_at = timezone.now()
        submission.status = Submission.Status.GRADED
        submission.save()
        messages.success(self.request, 'Submission graded.')
        return redirect('assignment_detail', pk=submission.assignment.pk)


# DRF Viewsets
class AssignmentViewSet(viewsets.ModelViewSet):
    queryset = Assignment.objects.all()
    serializer_class = AssignmentSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'description', 'school_class__name', 'subject__name']
    filterset_fields = ['school_class', 'section', 'subject', 'teacher', 'is_active']
    ordering_fields = ['due_date', 'assigned_date']
    ordering = ['-due_date']

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAdminOrTeacher()]
        return [IsAuthenticated()]


class SubmissionViewSet(viewsets.ModelViewSet):
    queryset = Submission.objects.all()
    serializer_class = SubmissionSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ['assignment__title', 'student__user__first_name', 'student__user__last_name']
    filterset_fields = ['assignment', 'student', 'status']
    ordering_fields = ['submitted_at', 'graded_at']
    ordering = ['-submitted_at']

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAdminOrTeacher()]
        return [IsAuthenticated()]