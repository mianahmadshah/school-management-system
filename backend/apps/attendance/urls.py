"""
URL routes for attendance.
Includes both Web UI (template) routes and API routes.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    AttendanceViewSet,
    AttendanceListView,
    MarkAttendanceView,
    StudentAttendanceView,
)

router = DefaultRouter()
router.register(r'', AttendanceViewSet, basename='attendance')

# Web UI URL patterns
urlpatterns = [
    # Admin/Teacher Attendance Views
    path('', AttendanceListView.as_view(), name='attendance_list'),
    path('mark/', MarkAttendanceView.as_view(), name='mark_attendance'),
    
    # Student View
    path('my-attendance/', StudentAttendanceView.as_view(), name='my_attendance'),
]

# API URL patterns
api_urlpatterns = [
    path('api/', include(router.urls)),
]