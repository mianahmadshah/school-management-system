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
        context['total_students'] = Student.objects.filter(is_active=True).count()
        context['total_teachers'] = Teacher.objects.filter(is_active=True).count()
        context['total_classes'] = Class.objects.filter(is_active=True).count()
        
        # Fee collection stats
        invoices = FeeInvoice.objects.all()
        context['total_fee_collected'] = sum(inv.amount_paid for inv in invoices)
        context['total_fee_pending'] = sum(inv.balance_due for inv in invoices)
        
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
        report_data = []
        for cls in classes:
            class_attendance = qs.filter(student__current_class=cls)
            total = class_attendance.count()
            present = class_attendance.filter(status='PRESENT').count()
            absent = class_attendance.filter(status='ABSENT').count()
            late = class_attendance.filter(status='LATE').count()
            excused = class_attendance.filter(status='EXCUSED').count()
            
            percentage = (present / total * 100) if total > 0 else 0
            
            report_data.append({
                'class': cls.name,
                'total': total,
                'present': present,
                'absent': absent,
                'late': late,
                'excused': excused,
                'percentage': round(percentage, 1)
            })
        
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
        report_data = []
        for cls in classes:
            class_results = qs.filter(student__current_class=cls)
            count = class_results.count()
            avg_marks = class_results.aggregate(avg=Avg('total_marks_obtained'))['avg'] or 0
            max_marks = class_results.aggregate(max=Sum('total_marks_obtained'))['max'] or 0
            
            report_data.append({
                'class': cls.name,
                'students_count': count,
                'avg_marks': round(avg_marks, 1),
                'max_marks': max_marks
            })
        
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
        report_data = []
        for cls in classes:
            class_invoices = qs.filter(student__current_class=cls)
            total_amount = sum(inv.total_amount for inv in class_invoices)
            total_paid = sum(inv.amount_paid for inv in class_invoices)
            total_due = sum(inv.balance_due for inv in class_invoices)
            
            report_data.append({
                'class': cls.name,
                'total_amount': total_amount,
                'total_paid': total_paid,
                'total_due': total_due
            })
        
        context['report_data'] = report_data
        context['classes'] = classes
        return context