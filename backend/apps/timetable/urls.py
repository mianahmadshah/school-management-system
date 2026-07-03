from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PeriodViewSet, TimetableViewSet

router = DefaultRouter()
router.register(r'periods', PeriodViewSet, basename='period')
router.register(r'schedule', TimetableViewSet, basename='schedule')

urlpatterns = [
    path('', include(router.urls)),
]
