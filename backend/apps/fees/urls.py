from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import FeeCategoryViewSet, FeeInvoiceViewSet, FeePaymentViewSet

router = DefaultRouter()
router.register(r'categories', FeeCategoryViewSet, basename='fee_category')
router.register(r'invoices', FeeInvoiceViewSet, basename='fee_invoice')
router.register(r'payments', FeePaymentViewSet, basename='fee_payment')

urlpatterns = [
    path('', include(router.urls)),
]
