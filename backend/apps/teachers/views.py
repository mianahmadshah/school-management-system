"""
Views for the teachers app.
Handles both Web UI templates (ListView, DetailView, CreateView, UpdateView, DeleteView)
and REST API views for backward compatibility.
"""
from django.db import transaction
from django.urls import reverse_lazy
from django.shortcuts import redirect
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth import get_user_model
from django.db.models import Q

from .models import Teacher
from .forms import TeacherUserForm, TeacherUserEditForm, TeacherProfileForm

# DRF Imports for backward compatibility
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend

from .serializers import (
    TeacherListSerializer,
    TeacherDetailSerializer,
    TeacherCreateSerializer,
    TeacherUpdateSerializer,
)
from apps.accounts.permissions import IsAdminUser, IsAdminOrTeacher

User = get_user_model()


# ─────────────────────────────────────────────────────────────
# TEMPLATE-BASED VIEWS (Web UI)
# ─────────────────────────────────────────────────────────────

class TeacherListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    """
    Renders teacher directory list, with search and department filtering.
    """
    model = Teacher
    template_name = 'teachers/teacher_list.html'
    context_object_name = 'teachers'
    paginate_by = 10

    def test_func(self):
        return self.request.user.role == User.Role.ADMIN

    def handle_no_permission(self):
        return redirect('unauthorized')

    def get_queryset(self):
        queryset = Teacher.objects.select_related('user').all()
        
        # Searching
        q = self.request.GET.get('q', '')
        if q:
            queryset = queryset.filter(
                Q(user__first_name__icontains=q) |
                Q(user__last_name__icontains=q) |
                Q(employee_id__icontains=q) |
                Q(department__icontains=q) |
                Q(specialization__icontains=q)
            )

        # Filtering by Department
        dept = self.request.GET.get('department', '')
        if dept:
            queryset = queryset.filter(department__iexact=dept)

        # Filtering by Employment Type
        emp_type = self.request.GET.get('employment_type', '')
        if emp_type:
            queryset = queryset.filter(employment_type=emp_type)

        # Filtering by Status
        status_filter = self.request.GET.get('status', '')
        if status_filter:
            queryset = queryset.filter(status=status_filter)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Fetch distinct departments for filter dropdown
        context['departments'] = Teacher.objects.values_list('department', flat=True).distinct().exclude(department__isnull=True).exclude(department='')
        
        # Preserve query params in pagination links
        query_params = self.request.GET.copy()
        if 'page' in query_params:
            query_params.pop('page')
        context['query_params'] = query_params.urlencode()
        return context


class TeacherDetailView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    """
    Renders full detailed card of a teacher.
    """
    model = Teacher
    template_name = 'teachers/teacher_detail.html'
    context_object_name = 'teacher'

    def test_func(self):
        # Admin or Teacher themselves can view
        user = self.request.user
        if user.role == User.Role.ADMIN:
            return True
        return hasattr(user, 'teacher_profile') and user.teacher_profile.pk == self.get_object().pk

    def handle_no_permission(self):
        return redirect('unauthorized')


class TeacherCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    """
    Form view to create a teacher user credential + teacher record in one transaction.
    """
    model = Teacher
    form_class = TeacherProfileForm
    template_name = 'teachers/teacher_form.html'
    success_url = reverse_lazy('teacher_list')

    def test_func(self):
        return self.request.user.role == User.Role.ADMIN

    def handle_no_permission(self):
        return redirect('unauthorized')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['user_form'] = TeacherUserForm(self.request.POST)
        else:
            context['user_form'] = TeacherUserForm()
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        user_form = context['user_form']
        if user_form.is_valid():
            try:
                with transaction.atomic():
                    user = user_form.save(commit=False)
                    user.role = User.Role.TEACHER
                    user.username = user.email
                    user.set_password(user_form.cleaned_data['password'])
                    user.save()
                    
                    teacher = form.save(commit=False)
                    teacher.user = user
                    teacher.save()
                messages.success(self.request, f"Teacher {teacher.full_name} created successfully.")
                return redirect(self.success_url)
            except Exception as e:
                messages.error(self.request, f"Error saving records: {str(e)}")
                return self.form_invalid(form)
        else:
            return self.form_invalid(form)


class TeacherUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """
    Updates a teacher profile and their associated User credentials.
    """
    model = Teacher
    form_class = TeacherProfileForm
    template_name = 'teachers/teacher_form.html'
    success_url = reverse_lazy('teacher_list')

    def test_func(self):
        return self.request.user.role == User.Role.ADMIN

    def handle_no_permission(self):
        return redirect('unauthorized')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['user_form'] = TeacherUserEditForm(self.request.POST, instance=self.object.user)
        else:
            context['user_form'] = TeacherUserEditForm(instance=self.object.user)
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        user_form = context['user_form']
        if user_form.is_valid():
            try:
                with transaction.atomic():
                    user_form.save()
                    form.save()
                messages.success(self.request, f"Teacher {self.object.full_name} updated successfully.")
                return redirect(self.success_url)
            except Exception as e:
                messages.error(self.request, f"Error saving changes: {str(e)}")
                return self.form_invalid(form)
        else:
            return self.form_invalid(form)


class TeacherDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    """
    Deletes a teacher record, triggering a cascade delete on their User credentials.
    """
    model = Teacher
    template_name = 'teachers/teacher_confirm_delete.html'
    success_url = reverse_lazy('teacher_list')

    def test_func(self):
        return self.request.user.role == User.Role.ADMIN

    def handle_no_permission(self):
        return redirect('unauthorized')

    def post(self, request, *args, **kwargs):
        teacher = self.get_object()
        teacher_name = teacher.full_name
        # Delete user account, which deletes teacher profile via CASCADE
        teacher.user.delete()
        messages.success(request, f"Teacher {teacher_name} deleted successfully.")
        return redirect(self.success_url)


# ─────────────────────────────────────────────────────────────
# DRF VIEWSET (Backward Compatibility)
# ─────────────────────────────────────────────────────────────

class TeacherViewSet(viewsets.ModelViewSet):
    queryset = Teacher.objects.select_related('user').all()
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['user__first_name', 'user__last_name', 'user__email', 'employee_id', 'department', 'specialization']
    filterset_fields = ['status', 'gender', 'department', 'employment_type']
    ordering_fields = ['employee_id', 'joining_date', 'experience_years']
    ordering = ['employee_id']

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes = [IsAdminUser]
        else:
            permission_classes = [IsAdminOrTeacher]
        return [permission() for permission in permission_classes]

    def get_serializer_class(self):
        if self.action == 'create':
            return TeacherCreateSerializer
        if self.action in ['update', 'partial_update']:
            return TeacherUpdateSerializer
        if self.action == 'retrieve':
            return TeacherDetailSerializer
        return TeacherListSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        teacher = serializer.save()
        detail_serializer = TeacherDetailSerializer(teacher, context={'request': request})
        return Response({'message': f'Teacher {teacher.full_name} created successfully.', 'data': detail_serializer.data}, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['get'], permission_classes=[IsAdminUser])
    def stats(self, request):
        total = Teacher.objects.count()
        active = Teacher.objects.filter(status='ACTIVE').count()
        on_leave = Teacher.objects.filter(status='ON_LEAVE').count()
        inactive = Teacher.objects.filter(status='INACTIVE').count()
        full_time = Teacher.objects.filter(employment_type='FULL_TIME').count()
        part_time = Teacher.objects.filter(employment_type='PART_TIME').count()
        return Response({
            'total_teachers': total, 'active': active, 'on_leave': on_leave, 'inactive': inactive,
            'employment_breakdown': {'full_time': full_time, 'part_time': part_time}
        })

    @action(detail=True, methods=['get'], permission_classes=[IsAdminOrTeacher])
    def profile(self, request, pk=None):
        teacher = self.get_object()
        serializer = TeacherDetailSerializer(teacher, context={'request': request})
        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        teacher = self.get_object()
        teacher_name = teacher.full_name
        teacher.user.delete()
        return Response({'message': f'Teacher {teacher_name} and their account have been deleted.'}, status=status.HTTP_200_OK)
