"""
URL routes for timetable app.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    PeriodViewSet, TimetableViewSet,
    PeriodListView, PeriodCreateView, PeriodUpdateView, PeriodDeleteView,
    TimetableListView, TimetableCreateView, TimetableUpdateView, TimetableDeleteView,
    StudentTimetableView, TeacherTimetableView,
)

router = DefaultRouter()
router.register(r'periods', PeriodViewSet, basename='period')
router.register(r'', TimetableViewSet, basename='timetable')

urlpatterns = [
    # Periods
    path('periods/', PeriodListView.as_view(), name='period_list'),
    path('periods/add/', PeriodCreateView.as_view(), name='period_create'),
    path('periods/<int:pk>/edit/', PeriodUpdateView.as_view(), name='period_update'),
    path('periods/<int:pk>/delete/', PeriodDeleteView.as_view(), name='period_delete'),

    # Timetable entries
    path('', TimetableListView.as_view(), name='timetable_list'),
    path('add/', TimetableCreateView.as_view(), name='timetable_create'),
    path('<int:pk>/edit/', TimetableUpdateView.as_view(), name='timetable_update'),
    path('<int:pk>/delete/', TimetableDeleteView.as_view(), name='timetable_delete'),

    # Role-specific views
    path('student/my-timetable/', StudentTimetableView.as_view(), name='my_timetable'),
    path('teacher/my-timetable/', TeacherTimetableView.as_view(), name='teacher_timetable'),
]

api_urlpatterns = [
    path('api/', include(router.urls)),
]