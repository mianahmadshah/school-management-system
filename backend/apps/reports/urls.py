"""
URL routes for reports app.
"""
from django.urls import path
from .views import (
    ReportDashboardView,
    AttendanceReportView,
    AcademicReportView,
    FeeCollectionReportView,
)

urlpatterns = [
    path('', ReportDashboardView.as_view(), name='report_dashboard'),
    path('attendance/', AttendanceReportView.as_view(), name='report_attendance'),
    path('academic/', AcademicReportView.as_view(), name='report_academic'),
    path('fees/', FeeCollectionReportView.as_view(), name='report_fees'),
]