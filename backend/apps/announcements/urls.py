"""
URL routes for announcements app.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    AnnouncementViewSet,
    AnnouncementListView,
    AnnouncementDetailView,
    AnnouncementCreateView,
    AnnouncementUpdateView,
    AnnouncementDeleteView,
)

router = DefaultRouter()
router.register(r'', AnnouncementViewSet, basename='announcement')

urlpatterns = [
    path('', AnnouncementListView.as_view(), name='announcement_list'),
    path('add/', AnnouncementCreateView.as_view(), name='announcement_create'),
    path('<int:pk>/', AnnouncementDetailView.as_view(), name='announcement_detail'),
    path('<int:pk>/edit/', AnnouncementUpdateView.as_view(), name='announcement_update'),
    path('<int:pk>/delete/', AnnouncementDeleteView.as_view(), name='announcement_delete'),
]

api_urlpatterns = [
    path('api/', include(router.urls)),
]