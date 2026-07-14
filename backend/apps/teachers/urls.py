"""
URL routes for the teachers app.
Includes both:
1. Template-based Web UI views
2. REST API routes (DRF)
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import TeacherViewSet, TeacherListView, TeacherDetailView, TeacherCreateView, TeacherUpdateView, TeacherDeleteView

router = DefaultRouter()
router.register(r'', TeacherViewSet, basename='teacher')

urlpatterns = [
    # Web UI Views
    path('', TeacherListView.as_view(), name='teacher_list'),
    path('create/', TeacherCreateView.as_view(), name='teacher_create'),
    path('<int:pk>/', TeacherDetailView.as_view(), name='teacher_detail'),
    path('<int:pk>/update/', TeacherUpdateView.as_view(), name='teacher_update'),
    path('<int:pk>/delete/', TeacherDeleteView.as_view(), name='teacher_delete'),
    
    # REST API
    path('api/', include(router.urls)),
]
