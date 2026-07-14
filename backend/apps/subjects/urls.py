"""
URL routes for subjects and enrollments.
Includes both Web UI (template) routes and API routes.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    SubjectViewSet, EnrollmentViewSet,
    SubjectListView, SubjectDetailView, SubjectCreateView, SubjectUpdateView, SubjectDeleteView,
    EnrollmentCreateView,
)

router = DefaultRouter()
router.register(r'', SubjectViewSet, basename='subject')
router.register(r'enrollments', EnrollmentViewSet, basename='enrollment')

# Web UI URL patterns
urlpatterns = [
    # Subject Web UI
    path('', SubjectListView.as_view(), name='subject_list'),
    path('add/', SubjectCreateView.as_view(), name='subject_create'),
    path('<int:pk>/', SubjectDetailView.as_view(), name='subject_detail'),
    path('<int:pk>/edit/', SubjectUpdateView.as_view(), name='subject_update'),
    path('<int:pk>/delete/', SubjectDeleteView.as_view(), name='subject_delete'),
    
    # Enrollment Web UI
    path('enrollments/add/', EnrollmentCreateView.as_view(), name='enrollment_create'),
]

# API URL patterns
api_urlpatterns = [
    path('api/', include(router.urls)),
]