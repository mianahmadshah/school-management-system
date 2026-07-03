"""
ViewSets for Fee management.
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

from apps.fees.models import FeeCategory, FeeInvoice, FeePayment
from apps.fees.serializers import (
    FeeCategorySerializer, 
    FeeInvoiceSerializer, FeePaymentSerializer
)
from apps.accounts.permissions import IsAdminUser
from api.v1.pagination import StandardResultsSetPagination


class FeeCategoryViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Fee Category management.
    
    Endpoints:
    - GET    /api/v1/fees/categories/         - List categories
    - POST   /api/v1/fees/categories/         - Create category (admin only)
    - GET    /api/v1/fees/categories/{id}/    - Get category details
    - PUT    /api/v1/fees/categories/{id}/    - Update category (admin only)
    - DELETE /api/v1/fees/categories/{id}/    - Delete category (admin only)
    """
    queryset = FeeCategory.objects.all()
    serializer_class = FeeCategorySerializer
    pagination_class = StandardResultsSetPagination
    
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['name']
    ordering = ['name']
    
    def get_permissions(self):
        """Override permissions per action."""
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes = [IsAdminUser]
        else:
            permission_classes = [IsAuthenticated]
        
        return [permission() for permission in permission_classes]


class FeeInvoiceViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Fee Invoice management.
    
    Endpoints:
    - GET    /api/v1/fees/invoices/         - List invoices
    - POST   /api/v1/fees/invoices/         - Create invoice (admin only)
    - GET    /api/v1/fees/invoices/{id}/    - Get invoice details
    - PUT    /api/v1/fees/invoices/{id}/    - Update invoice (admin only)
    """
    queryset = FeeInvoice.objects.select_related('student').all()
    serializer_class = FeeInvoiceSerializer
    pagination_class = StandardResultsSetPagination
    
    filter_backends = [
        DjangoFilterBackend,
        SearchFilter,
        OrderingFilter
    ]
    filterset_fields = ['status', 'academic_year']
    search_fields = ['student__user__first_name', 'student__user__last_name', 'invoice_number']
    ordering_fields = ['due_date', 'invoice_date']
    ordering = ['-invoice_date']
    
    def get_permissions(self):
        """Override permissions per action."""
        if self.action in ['create', 'update', 'partial_update']:
            permission_classes = [IsAdminUser]
        else:
            permission_classes = [IsAuthenticated]
        
        return [permission() for permission in permission_classes]
    
    @action(detail=False, methods=['get'])
    def overdue(self, request):
        """Get overdue invoices."""
        from datetime import date
        overdue_invoices = FeeInvoice.objects.filter(
            status='PENDING',
            due_date__lt=date.today()
        )
        
        serializer = FeeInvoiceSerializer(overdue_invoices, many=True)
        return Response({
            'count': overdue_invoices.count(),
            'results': serializer.data
        })
    
    @action(detail=True, methods=['get'])
    def student_invoices(self, request, pk=None):
        """Get all invoices for a student."""
        invoice = self.get_object()
        student_invoices = FeeInvoice.objects.filter(student=invoice.student)
        
        serializer = FeeInvoiceSerializer(student_invoices, many=True)
        return Response({
            'student': str(invoice.student),
            'count': student_invoices.count(),
            'results': serializer.data
        })


class FeePaymentViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Fee Payment management.
    
    Endpoints:
    - GET    /api/v1/fees/payments/         - List payments
    - POST   /api/v1/fees/payments/         - Record payment (admin only)
    - GET    /api/v1/fees/payments/{id}/    - Get payment details
    """
    queryset = FeePayment.objects.select_related(
        'invoice', 'collected_by'
    ).all()
    serializer_class = FeePaymentSerializer
    pagination_class = StandardResultsSetPagination
    
    filter_backends = [
        DjangoFilterBackend,
        SearchFilter,
        OrderingFilter
    ]
    filterset_fields = ['payment_method', 'payment_date']
    search_fields = ['invoice__student__user__first_name', 'transaction_id']
    ordering_fields = ['payment_date', 'amount']
    ordering = ['-payment_date']
    
    def get_permissions(self):
        """Override permissions per action."""
        if self.action in ['create']:
            permission_classes = [IsAdminUser]
        else:
            permission_classes = [IsAuthenticated]
        
        return [permission() for permission in permission_classes]
    
    @action(detail=False, methods=['get'])
    def report(self, request):
        """Get payment summary report."""
        from django.db.models import Sum
        
        total_payments = FeePayment.objects.aggregate(total=Sum('amount'))['total'] or 0
        payment_count = FeePayment.objects.count()
        
        # By payment method
        by_method = FeePayment.objects.values('payment_method').annotate(
            count=Sum('amount')
        )
        
        return Response({
            'summary': {
                'total_payments': float(total_payments),
                'total_transactions': payment_count,
                'average_payment': float(total_payments / payment_count) if payment_count > 0 else 0
            },
            'by_method': by_method
        })
