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

from .models import Class, Section, AcademicSession
from .forms import ClassForm, SectionForm, AcademicSessionForm
from apps.subjects.models import Enrollment
from apps.examinations.models import Result

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


# ─────────────────────────────────────────────────────────────
# ACADEMIC SESSION & PROMOTION VIEWS
# ─────────────────────────────────────────────────────────────

class AcademicSessionListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = AcademicSession
    template_name = 'classes/session_list.html'
    context_object_name = 'sessions'

    def test_func(self):
        return self.request.user.role == User.Role.ADMIN

    def handle_no_permission(self):
        return redirect('unauthorized')


class AcademicSessionCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = AcademicSession
    form_class = AcademicSessionForm
    template_name = 'classes/session_form.html'
    success_url = reverse_lazy('session_list')

    def test_func(self):
        return self.request.user.role == User.Role.ADMIN

    def handle_no_permission(self):
        return redirect('unauthorized')

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, f'Academic Session "{self.object.name}" created successfully.')
        return response


class AcademicSessionUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = AcademicSession
    form_class = AcademicSessionForm
    template_name = 'classes/session_form.html'
    success_url = reverse_lazy('session_list')

    def test_func(self):
        return self.request.user.role == User.Role.ADMIN

    def handle_no_permission(self):
        return redirect('unauthorized')


class SessionClosingView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    """
    Session Closing & Promotion Console.
    Calculates final exam averages, pass/fail status, attendance rates, and fee balance status
    for all enrolled students in the active session.
    """
    model = Enrollment
    template_name = 'classes/session_closing.html'
    context_object_name = 'enrollments'

    def test_func(self):
        return self.request.user.role == User.Role.ADMIN

    def handle_no_permission(self):
        return redirect('unauthorized')

    def get_queryset(self):
        session_id = self.request.GET.get('session_id')
        if session_id:
            session = AcademicSession.objects.filter(pk=session_id).first()
        else:
            session = AcademicSession.get_current_session()
        
        if not session:
            return Enrollment.objects.none()

        return Enrollment.objects.filter(
            academic_session=session,
            is_active=True
        ).select_related('student__user', 'school_class', 'section', 'academic_session')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['sessions'] = AcademicSession.objects.all()
        session_id = self.request.GET.get('session_id')
        if session_id:
            context['current_session'] = AcademicSession.objects.filter(pk=session_id).first()
        else:
            context['current_session'] = AcademicSession.get_current_session()

        enrollment_details = []
        for enr in context['enrollments']:
            student = enr.student
            results = Result.objects.filter(student=student, exam__academic_session=enr.academic_session)
            if results.exists():
                avg_pct = sum(r.percentage for r in results) / results.count()
                all_passed = all(r.passed for r in results)
            else:
                avg_pct = 0
                all_passed = True

            from apps.attendance.models import Attendance
            att_total = Attendance.objects.filter(student=student).count()
            att_present = Attendance.objects.filter(student=student, status='PRESENT').count()
            att_pct = (att_present / att_total * 100) if att_total > 0 else 100

            from apps.fees.models import FeeInvoice
            invoices = FeeInvoice.objects.filter(student=student)
            total_balance = sum(inv.balance_due for inv in invoices)

            enrollment_details.append({
                'enrollment': enr,
                'avg_percentage': round(avg_pct, 1),
                'passed': all_passed,
                'attendance_pct': round(att_pct, 1),
                'fee_balance': total_balance,
                'suggested_status': 'PROMOTED' if (all_passed and avg_pct >= 40) else 'REPEATING'
            })

        context['enrollment_details'] = enrollment_details
        context['next_sessions'] = AcademicSession.objects.filter(is_active=True)
        return context


class PromoteStudentsView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    """
    Processes promotion for selected students into a new Academic Session.
    """
    model = Enrollment

    def test_func(self):
        return self.request.user.role == User.Role.ADMIN

    def handle_no_permission(self):
        return redirect('unauthorized')

    def post(self, request, *args, **kwargs):
        from django.db import transaction
        target_session_id = request.POST.get('target_session_id')
        target_session = AcademicSession.objects.filter(pk=target_session_id).first()
        if not target_session:
            messages.error(request, "Target Academic Session is required for promotion.")
            return redirect('session_closing')

        enrollment_ids = request.POST.getlist('enrollment_ids')
        promoted_count = 0

        with transaction.atomic():
            for enr_id in enrollment_ids:
                decision = request.POST.get(f'decision_{enr_id}', 'PROMOTED')
                old_enr = Enrollment.objects.filter(pk=enr_id).first()
                if not old_enr:
                    continue

                old_enr.is_active = False
                old_enr.status = decision
                old_enr.save()

                if decision == 'PROMOTED':
                    next_grade = (old_enr.school_class.numeric_grade or 1) + 1
                    target_class = Class.objects.filter(numeric_grade=next_grade).first() or old_enr.school_class
                else:
                    target_class = old_enr.school_class

                Enrollment.objects.create(
                    student=old_enr.student,
                    school_class=target_class,
                    section=old_enr.section,
                    academic_session=target_session,
                    academic_year=target_session.name,
                    roll_number=old_enr.roll_number,
                    status='ENROLLED',
                    is_active=True
                )

                old_enr.student.current_class = target_class
                old_enr.student.save()
                promoted_count += 1

        messages.success(request, f"Successfully processed promotion for {promoted_count} students into session {target_session.name}.")
        return redirect('session_closing')