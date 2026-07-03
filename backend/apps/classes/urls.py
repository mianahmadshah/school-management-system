"""
URL routes for classes and sections.
Both use separate routers but are both mounted at /api/v1/classes/
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ClassViewSet, SectionViewSet

router = DefaultRouter()
# Class routes:   /api/v1/classes/
router.register(r'', ClassViewSet, basename='class')
# Section routes: /api/v1/classes/sections/
router.register(r'sections', SectionViewSet, basename='section')

urlpatterns = [
    path('', include(router.urls)),
]
