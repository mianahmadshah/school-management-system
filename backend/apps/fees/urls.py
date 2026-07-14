"""
URL routes for fees module.
Includes both Web UI (template) routes and API routes.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    FeeCategoryViewSet, FeeStructureViewSet, FeeInvoiceViewSet, FeePaymentViewSet,
    FeeCategoryListView, FeeCategoryCreateView, FeeCategoryUpdateView, FeeCategoryDeleteView,
    FeeStructureListView, FeeStructureCreateView,
    FeeInvoiceListView, FeeInvoiceCreateView, FeeInvoiceDetailView,
    RecordPaymentView,
)

router = DefaultRouter()
router.register(r'categories', FeeCategoryViewSet, basename='fee-category')
router.register(r'structures', FeeStructureViewSet, basename='fee-structure')
router.register(r'invoices', FeeInvoiceViewSet, basename='fee-invoice')
router.register(r'payments', FeePaymentViewSet, basename='fee-payment')

urlpatterns = [
    # Fee Categories
    path('categories/', FeeCategoryListView.as_view(), name='fee_category_list'),
    path('categories/add/', FeeCategoryCreateView.as_view(), name='fee_category_create'),
    path('categories/<int:pk>/edit/', FeeCategoryUpdateView.as_view(), name='fee_category_update'),
    path('categories/<int:pk>/delete/', FeeCategoryDeleteView.as_view(), name='fee_category_delete'),

    # Fee Structures
    path('structures/', FeeStructureListView.as_view(), name='fee_structure_list'),
    path('structures/add/', FeeStructureCreateView.as_view(), name='fee_structure_create'),

    # Fee Invoices
    path('invoices/', FeeInvoiceListView.as_view(), name='invoice_list'),
    path('invoices/add/', FeeInvoiceCreateView.as_view(), name='invoice_create'),
    path('invoices/<int:pk>/', FeeInvoiceDetailView.as_view(), name='invoice_detail'),
    path('invoices/<int:pk>/pay/', RecordPaymentView.as_view(), name='record_payment'),
]

api_urlpatterns = [
    path('api/', include(router.urls)),
]