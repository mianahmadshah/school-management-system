"""
API Routers configuration for all ViewSets.

This file combines all routers from different apps and creates
a single DefaultRouter instance for URL generation.
"""
from rest_framework.routers import DefaultRouter

# Import all ViewSets
from apps.accounts.viewsets import UserViewSet
from apps.students.viewsets import StudentViewSet
from apps.teachers.viewsets import TeacherViewSet
from apps.classes.viewsets import ClassViewSet, SectionViewSet
from apps.subjects.viewsets import SubjectViewSet, EnrollmentViewSet
from apps.attendance.viewsets import AttendanceViewSet
from apps.examinations.viewsets import ExamViewSet, MarksViewSet, ResultViewSet
from apps.fees.viewsets import (
    FeeCategoryViewSet,
    FeeInvoiceViewSet, FeePaymentViewSet
)
from apps.announcements.viewsets import AnnouncementViewSet
from apps.assignments.viewsets import AssignmentViewSet, SubmissionViewSet
from apps.timetable.viewsets import PeriodViewSet, TimetableViewSet
from apps.activity_logs.viewsets import ActivityLogViewSet


# Create router instance
router = DefaultRouter()

# Register all ViewSets
# Accounts
router.register(r'users', UserViewSet, basename='user')

# Students
router.register(r'students', StudentViewSet, basename='student')

# Teachers
router.register(r'teachers', TeacherViewSet, basename='teacher')

# Classes
router.register(r'classes', ClassViewSet, basename='class')
router.register(r'sections', SectionViewSet, basename='section')

# Subjects & Enrollments
router.register(r'subjects', SubjectViewSet, basename='subject')
router.register(r'enrollments', EnrollmentViewSet, basename='enrollment')

# Attendance
router.register(r'attendance', AttendanceViewSet, basename='attendance')

# Examinations
router.register(r'exams', ExamViewSet, basename='exam')
router.register(r'marks', MarksViewSet, basename='marks')
router.register(r'results', ResultViewSet, basename='result')

# Fees
router.register(r'fees/categories', FeeCategoryViewSet, basename='fee-category')
router.register(r'fees/invoices', FeeInvoiceViewSet, basename='fee-invoice')
router.register(r'fees/payments', FeePaymentViewSet, basename='fee-payment')

# Announcements
router.register(r'announcements', AnnouncementViewSet, basename='announcement')

# Assignments
router.register(r'assignments', AssignmentViewSet, basename='assignment')
router.register(r'submissions', SubmissionViewSet, basename='submission')

# Timetable
router.register(r'periods', PeriodViewSet, basename='period')
router.register(r'timetable', TimetableViewSet, basename='timetable')

# Activity Logs
router.register(r'logs', ActivityLogViewSet, basename='activitylog')


# Export
__all__ = ['router']
