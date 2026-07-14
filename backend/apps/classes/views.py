"""
Views for the classes app.
Provides full CRUD for both Class and Section models via both Web UI and API.
"""
from django.urls import reverse_lazy
from django.shortcuts import redirect
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth import get_user_model
from django.db.models import Q

from .models import Class, Section
from .forms import ClassForm, SectionForm

# DRF imports for API
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Count

from .serializers import (
    ClassSerializer,
    ClassListSerializer,
    ClassCreateUpdateSerializer,
    SectionSerializer,
)
from apps.accounts.permissions import IsAdminUser, IsAdminOrTeacher

User = get_user_model()


# ─────────────────────────────────────────────────────────────
# TEMPLATE-BASED VIEWS (Web UI) — Class
# ─────────────────────────────────────────────────────────────

class ClassListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    """Renders list of all classes."""
    model = Class
    template_name = 'classes/class_list.html'
    context_object_name = 'classes'
    paginate_by = 10

    def test_func(self):
        return self.request.user.role in [User.Role.ADMIN, User.Role.TEACHER]

    def handle_no_permission(self):
        return redirect('unauthorized')

    def get_queryset(self):
        queryset = Class.objects.select_related('class_teacher__user').prefetch_related('sections')
        q = self.request.GET.get('q', '')
        if q:
            queryset = queryset.filter(
                Q(name__icontains=q) | Q(description__icontains=q)
            )
        return queryset


class ClassDetailView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    """Renders detailed view of a class with its sections."""
    model = Class
    template_name = 'classes/class_detail.html'
    context_object_name = 'class_obj'

    def test_func(self):
        return self.request.user.role in [User.Role.ADMIN, User.Role.TEACHER]

    def handle_no_permission(self):
        return redirect('unauthorized')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['sections'] = self.object.sections.select_related('section_teacher__user').all()
        return context


class ClassCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    """Form view to create a new class."""
    model = Class
    form_class = ClassForm
    template_name = 'classes/class_form.html'
    success_url = reverse_lazy('class_list')

    def test_func(self):
        return self.request.user.role == User.Role.ADMIN

    def handle_no_permission(self):
        return redirect('unauthorized')

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, f'Class "{self.object.name}" created successfully.')
        return response


class ClassUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """Form view to update an existing class."""
    model = Class
    form_class = ClassForm
    template_name = 'classes/class_form.html'
    success_url = reverse_lazy('class_list')

    def test_func(self):
        return self.request.user.role == User.Role.ADMIN

    def handle_no_permission(self):
        return redirect('unauthorized')

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, f'Class "{self.object.name}" updated successfully.')
        return response


class ClassDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    """Deletes a class."""
    model = Class
    template_name = 'classes/class_confirm_delete.html'
    success_url = reverse_lazy('class_list')

    def test_func(self):
        return self.request.user.role == User.Role.ADMIN

    def handle_no_permission(self):
        return redirect('unauthorized')

    def post(self, request, *args, **kwargs):
        class_obj = self.get_object()
        class_name = class_obj.name
        class_obj.delete()
        messages.success(request, f'Class "{class_name}" deleted successfully.')
        return redirect(self.success_url)


# ─────────────────────────────────────────────────────────────
# TEMPLATE-BASED VIEWS (Web UI) — Section
# ─────────────────────────────────────────────────────────────

class SectionCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    """Form view to create a new section within a class."""
    model = Section
    form_class = SectionForm
    template_name = 'classes/section_form.html'
    success_url = reverse_lazy('class_list')

    def test_func(self):
        return self.request.user.role == User.Role.ADMIN

    def handle_no_permission(self):
        return redirect('unauthorized')

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, f'Section "{self.object}" created successfully.')
        return response


class SectionUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """Form view to update an existing section."""
    model = Section
    form_class = SectionForm
    template_name = 'classes/section_form.html'
    success_url = reverse_lazy('class_list')

    def test_func(self):
        return self.request.user.role == User.Role.ADMIN

    def handle_no_permission(self):
        return redirect('unauthorized')

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, f'Section "{self.object}" updated successfully.')
        return response


class SectionDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    """Deletes a section."""
    model = Section
    template_name = 'classes/section_confirm_delete.html'
    success_url = reverse_lazy('class_list')

    def test_func(self):
        return self.request.user.role == User.Role.ADMIN

    def handle_no_permission(self):
        return redirect('unauthorized')

    def post(self, request, *args, **kwargs):
        section = self.get_object()
        section_name = str(section)
        section.delete()
        messages.success(request, f'Section "{section_name}" deleted successfully.')
        return redirect(self.success_url)


# ─────────────────────────────────────────────────────────────
# DRF VIEWSETS (API) — Keep existing API code intact
# ─────────────────────────────────────────────────────────────

class ClassViewSet(viewsets.ModelViewSet):
    """API CRUD ViewSet for Class management."""
    queryset = Class.objects.annotate(
        total_sections_count=Count('sections', distinct=True),
        total_students_count=Count('sections__enrollments', distinct=True),
    ).prefetch_related('sections').select_related('class_teacher__user')

    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description']
    filterset_fields = ['is_active']
    ordering_fields = ['numeric_grade', 'name', 'created_at']
    ordering = ['numeric_grade', 'name']

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAdminUser()]
        return [IsAdminOrTeacher()]

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return ClassSerializer
        if self.action in ['create', 'update', 'partial_update']:
            return ClassCreateUpdateSerializer
        return ClassListSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        school_class = serializer.save()
        return Response(
            {'message': f'Class "{school_class.name}" created successfully.', 'data': ClassSerializer(school_class).data},
            status=status.HTTP_201_CREATED
        )

    @action(detail=False, methods=['get'], permission_classes=[IsAdminOrTeacher])
    def active(self, request):
        classes = self.queryset.filter(is_active=True)
        serializer = ClassListSerializer(classes, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'], permission_classes=[IsAdminOrTeacher])
    def sections(self, request, pk=None):
        school_class = self.get_object()
        sections = school_class.sections.filter(is_active=True).select_related('section_teacher__user')
        serializer = SectionSerializer(sections, many=True)
        return Response({'class': school_class.name, 'total_sections': sections.count(), 'sections': serializer.data})

    @action(detail=False, methods=['get'], permission_classes=[IsAdminUser])
    def stats(self, request):
        total = Class.objects.count()
        active = Class.objects.filter(is_active=True).count()
        total_sections = Section.objects.count()
        active_sections = Section.objects.filter(is_active=True).count()
        return Response({'total_classes': total, 'active_classes': active, 'total_sections': total_sections, 'active_sections': active_sections})


class SectionViewSet(viewsets.ModelViewSet):
    """CRUD ViewSet for Section management."""
    queryset = Section.objects.select_related('school_class', 'section_teacher__user').all()
    serializer_class = SectionSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'school_class__name', 'room_number']
    filterset_fields = ['school_class', 'is_active']
    ordering_fields = ['school_class', 'name']
    ordering = ['school_class', 'name']

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAdminUser()]
        return [IsAdminOrTeacher()]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        section = serializer.save()
        return Response({'message': f'Section "{section}" created successfully.', 'data': SectionSerializer(section).data}, status=status.HTTP_201_CREATED)