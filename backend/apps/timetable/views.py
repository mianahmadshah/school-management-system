"""
Views for the timetable app.
"""
from django.urls import reverse_lazy
from django.shortcuts import redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView
from django.contrib.auth import get_user_model
from django.db.models import Q
from rest_framework import viewsets, filters
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from .models import Period, Timetable
from .forms import PeriodForm, TimetableForm
from apps.classes.models import Class, Section
from apps.subjects.models import Subject
from apps.teachers.models import Teacher
from .serializers import PeriodSerializer, TimetableSerializer
from apps.accounts.permissions import IsAdminUser, IsAdminOrTeacher

User = get_user_model()


class PeriodListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = Period
    template_name = 'timetable/period_list.html'
    context_object_name = 'periods'
    paginate_by = 20

    def test_func(self):
        return self.request.user.role == User.Role.ADMIN

    def handle_no_permission(self):
        return redirect('unauthorized')


class PeriodCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = Period
    form_class = PeriodForm
    template_name = 'timetable/period_form.html'
    success_url = reverse_lazy('period_list')

    def test_func(self):
        return self.request.user.role == User.Role.ADMIN

    def handle_no_permission(self):
        return redirect('unauthorized')

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, f'Period "{self.object.name}" created.')
        return response


class PeriodUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Period
    form_class = PeriodForm
    template_name = 'timetable/period_form.html'
    success_url = reverse_lazy('period_list')

    def test_func(self):
        return self.request.user.role == User.Role.ADMIN

    def handle_no_permission(self):
        return redirect('unauthorized')

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, f'Period "{self.object.name}" updated.')
        return response


class PeriodDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Period
    template_name = 'timetable/period_confirm_delete.html'
    success_url = reverse_lazy('period_list')

    def test_func(self):
        return self.request.user.role == User.Role.ADMIN

    def handle_no_permission(self):
        return redirect('unauthorized')


class TimetableListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = Timetable
    template_name = 'timetable/timetable_list.html'
    context_object_name = 'entries'
    paginate_by = 30

    def test_func(self):
        return self.request.user.role in [User.Role.ADMIN, User.Role.TEACHER]

    def handle_no_permission(self):
        return redirect('unauthorized')

    def get_queryset(self):
        qs = Timetable.objects.filter(is_active=True).select_related(
            'school_class', 'section', 'subject', 'teacher', 'period'
        )
        class_id = self.request.GET.get('class_id', '')
        if class_id:
            qs = qs.filter(school_class_id=class_id)
        day = self.request.GET.get('day', '')
        if day:
            qs = qs.filter(day_of_week=day)
        teacher_id = self.request.GET.get('teacher_id', '')
        if teacher_id:
            qs = qs.filter(teacher_id=teacher_id)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['classes'] = Class.objects.filter(is_active=True)
        context['teachers'] = Teacher.objects.all()
        context['days'] = Timetable.DayOfWeek.choices
        return context


class TimetableCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = Timetable
    form_class = TimetableForm
    template_name = 'timetable/timetable_form.html'
    success_url = reverse_lazy('timetable_list')

    def test_func(self):
        return self.request.user.role == User.Role.ADMIN

    def handle_no_permission(self):
        return redirect('unauthorized')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['classes'] = Class.objects.filter(is_active=True)
        return context

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Timetable entry created.')
        return response


class TimetableUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Timetable
    form_class = TimetableForm
    template_name = 'timetable/timetable_form.html'
    success_url = reverse_lazy('timetable_list')

    def test_func(self):
        return self.request.user.role == User.Role.ADMIN

    def handle_no_permission(self):
        return redirect('unauthorized')

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Timetable entry updated.')
        return response


class TimetableDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Timetable
    template_name = 'timetable/timetable_confirm_delete.html'
    success_url = reverse_lazy('timetable_list')

    def test_func(self):
        return self.request.user.role == User.Role.ADMIN

    def handle_no_permission(self):
        return redirect('unauthorized')


# Student view: my timetable
class StudentTimetableView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = Timetable
    template_name = 'timetable/my_timetable.html'
    context_object_name = 'entries'

    def test_func(self):
        return self.request.user.role == User.Role.STUDENT

    def handle_no_permission(self):
        return redirect('unauthorized')

    def get_queryset(self):
        user = self.request.user
        student = getattr(user, 'student_profile', None)
        if not student:
            return Timetable.objects.none()
        return Timetable.objects.filter(
            school_class=student.current_class,
            section=student.section,
            is_active=True
        ).select_related('subject', 'teacher', 'period').order_by('day_of_week', 'period__order')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Group by day
        days = {}
        for day, _ in Timetable.DayOfWeek.choices:
            days[day] = []
        for entry in context['entries']:
            days[entry.day_of_week].append(entry)
        context['days'] = days
        context['day_choices'] = Timetable.DayOfWeek.choices
        return context


# Teacher view: my timetable
class TeacherTimetableView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = Timetable
    template_name = 'timetable/my_timetable.html'
    context_object_name = 'entries'

    def test_func(self):
        return self.request.user.role == User.Role.TEACHER

    def handle_no_permission(self):
        return redirect('unauthorized')

    def get_queryset(self):
        user = self.request.user
        teacher = getattr(user, 'teacher_profile', None)
        if not teacher:
            return Timetable.objects.none()
        return Timetable.objects.filter(
            teacher=teacher,
            is_active=True
        ).select_related('school_class', 'section', 'subject', 'period').order_by('day_of_week', 'period__order')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        days = {}
        for day, _ in Timetable.DayOfWeek.choices:
            days[day] = []
        for entry in context['entries']:
            days[entry.day_of_week].append(entry)
        context['days'] = days
        context['day_choices'] = Timetable.DayOfWeek.choices
        return context


# DRF Viewsets
class PeriodViewSet(viewsets.ModelViewSet):
    queryset = Period.objects.all()
    serializer_class = PeriodSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['is_break']
    ordering_fields = ['order', 'start_time']
    ordering = ['order', 'start_time']

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAdminUser()]
        return [IsAuthenticated()]


class TimetableViewSet(viewsets.ModelViewSet):
    queryset = Timetable.objects.all()
    serializer_class = TimetableSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['school_class__name', 'subject__name', 'teacher__user__first_name', 'teacher__user__last_name']
    filterset_fields = ['school_class', 'section', 'day_of_week', 'teacher', 'period']
    ordering_fields = ['day_of_week', 'period__start_time']
    ordering = ['day_of_week', 'period__start_time']

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAdminUser()]
        return [IsAuthenticated()]