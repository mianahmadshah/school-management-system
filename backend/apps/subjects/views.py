"""
Views for the subjects app.
Handles Subject and Enrollment models via both Web UI and API.
"""
from django.urls import reverse_lazy
from django.shortcuts import redirect
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth import get_user_model
from django.db.models import Q

from .models import Subject, Enrollment
from .forms import SubjectForm, EnrollmentForm

# DRF imports for API
from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Count

from .serializers import SubjectSerializer, EnrollmentSerializer
from apps.accounts.permissions import IsAdminUser, IsAdminOrTeacher

User = get_user_model()


# ─────────────────────────────────────────────────────────────
# TEMPLATE-BASED VIEWS (Web UI) — Subject
# ─────────────────────────────────────────────────────────────

class SubjectListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    """Renders list of all subjects."""
    model = Subject
    template_name = 'subjects/subject_list.html'
    context_object_name = 'subjects'
    paginate_by = 10

    def test_func(self):
        return self.request.user.role in [User.Role.ADMIN, User.Role.TEACHER]

    def handle_no_permission(self):
        return redirect('unauthorized')

    def get_queryset(self):
        queryset = Subject.objects.select_related('school_class', 'teacher__user').all()
        q = self.request.GET.get('q', '')
        if q:
            queryset = queryset.filter(
                Q(name__icontains=q) | Q(code__icontains=q) | Q(school_class__name__icontains=q)
            )
        class_id = self.request.GET.get('class_id', '')
        if class_id:
            queryset = queryset.filter(school_class_id=class_id)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        from apps.classes.models import Class
        context['classes'] = Class.objects.filter(is_active=True)
        return context


class SubjectDetailView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    """Renders detailed view of a subject."""
    model = Subject
    template_name = 'subjects/subject_detail.html'
    context_object_name = 'subject'

    def test_func(self):
        return self.request.user.role in [User.Role.ADMIN, User.Role.TEACHER]

    def handle_no_permission(self):
        return redirect('unauthorized')


class SubjectCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    """Form view to create a new subject."""
    model = Subject
    form_class = SubjectForm
    template_name = 'subjects/subject_form.html'
    success_url = reverse_lazy('subject_list')

    def test_func(self):
        return self.request.user.role == User.Role.ADMIN

    def handle_no_permission(self):
        return redirect('unauthorized')

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, f'Subject "{self.object.name}" created successfully.')
        return response


class SubjectUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """Form view to update an existing subject."""
    model = Subject
    form_class = SubjectForm
    template_name = 'subjects/subject_form.html'
    success_url = reverse_lazy('subject_list')

    def test_func(self):
        return self.request.user.role == User.Role.ADMIN

    def handle_no_permission(self):
        return redirect('unauthorized')

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, f'Subject "{self.object.name}" updated successfully.')
        return response


class SubjectDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    """Deletes a subject."""
    model = Subject
    template_name = 'subjects/subject_confirm_delete.html'
    success_url = reverse_lazy('subject_list')

    def test_func(self):
        return self.request.user.role == User.Role.ADMIN

    def handle_no_permission(self):
        return redirect('unauthorized')

    def post(self, request, *args, **kwargs):
        subject = self.get_object()
        subject_name = subject.name
        subject.delete()
        messages.success(request, f'Subject "{subject_name}" deleted successfully.')
        return redirect(self.success_url)


# ─────────────────────────────────────────────────────────────
# TEMPLATE-BASED VIEWS (Web UI) — Enrollment
# ─────────────────────────────────────────────────────────────

class EnrollmentCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    """Form view to enroll a student in a class/section."""
    model = Enrollment
    form_class = EnrollmentForm
    template_name = 'subjects/enrollment_form.html'
    success_url = reverse_lazy('student_list')

    def test_func(self):
        return self.request.user.role == User.Role.ADMIN

    def handle_no_permission(self):
        return redirect('unauthorized')

    def form_valid(self, form):
        enrollment = form.save()
        # Update student's current class and section
        if enrollment.is_active:
            student = enrollment.student
            student.current_class = enrollment.school_class
            student.section = enrollment.section
            student.roll_number = enrollment.roll_number or student.roll_number
            student.save()
        messages.success(self.request, f'Student enrolled successfully in {enrollment.school_class.name}.')
        return redirect(self.success_url)


# ─────────────────────────────────────────────────────────────
# DRF VIEWSETS (API) — Keep existing API code intact
# ─────────────────────────────────────────────────────────────

class SubjectViewSet(viewsets.ModelViewSet):
    """CRUD ViewSet for Subjects."""
    queryset = Subject.objects.select_related('school_class', 'teacher__user').all()
    serializer_class = SubjectSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'code', 'school_class__name']
    filterset_fields = ['school_class', 'subject_type', 'is_active', 'teacher']
    ordering_fields = ['name', 'code', 'school_class']
    ordering = ['school_class', 'name']

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAdminUser()]
        return [IsAdminOrTeacher()]

    @action(detail=False, methods=['get'], permission_classes=[IsAdminUser])
    def stats(self, request):
        total = Subject.objects.count()
        active = Subject.objects.filter(is_active=True).count()
        return Response({'total_subjects': total, 'active_subjects': active})


class EnrollmentViewSet(viewsets.ModelViewSet):
    """CRUD ViewSet for Enrollments."""
    queryset = Enrollment.objects.select_related('student__user', 'school_class', 'section').all()
    serializer_class = EnrollmentSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['student__user__first_name', 'student__user__last_name', 'student__admission_number', 'roll_number']
    filterset_fields = ['school_class', 'section', 'academic_year', 'is_active']
    ordering_fields = ['academic_year', 'school_class', 'student__user__first_name']
    ordering = ['-academic_year', 'school_class', 'section']

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAdminUser()]
        return [IsAdminOrTeacher()]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        enrollment = serializer.save()
        if enrollment.is_active:
            student = enrollment.student
            student.current_class = enrollment.school_class
            student.section = enrollment.section
            student.roll_number = enrollment.roll_number or student.roll_number
            student.save()
        return Response(
            {'message': f'Student enrolled successfully in {enrollment.school_class.name} {enrollment.section.name}.', 'data': EnrollmentSerializer(enrollment).data},
            status=status.HTTP_201_CREATED
        )