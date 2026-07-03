"""
Views for the fees and finance app.
"""
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Sum

from .models import FeeCategory, FeeInvoice, FeePayment
from .serializers import (
    FeeCategorySerializer, FeeInvoiceSerializer, 
    FeePaymentSerializer, BulkInvoiceSerializer
)
from apps.accounts.permissions import IsAdminUser
from apps.activity_logs.models import ActivityLog


class FeeCategoryViewSet(viewsets.ModelViewSet):
    """CRUD ViewSet for Fee Categories."""
    queryset = FeeCategory.objects.all()
    serializer_class = FeeCategorySerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name']
    ordering = ['name']

    def get_permissions(self):
        # Only admins manage fee categories
        if self.action in ['list', 'retrieve']:
            return [IsAuthenticated()]
        return [IsAdminUser()]


class FeeInvoiceViewSet(viewsets.ModelViewSet):
    """CRUD ViewSet for Fee Invoices."""
    serializer_class = FeeInvoiceSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['invoice_number', 'student__user__first_name', 'student__user__last_name', 'student__admission_number']
    filterset_fields = ['category', 'status', 'student']
    ordering_fields = ['issue_date', 'due_date', 'status']
    ordering = ['-issue_date']

    def get_queryset(self):
        qs = FeeInvoice.objects.select_related('student__user', 'category').prefetch_related('payments')
        user = self.request.user
        
        # Students see only their own invoices
        if user.is_student:
            return qs.filter(student__user=user)
        # Teachers shouldn't really see finances unless explicitly allowed, but we'll assume Admins only
        if not user.is_admin:
            # Maybe return none for teachers
            return qs.none()
        return qs.all()

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy', 'bulk_generate']:
            return [IsAdminUser()]
        return [IsAuthenticated()]

    @action(detail=False, methods=['post'], permission_classes=[IsAdminUser])
    def bulk_generate(self, request):
        """
        POST /api/v1/fees/invoices/bulk_generate/
        Generate invoices for an entire class.
        """
        serializer = BulkInvoiceSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        result = serializer.save()
        return Response({
            "message": "Invoices generated successfully.",
            "details": result
        }, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['get'], permission_classes=[IsAdminUser])
    def stats(self, request):
        """Dashboard statistics for fees."""
        total_invoices = FeeInvoice.objects.count()
        paid_invoices = FeeInvoice.objects.filter(status='PAID').count()
        unpaid_invoices = FeeInvoice.objects.filter(status='UNPAID').count()
        
        agg = FeeInvoice.objects.aggregate(
            total_expected=Sum('total_amount'),
            total_collected=Sum('amount_paid')
        )
        
        expected = agg['total_expected'] or 0
        collected = agg['total_collected'] or 0
        balance = expected - collected

        return Response({
            "total_invoices": total_invoices,
            "paid_invoices": paid_invoices,
            "unpaid_invoices": unpaid_invoices,
            "total_expected": expected,
            "total_collected": collected,
            "total_outstanding": balance,
        })


class FeePaymentViewSet(viewsets.ModelViewSet):
    """CRUD ViewSet for Fee Payments."""
    serializer_class = FeePaymentSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['invoice__invoice_number', 'reference_number']
    filterset_fields = ['payment_method', 'invoice']
    ordering_fields = ['payment_date', 'amount']
    ordering = ['-payment_date']

    def get_queryset(self):
        qs = FeePayment.objects.select_related('invoice', 'collected_by')
        user = self.request.user
        if user.is_student:
            return qs.filter(invoice__student__user=user)
        if not user.is_admin:
            return qs.none()
        return qs.all()

    def get_permissions(self):
        # Only admins can create/update/delete payments
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAdminUser()]
        return [IsAuthenticated()]

    def create(self, request, *args, **kwargs):
        """Override create to assign collected_by"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Check if amount exceeds balance
        invoice = serializer.validated_data['invoice']
        amount = serializer.validated_data['amount']
        
        if amount > invoice.balance_due:
            return Response(
                {"error": f"Payment amount ({amount}) exceeds the invoice balance due ({invoice.balance_due})."},
                status=status.HTTP_400_BAD_REQUEST
            )

        payment = serializer.save(collected_by=request.user)
        
        # Log the payment activity
        ActivityLog.log(
            user=request.user,
            action=ActivityLog.ActionType.PAYMENT,
            model_name='FeePayment',
            object_id=payment.id,
            description=f"Collected payment of {amount} for Invoice {invoice.invoice_number}",
            request=request
        )
        
        return Response(serializer.data, status=status.HTTP_201_CREATED)
