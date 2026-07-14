"""
URL routes for examinations, marks, and results.
Includes both Web UI and API routes.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    ExamViewSet, MarksViewSet, ResultViewSet,
    ExamListView, ExamDetailView, ExamCreateView, ExamUpdateView, ExamDeleteView,
    MarksEntryView, MarksListView,
    ResultListView, GenerateResultView, StudentResultView,
)

router = DefaultRouter()
router.register(r'', ExamViewSet, basename='exam')
router.register(r'marks', MarksViewSet, basename='marks')
router.register(r'results', ResultViewSet, basename='result')

# Web UI URL patterns
urlpatterns = [
    # Exams
    path('', ExamListView.as_view(), name='exam_list'),
    path('add/', ExamCreateView.as_view(), name='exam_create'),
    path('<int:pk>/', ExamDetailView.as_view(), name='exam_detail'),
    path('<int:pk>/edit/', ExamUpdateView.as_view(), name='exam_update'),
    path('<int:pk>/delete/', ExamDeleteView.as_view(), name='exam_delete'),
    
    # Marks
    path('marks/entry/', MarksEntryView.as_view(), name='marks_entry'),
    path('marks/', MarksListView.as_view(), name='marks_list'),
    
    # Results
    path('results/', ResultListView.as_view(), name='result_list'),
    path('results/generate/', GenerateResultView.as_view(), name='generate_result'),
    path('results/my-results/', StudentResultView.as_view(), name='my_results'),
]

api_urlpatterns = [
    path('api/', include(router.urls)),
]