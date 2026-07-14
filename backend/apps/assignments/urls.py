"""
URL routes for assignments app.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    AssignmentViewSet, SubmissionViewSet,
    AssignmentListView, AssignmentDetailView, AssignmentCreateView, AssignmentUpdateView, AssignmentDeleteView,
    GradeSubmissionView,
)

router = DefaultRouter()
router.register(r'', AssignmentViewSet, basename='assignment')
router.register(r'submissions', SubmissionViewSet, basename='submission')

urlpatterns = [
    path('', AssignmentListView.as_view(), name='assignment_list'),
    path('add/', AssignmentCreateView.as_view(), name='assignment_create'),
    path('<int:pk>/', AssignmentDetailView.as_view(), name='assignment_detail'),
    path('<int:pk>/edit/', AssignmentUpdateView.as_view(), name='assignment_update'),
    path('<int:pk>/delete/', AssignmentDeleteView.as_view(), name='assignment_delete'),
    path('submissions/<int:pk>/grade/', GradeSubmissionView.as_view(), name='grade_submission'),
]

api_urlpatterns = [
    path('api/', include(router.urls)),
]