from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import SubjectViewSet, EnrollmentViewSet

router = DefaultRouter()
router.register(r'subjects', SubjectViewSet, basename='subject')
router.register(r'enrollments', EnrollmentViewSet, basename='enrollment')

urlpatterns = [
    path('', include(router.urls)),
]
