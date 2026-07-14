"""
Views for the announcements app.
"""
from django.urls import reverse_lazy
from django.shortcuts import redirect
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.db.models import Q

from .models import Announcement
from .forms import AnnouncementForm
from apps.classes.models import Class, Section

from rest_framework import viewsets, filters
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from .serializers import AnnouncementSerializer
from apps.accounts.permissions import IsAdminUser, IsAdminOrTeacher

User = get_user_model()


class AnnouncementListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = Announcement
    template_name = 'announcements/announcement_list.html'
    context_object_name = 'announcements'
    paginate_by = 20

    def test_func(self):
        return self.request.user.role in [User.Role.ADMIN, User.Role.TEACHER, User.Role.STUDENT]

    def handle_no_permission(self):
        return redirect('unauthorized')

    def get_queryset(self):
        qs = Announcement.objects.filter(is_published=True)
        # Filter expired
        qs = qs.filter(Q(expires_at__isnull=True) | Q(expires_at__gt=timezone.now()))
        user = self.request.user
        if user.is_student:
            student = getattr(user, 'student_profile', None)
            if student:
                qs = qs.filter(
                    Q(target_audience=Announcement.Audience.STUDENTS) |
                    Q(target_audience=Announcement.Audience.SPECIFIC_CLASS, target_class=student.current_class) |
                    Q(target_audience=Announcement.Audience.SPECIFIC_SECTION, target_section=student.section)
                )
        elif user.is_teacher:
            qs = qs.filter(
                Q(target_audience=Announcement.Audience.TEACHERS) |
                Q(target_audience=Announcement.Audience.ALL)
            )
        return qs.order_by('-is_important', '-published_at')


class AnnouncementDetailView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    model = Announcement
    template_name = 'announcements/announcement_detail.html'
    context_object_name = 'announcement'

    def test_func(self):
        return self.request.user.role in [User.Role.ADMIN, User.Role.TEACHER, User.Role.STUDENT]

    def handle_no_permission(self):
        return redirect('unauthorized')


class AnnouncementCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = Announcement
    form_class = AnnouncementForm
    template_name = 'announcements/announcement_form.html'
    success_url = reverse_lazy('announcement_list')

    def test_func(self):
        return self.request.user.role in [User.Role.ADMIN, User.Role.TEACHER]

    def handle_no_permission(self):
        return redirect('unauthorized')

    def form_valid(self, form):
        form.instance.published_by = self.request.user
        response = super().form_valid(form)
        messages.success(self.request, 'Announcement published.')
        return response


class AnnouncementUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Announcement
    form_class = AnnouncementForm
    template_name = 'announcements/announcement_form.html'
    success_url = reverse_lazy('announcement_list')

    def test_func(self):
        return self.request.user.role in [User.Role.ADMIN, User.Role.TEACHER]

    def handle_no_permission(self):
        return redirect('unauthorized')

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Announcement updated.')
        return response


class AnnouncementDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Announcement
    template_name = 'announcements/announcement_confirm_delete.html'
    success_url = reverse_lazy('announcement_list')

    def test_func(self):
        return self.request.user.role == User.Role.ADMIN

    def handle_no_permission(self):
        return redirect('unauthorized')


# DRF Viewset
class AnnouncementViewSet(viewsets.ModelViewSet):
    queryset = Announcement.objects.all()
    serializer_class = AnnouncementSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'content']
    filterset_fields = ['target_audience', 'is_published', 'is_important']
    ordering_fields = ['published_at', 'is_important']
    ordering = ['-published_at']

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAdminOrTeacher()]
        return [IsAuthenticated()]