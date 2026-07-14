"""
Views for the attendance app.
Provides both Web UI templates and API views.
"""
from django.urls import reverse_lazy
from django.shortcuts import redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView, FormView
from django.contrib.auth import get_user_model
from django.db.models import Q
import datetime

from .models import Attendance
from .forms import AttendanceForm, BulkAttendanceForm
from apps.students.models import Student
from apps.classes.models import Class, Section

# DRF imports for API
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend

from .serializers import AttendanceSerializer, BulkAttendanceSerializer
from apps.accounts.permissions import IsAdminUser, IsAdminOrTeacher

User = get_user_model()


# ─────────────────────────────────────────────────────────────
# TEMPLATE-BASED VIEWS (Web UI)
# ─────────────────────────────────────────────────────────────

class AttendanceListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    """Renders list of attendance records."""
    model = Attendance
    template_name = 'attendance/attendance_list.html'
    context_object_name = 'records'
    paginate_by = 20

    def test_func(self):
        return self.request.user.role in [User.Role.ADMIN, User.Role.TEACHER]

    def handle_no_permission(self):
        return redirect('unauthorized')

    def get_queryset(self):
        queryset = Attendance.objects.select_related('student__user', 'school_class', 'section', 'marked_by')
        
        # Filter by date
        date = self.request.GET.get('date', '')
        if date:
            queryset = queryset.filter(date=date)
        else:
            queryset = queryset.filter(date=datetime.date.today())
        
        # Filter by class
        class_id = self.request.GET.get('class_id', '')
        if class_id:
            queryset = queryset.filter(school_class_id=class_id)
        
        # Filter by section
        section_id = self.request.GET.get('section_id', '')
        if section_id:
            queryset = queryset.filter(section_id=section_id)
        
        # Filter by status
        status_filter = self.request.GET.get('status', '')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['classes'] = Class.objects.filter(is_active=True)
        context['sections'] = Section.objects.filter(is_active=True)
        context['today'] = datetime.date.today()
        return context


class StudentAttendanceView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    """Student views their own attendance records."""
    model = Attendance
    template_name = 'attendance/my_attendance.html'
    context_object_name = 'records'
    paginate_by = 30

    def test_func(self):
        return self.request.user.role == User.Role.STUDENT

    def handle_no_permission(self):
        return redirect('unauthorized')

    def get_queryset(self):
        student = getattr(self.request.user, 'student_profile', None)
        if not student:
            return Attendance.objects.none()
        
        queryset = Attendance.objects.filter(student=student).select_related('school_class', 'section')
        
        # Filter by date range
        from_date = self.request.GET.get('from_date', '')
        to_date = self.request.GET.get('to_date', '')
        if from_date:
            queryset = queryset.filter(date__gte=from_date)
        if to_date:
            queryset = queryset.filter(date__lte=to_date)
        
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        student = getattr(self.request.user, 'student_profile', None)
        if student:
            total = self.object_list.count()
            present = self.object_list.filter(status='PRESENT').count()
            context['attendance_percentage'] = f"{int((present / total) * 100)}%" if total > 0 else "N/A"
        return context


class MarkAttendanceView(LoginRequiredMixin, UserPassesTestMixin, FormView):
    """Mark attendance for a class/section on a specific date."""
    template_name = 'attendance/mark_attendance.html'
    form_class = BulkAttendanceForm
    success_url = reverse_lazy('attendance_list')

    def test_func(self):
        return self.request.user.role in [User.Role.ADMIN, User.Role.TEACHER]

    def handle_no_permission(self):
        return redirect('unauthorized')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['classes'] = Class.objects.filter(is_active=True)
        context['today'] = datetime.date.today()
        
        # If class and section selected, load students
        class_id = self.request.GET.get('class_id', '')
        section_id = self.request.GET.get('section_id', '')
        date = self.request.GET.get('date', datetime.date.today().isoformat())
        
        context['selected_class'] = class_id
        context['selected_section'] = section_id
        context['selected_date'] = date
        
        if class_id and section_id:
            students = Student.objects.filter(
                current_class_id=class_id, section_id=section_id, status='ACTIVE'
            ).select_related('user').order_by('roll_number', 'user__first_name')
            
            # Check which students already have attendance for this date
            existing = Attendance.objects.filter(
                date=date, school_class_id=class_id, section_id=section_id
            ).values_list('student_id', flat=True)
            
            context['students'] = students
            context['existing_ids'] = list(existing)
        
        return context

    def form_valid(self, form):
        records = form.save(commit=False)
        marked_by = self.request.user
        count = 0
        for record in records:
            record.marked_by = marked_by
            record.save()
            count += 1
        messages.success(self.request, f'Attendance marked for {count} student(s).')
        return redirect(self.success_url)


# ─────────────────────────────────────────────────────────────
# DRF VIEWSETS (API) — Keep existing API code intact
# ─────────────────────────────────────────────────────────────

class AttendanceViewSet(viewsets.ModelViewSet):
    """CRUD ViewSet for Attendance."""
    serializer_class = AttendanceSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['student__user__first_name', 'student__user__last_name', 'student__admission_number']
    filterset_fields = ['school_class', 'section', 'date', 'status', 'student']
    ordering_fields = ['date', 'student__user__first_name']
    ordering = ['-date', 'school_class', 'section', 'student__user__first_name']

    def get_permissions(self):
        return [IsAuthenticated()]

    def get_queryset(self):
        user = self.request.user
        qs = Attendance.objects.select_related('student__user', 'school_class', 'section', 'marked_by')
        if user.is_student:
            return qs.filter(student__user=user)
        return qs.all()

    def create(self, request, *args, **kwargs):
        if not (request.user.is_admin or request.user.is_teacher):
            return Response({"detail": "You do not have permission to mark attendance."}, status=status.HTTP_403_FORBIDDEN)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(marked_by=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        if not (request.user.is_admin or request.user.is_teacher):
            return Response({"detail": "Forbidden."}, status=status.HTTP_403_FORBIDDEN)
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        if not request.user.is_admin:
            return Response({"detail": "Only admins can delete attendance records."}, status=status.HTTP_403_FORBIDDEN)
        return super().destroy(request, *args, **kwargs)

    @action(detail=False, methods=['post'], permission_classes=[IsAdminOrTeacher])
    def bulk_mark(self, request):
        serializer = BulkAttendanceSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        result = serializer.save()
        return Response({"message": "Attendance marked successfully.", "details": result}, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'], permission_classes=[IsAdminOrTeacher])
    def today_stats(self, request):
        today = datetime.date.today()
        qs = Attendance.objects.filter(date=today)
        total_marked = qs.count()
        present = qs.filter(status='PRESENT').count()
        absent = qs.filter(status='ABSENT').count()
        late = qs.filter(status='LATE').count()
        half_day = qs.filter(status='HALF_DAY').count()
        on_leave = qs.filter(status='LEAVE').count()
        return Response({
            "date": today, "total_marked": total_marked, "present": present,
            "absent": absent, "late": late, "half_day": half_day, "on_leave": on_leave
        })