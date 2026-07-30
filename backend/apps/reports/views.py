"""
Views for the reports app.
"""
from django.urls import reverse_lazy
from django.shortcuts import redirect
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import ListView, FormView, TemplateView
from django.contrib.auth import get_user_model
from django.db.models import Count, Avg, Sum, Q
from django.utils import timezone
from datetime import timedelta

from .models import Report
from .forms import ReportFilterForm
from apps.classes.models import Class
from apps.attendance.models import Attendance
from apps.examinations.models import Result
from apps.fees.models import FeeInvoice
from apps.students.models import Student
from apps.teachers.models import Teacher

User = get_user_model()


class ReportDashboardView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    template_name = 'reports/dashboard.html'

    def test_func(self):
        return self.request.user.role == User.Role.ADMIN

    def handle_no_permission(self):
        return redirect('unauthorized')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Quick stats
        context['total_students'] = Student.objects.filter(status='ACTIVE').count()
        context['total_teachers'] = Teacher.objects.filter(status='ACTIVE').count()
        context['total_classes'] = Class.objects.filter(is_active=True).count()
        
        # Fee collection stats
        fee_agg = FeeInvoice.objects.aggregate(
            collected=Sum('amount_paid'),
            total=Sum('total_amount')
        )
        context['total_fee_collected'] = fee_agg['collected'] or 0
        context['total_fee_pending'] = (fee_agg['total'] or 0) - (fee_agg['collected'] or 0)
        
        # Attendance today
        today = timezone.now().date()
        context['attendance_today'] = Attendance.objects.filter(date=today).count()
        context['attendance_present'] = Attendance.objects.filter(date=today, status='PRESENT').count()
        
        # Exam results average
        context['avg_result'] = Result.objects.aggregate(avg=Avg('total_marks_obtained'))['avg'] or 0
        
        # Recent reports
        context['recent_reports'] = Report.objects.all()[:10]
        
        return context


class AttendanceReportView(LoginRequiredMixin, UserPassesTestMixin, FormView):
    template_name = 'reports/attendance_report.html'
    form_class = ReportFilterForm

    def test_func(self):
        return self.request.user.role == User.Role.ADMIN

    def handle_no_permission(self):
        return redirect('unauthorized')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        class_id = self.request.GET.get('class_id', '')
        from_date = self.request.GET.get('from_date', '')
        to_date = self.request.GET.get('to_date', '')
        
        qs = Attendance.objects.all().select_related('student', 'student__current_class')
        if class_id:
            qs = qs.filter(student__current_class_id=class_id)
        if from_date:
            qs = qs.filter(date__gte=from_date)
        if to_date:
            qs = qs.filter(date__lte=to_date)
        
        # Group by class
        classes = Class.objects.filter(is_active=True)
        # Use a single annotated query instead of N+1 loop
        from django.db.models import Case, When, IntegerField
        report_data = list(
            qs.values('student__current_class__name')
            .annotate(
                total=Count('id'),
                present=Count(Case(When(status='PRESENT', then=1), output_field=IntegerField())),
                absent=Count(Case(When(status='ABSENT', then=1), output_field=IntegerField())),
                late=Count(Case(When(status='LATE', then=1), output_field=IntegerField())),
                excused=Count(Case(When(status='EXCUSED', then=1), output_field=IntegerField())),
            )
            .order_by('student__current_class__name')
        )
        for item in report_data:
            item['class'] = item.pop('student__current_class__name')
            total = item['total']
            item['percentage'] = round((item['present'] / total * 100), 1) if total > 0 else 0
        
        context['report_data'] = report_data
        context['classes'] = classes
        return context


class AcademicReportView(LoginRequiredMixin, UserPassesTestMixin, FormView):
    template_name = 'reports/academic_report.html'
    form_class = ReportFilterForm

    def test_func(self):
        return self.request.user.role == User.Role.ADMIN

    def handle_no_permission(self):
        return redirect('unauthorized')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        class_id = self.request.GET.get('class_id', '')
        exam_id = self.request.GET.get('exam_id', '')
        
        qs = Result.objects.all().select_related('student', 'exam', 'student__current_class')
        if class_id:
            qs = qs.filter(student__current_class_id=class_id)
        if exam_id:
            qs = qs.filter(exam_id=exam_id)
        
        # Group by class
        classes = Class.objects.filter(is_active=True)
        from django.db.models import Max
        report_data = list(
            qs.values('student__current_class__name')
            .annotate(
                students_count=Count('id'),
                avg_marks=Avg('total_marks_obtained'),
                max_marks=Max('total_marks_obtained'),
            )
            .order_by('student__current_class__name')
        )
        for item in report_data:
            item['class'] = item.pop('student__current_class__name')
            item['avg_marks'] = round(item['avg_marks'] or 0, 1)
            item['max_marks'] = item['max_marks'] or 0
        
        context['report_data'] = report_data
        context['classes'] = classes
        return context


class FeeCollectionReportView(LoginRequiredMixin, UserPassesTestMixin, FormView):
    template_name = 'reports/fee_report.html'
    form_class = ReportFilterForm

    def test_func(self):
        return self.request.user.role == User.Role.ADMIN

    def handle_no_permission(self):
        return redirect('unauthorized')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        class_id = self.request.GET.get('class_id', '')
        from_date = self.request.GET.get('from_date', '')
        to_date = self.request.GET.get('to_date', '')
        
        qs = FeeInvoice.objects.all().select_related('student', 'student__current_class')
        if class_id:
            qs = qs.filter(student__current_class_id=class_id)
        if from_date:
            qs = qs.filter(issue_date__gte=from_date)
        if to_date:
            qs = qs.filter(issue_date__lte=to_date)
        
        # Group by class
        classes = Class.objects.filter(is_active=True)
        report_data = list(
            qs.values('student__current_class__name')
            .annotate(
                total_amount=Sum('total_amount'),
                total_paid=Sum('amount_paid'),
            )
            .order_by('student__current_class__name')
        )
        for item in report_data:
            item['class'] = item.pop('student__current_class__name')
            item['total_due'] = (item['total_amount'] or 0) - (item['total_paid'] or 0)
        
        context['report_data'] = report_data
        context['classes'] = classes
        return context