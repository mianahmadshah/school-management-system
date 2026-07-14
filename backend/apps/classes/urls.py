"""
URL routes for classes and sections.
Includes both Web UI (template) routes and API routes.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    ClassViewSet, SectionViewSet,
    ClassListView, ClassDetailView, ClassCreateView, ClassUpdateView, ClassDeleteView,
    SectionCreateView, SectionUpdateView, SectionDeleteView,
)

router = DefaultRouter()
router.register(r'', ClassViewSet, basename='class')
router.register(r'sections', SectionViewSet, basename='section')

# Web UI URL patterns
urlpatterns = [
    # Class Web UI
    path('', ClassListView.as_view(), name='class_list'),
    path('add/', ClassCreateView.as_view(), name='class_create'),
    path('<int:pk>/', ClassDetailView.as_view(), name='class_detail'),
    path('<int:pk>/edit/', ClassUpdateView.as_view(), name='class_update'),
    path('<int:pk>/delete/', ClassDeleteView.as_view(), name='class_delete'),
    
    # Section Web UI
    path('sections/add/', SectionCreateView.as_view(), name='section_create'),
    path('sections/<int:pk>/edit/', SectionUpdateView.as_view(), name='section_update'),
    path('sections/<int:pk>/delete/', SectionDeleteView.as_view(), name='section_delete'),
]

# API URL patterns
api_urlpatterns = [
    path('api/', include(router.urls)),
]