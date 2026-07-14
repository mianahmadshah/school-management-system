"""
URL routes for the students app.
Includes both:
1. Template-based Web UI views
2. REST API routes (DRF)
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import StudentViewSet, StudentListView, StudentDetailView, StudentCreateView, StudentUpdateView, StudentDeleteView

router = DefaultRouter()
router.register(r'', StudentViewSet, basename='student')

urlpatterns = [
    # Web UI Views
    path('', StudentListView.as_view(), name='student_list'),
    path('create/', StudentCreateView.as_view(), name='student_create'),
    path('<int:pk>/', StudentDetailView.as_view(), name='student_detail'),
    path('<int:pk>/update/', StudentUpdateView.as_view(), name='student_update'),
    path('<int:pk>/delete/', StudentDeleteView.as_view(), name='student_delete'),
    
    # REST API
    path('api/', include(router.urls)),
]
