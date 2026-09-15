"""
Views for the fees app.
Provides Web UI templates and API views.
"""
from django.urls import reverse_lazy
from django.shortcuts import redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, FormView, TemplateView
from django.contrib.auth import get_user_model
from django.db.models import Sum, Q
from django.utils import timezone

from .models import FeeCategory, FeeStructure, FeeInvoice, FeePayment
from .forms import FeeCategoryForm, FeeStructureForm, FeeInvoiceForm, FeePaymentForm
from apps.classes.models import Class
from apps.students.models import Student
from apps.accounts.permissions import IsAdminUser, IsAdminOrTeacher
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from .serializers import FeeCategorySerializer, FeeStructureSerializer, FeeInvoiceSerializer, FeePaymentSerializer

User = get_user_model()


# ─────────────────────────────────────────────────────────────
# Web UI Views — Fee Categories
# ─────────────────────────────────────────────────────────────

class FeeCategoryListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = FeeCategory
    template_name = 'fees/fee_category_list.html'
    context_object_name = 'categories'
    paginate_by = 15

    def test_func(self):
        return self.request.user.role == User.Role.ADMIN

    def handle_no_permission(self):
        return redirect('unauthorized')

    def get_queryset(self):
        q = self.request.GET.get('q', '')
        qs = FeeCategory.objects.filter(is_active=True)
        if q:
            qs = qs.filter(Q(name__icontains=q) | Q(code__icontains=q))
        return qs


class FeeCategoryCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = FeeCategory
    form_class = FeeCategoryForm
    template_name = 'fees/fee_category_form.html'
    success_url = reverse_lazy('fee_category_list')

    def test_func(self):
        return self.request.user.role == User.Role.ADMIN

    def handle_no_permission(self):
        return redirect('unauthorized')

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, f'Fee category "{self.object.name}" created.')
        return response


class FeeCategoryUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = FeeCategory
    form_class = FeeCategoryForm
    template_name = 'fees/fee_category_form.html'
    success_url = reverse_lazy('fee_category_list')

    def test_func(self):
        return self.request.user.role == User.Role.ADMIN

    def handle_no_permission(self):
        return redirect('unauthorized')

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, f'Fee category "{self.object.name}" updated.')
        return response


class FeeCategoryDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = FeeCategory
    template_name = 'fees/fee_category_confirm_delete.html'
    success_url = reverse_lazy('fee_category_list')

    def test_func(self):
        return self.request.user.role == User.Role.ADMIN

    def handle_no_permission(self):
        return redirect('unauthorized')


# ─────────────────────────────────────────────────────────────
# Web UI — Fee Structures
# ─────────────────────────────────────────────────────────────

class FeeStructureListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = FeeStructure
    template_name = 'fees/fee_structure_list.html'
    context_object_name = 'structures'
    paginate_by = 15

    def test_func(self):
        return self.request.user.role == User.Role.ADMIN

    def handle_no_permission(self):
        return redirect('unauthorized')

    def get_queryset(self):
        qs = FeeStructure.objects.filter(is_active=True).select_related('school_class', 'category').order_by('school_class_id', 'id')
        class_id = self.request.GET.get('class_id', '')
        if class_id:
            qs = qs.filter(school_class_id=class_id)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['classes'] = Class.objects.filter(is_active=True)
        return context


class FeeStructureCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = FeeStructure
    form_class = FeeStructureForm
    template_name = 'fees/fee_structure_form.html'
    success_url = reverse_lazy('fee_structure_list')

    def test_func(self):
        return self.request.user.role == User.Role.ADMIN

    def handle_no_permission(self):
        return redirect('unauthorized')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['classes'] = Class.objects.filter(is_active=True)
        return context

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Fee structure added.')
        return response


# ─────────────────────────────────────────────────────────────
# Web UI — Fee Invoices
# ─────────────────────────────────────────────────────────────

class FeeInvoiceListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = FeeInvoice
    template_name = 'fees/invoice_list.html'
    context_object_name = 'invoices'
    paginate_by = 20

    def test_func(self):
        return self.request.user.role in [User.Role.ADMIN, User.Role.TEACHER, User.Role.STUDENT]

    def handle_no_permission(self):
        return redirect('unauthorized')

    def get_queryset(self):
        qs = FeeInvoice.objects.select_related('student__user', 'student__current_class', 'academic_session').prefetch_related('items')
        user = self.request.user
        if user.is_student:
            student = getattr(user, 'student_profile', None)
            if student:
                qs = qs.filter(student=student)
        
        # Student filter
        student_id = self.request.GET.get('student_id', '')
        if student_id:
            qs = qs.filter(student_id=student_id)
            
        # Class filter
        class_id = self.request.GET.get('class_id', '')
        if class_id:
            qs = qs.filter(student__current_class_id=class_id)
            
        # Status filter
        status = self.request.GET.get('status', '')
        if status:
            qs = qs.filter(status=status)
            
        # Search query (student name or admission number)
        q = self.request.GET.get('q', '').strip()
        if q:
            qs = qs.filter(
                Q(student__user__first_name__icontains=q) |
                Q(student__user__last_name__icontains=q) |
                Q(student__admission_number__icontains=q) |
                Q(invoice_number__icontains=q)
            )
        return qs.order_by('-issue_date', '-id')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
        # Calculate totals for the current filtered queryset (without pagination)
        filtered_qs = self.get_queryset()
        totals = filtered_qs.aggregate(
            total_invoiced=Sum('total_amount'),
            total_collected=Sum('amount_paid'),
        )
        total_invoiced = totals['total_invoiced'] or 0
        total_collected = totals['total_collected'] or 0
        balance_due = max(0, total_invoiced - total_collected)
        
        context['kpi_total_invoiced'] = total_invoiced
        context['kpi_total_collected'] = total_collected
        context['kpi_balance_due'] = balance_due
        context['kpi_unpaid_count'] = filtered_qs.filter(status__in=['UNPAID', 'PARTIAL']).count()
        context['kpi_paid_count'] = filtered_qs.filter(status='PAID').count()
        
        if user.role != User.Role.STUDENT:
            context['students'] = Student.objects.filter(status='ACTIVE').select_related('user').order_by('user__first_name')
            context['classes'] = Class.objects.filter(is_active=True).order_by('name')
        
        # Preserve query string for pagination
        query_params = self.request.GET.copy()
        if 'page' in query_params:
            query_params.pop('page')
        context['query_params'] = query_params.urlencode()
        return context


class FeeInvoiceCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = FeeInvoice
    form_class = FeeInvoiceForm
    template_name = 'fees/invoice_form.html'
    success_url = reverse_lazy('invoice_list')

    def test_func(self):
        return self.request.user.role == User.Role.ADMIN

    def handle_no_permission(self):
        return redirect('unauthorized')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['students'] = Student.objects.filter(status='ACTIVE').select_related('user')
        return context

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, f'Invoice {self.object.invoice_number} created.')
        return response


class FeeInvoiceDetailView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    model = FeeInvoice
    template_name = 'fees/invoice_detail.html'
    context_object_name = 'invoice'

    def test_func(self):
        user = self.request.user
        if user.role == User.Role.ADMIN:
            return True
        if user.is_student:
            return self.object.student.user == user
        return False

    def handle_no_permission(self):
        return redirect('unauthorized')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['payments'] = self.object.payments.all()
        return context


# ─────────────────────────────────────────────────────────────
# Web UI — Fee Payments
# ─────────────────────────────────────────────────────────────

class RecordPaymentView(LoginRequiredMixin, UserPassesTestMixin, FormView):
    template_name = 'fees/record_payment.html'
    form_class = FeePaymentForm
    
    def test_func(self):
        return self.request.user.role == User.Role.ADMIN

    def handle_no_permission(self):
        return redirect('unauthorized')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        invoice = get_object_or_404(FeeInvoice, pk=self.kwargs.get('pk'))
        context['invoice'] = invoice
        return context

    def form_valid(self, form):
        invoice = get_object_or_404(FeeInvoice, pk=self.kwargs.get('pk'))
        payment = form.save(commit=False)
        payment.invoice = invoice
        payment.collected_by = self.request.user
        payment.save()

        # Recalculate invoice amount_paid and update status
        invoice.update_totals()

        messages.success(self.request, f'Payment of Rs. {payment.amount} recorded for invoice {invoice.invoice_number}.')
        return redirect('invoice_detail', pk=invoice.pk)


class GenerateClassInvoicesView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    """
    Bulk generates monthly fee invoices for all active enrollments in a selected class & academic session.
    """
    template_name = 'fees/generate_invoices.html'

    def test_func(self):
        return self.request.user.role == User.Role.ADMIN

    def handle_no_permission(self):
        return redirect('unauthorized')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        from apps.classes.models import AcademicSession
        context['classes'] = Class.objects.filter(is_active=True)
        context['categories'] = FeeCategory.objects.filter(is_active=True)
        context['sessions'] = AcademicSession.objects.filter(is_active=True)
        context['current_session'] = AcademicSession.get_current_session()
        return context

    def post(self, request, *args, **kwargs):
        from apps.classes.models import AcademicSession
        from apps.subjects.models import Enrollment
        import random

        class_id = request.POST.get('class_id')
        category_id = request.POST.get('category_id')
        due_date = request.POST.get('due_date')
        amount_input = request.POST.get('amount')
        session_id = request.POST.get('session_id')

        school_class = get_object_or_404(Class, pk=class_id)
        session = AcademicSession.objects.filter(pk=session_id).first() or AcademicSession.get_current_session()
        category = FeeCategory.objects.filter(pk=category_id).first()

        amount = float(amount_input) if amount_input else (category.default_amount if category else 5000.0)

        enrollments = Enrollment.objects.filter(
            school_class=school_class,
            academic_session=session,
            is_active=True
        ).select_related('student')

        from .models import FeeInvoiceItem
        generated_count = 0
        for enr in enrollments:
            rand_num = random.randint(1000, 9999)
            inv_no = f"INV-{school_class.name.replace(' ', '')}-{timezone.now().strftime('%Y%m%d')}-{rand_num}"
            
            # Calculate Arrears
            arrears = 0
            unpaid_invoices = FeeInvoice.objects.filter(student=enr.student, status__in=['UNPAID', 'PARTIAL'])
            for upi in unpaid_invoices:
                arrears += upi.balance_due
            
            invoice = FeeInvoice.objects.create(
                student=enr.student,
                academic_session=session,
                academic_year=session.name,
                invoice_number=inv_no,
                due_date=due_date or (timezone.now() + timezone.timedelta(days=15)).date(),
                total_amount=0,
                amount_paid=0,
                status='UNPAID',
                remarks=f"Monthly Fee ({category.name if category else 'Tuition Fee'}) - {session.name}"
            )
            
            # Main Fee Item
            FeeInvoiceItem.objects.create(
                invoice=invoice,
                fee_category=category,
                description=f"Monthly Fee ({category.name if category else 'Tuition Fee'})",
                amount=amount
            )
            
            # Arrears Item
            if arrears > 0:
                FeeInvoiceItem.objects.create(
                    invoice=invoice,
                    fee_category=None,
                    description="Previous Arrears (Carried Forward)",
                    amount=arrears
                )
                
            invoice.update_totals()
            generated_count += 1

        messages.success(request, f"Successfully generated {generated_count} fee invoices for {school_class.name} ({session.name}).")
        return redirect('invoice_list')


from django.views.generic import View

class VoidPaymentView(LoginRequiredMixin, UserPassesTestMixin, View):
    """
    Voids an existing payment and recalculates the invoice.
    """
    def test_func(self):
        return self.request.user.role == User.Role.ADMIN

    def handle_no_permission(self):
        return redirect('unauthorized')

    def post(self, request, *args, **kwargs):
        payment = get_object_or_404(FeePayment, pk=self.kwargs.get('pk'))
        if not payment.is_void:
            payment.is_void = True
            payment.void_reason = request.POST.get('void_reason', 'Voided by admin')
            payment.voided_at = timezone.now()
            payment.save()
            
            # Recalculate invoice
            payment.invoice.update_totals()
            messages.success(request, f"Payment of Rs. {payment.amount} has been voided.")
        else:
            messages.info(request, "This payment is already voided.")
            
        return redirect('invoice_detail', pk=payment.invoice.pk)


class StudentLedgerView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    """
    Shows a chronological ledger (Debits vs Credits) for a specific student.
    """
    model = Student
    template_name = 'fees/student_ledger.html'
    context_object_name = 'student'

    def test_func(self):
        user = self.request.user
        if user.role == User.Role.ADMIN:
            return True
        if user.is_student:
            return getattr(user, 'student_profile', None) == self.get_object()
        return False

    def handle_no_permission(self):
        return redirect('unauthorized')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        student = self.object
        
        invoices = FeeInvoice.objects.filter(student=student)
        payments = FeePayment.objects.filter(invoice__student=student, is_void=False)
        
        ledger_entries = []
        for inv in invoices:
            ledger_entries.append({
                'date': inv.issue_date,
                'description': f"Invoice: {inv.invoice_number}",
                'debit': inv.total_amount,
                'credit': 0,
                'obj': inv,
                'type': 'invoice'
            })
            
        for pay in payments:
            ledger_entries.append({
                'date': pay.payment_date,
                'description': f"Payment: {pay.payment_method}",
                'debit': 0,
                'credit': pay.amount,
                'obj': pay,
                'type': 'payment'
            })
            
        # Sort by date, then invoice before payment if same date
        ledger_entries.sort(key=lambda x: (x['date'], 0 if x['type'] == 'invoice' else 1))
        
        balance = 0
        for entry in ledger_entries:
            balance += entry['debit'] - entry['credit']
            entry['balance'] = balance
            
        context['ledger_entries'] = ledger_entries
        context['current_balance'] = balance
        return context

# ─────────────────────────────────────────────────────────────
# DRF Viewsets (API)
# ─────────────────────────────────────────────────────────────

class FeeCategoryViewSet(viewsets.ModelViewSet):
    queryset = FeeCategory.objects.all()
    serializer_class = FeeCategorySerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ['name', 'code']
    filterset_fields = ['is_active']
    ordering_fields = ['name']
    ordering = ['name']

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAdminUser()]
        return [IsAuthenticated()]


class FeeStructureViewSet(viewsets.ModelViewSet):
    queryset = FeeStructure.objects.all()
    serializer_class = FeeStructureSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ['school_class__name', 'category__name', 'academic_year']
    filterset_fields = ['school_class', 'category', 'academic_year', 'is_active']
    ordering_fields = ['due_date', 'school_class__name']
    ordering = ['due_date']

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAdminUser()]
        return [IsAuthenticated()]


class FeeInvoiceViewSet(viewsets.ModelViewSet):
    queryset = FeeInvoice.objects.all()
    serializer_class = FeeInvoiceSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ['invoice_number', 'student__user__first_name', 'student__user__last_name', 'student__admission_number']
    filterset_fields = ['status', 'student', 'academic_year']
    ordering_fields = ['issue_date', 'due_date', 'status']
    ordering = ['-issue_date']

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAdminUser()]
        return [IsAuthenticated()]

    def get_queryset(self):
        qs = FeeInvoice.objects.select_related('student__user')
        user = self.request.user
        if user.is_student:
            return qs.filter(student__user=user)
        return qs.all()


class FeePaymentViewSet(viewsets.ModelViewSet):
    queryset = FeePayment.objects.all()
    serializer_class = FeePaymentSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ['invoice__invoice_number', 'reference_number']
    filterset_fields = ['payment_method', 'invoice']
    ordering_fields = ['payment_date', 'amount']
    ordering = ['-payment_date']

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAdminUser()]
        return [IsAuthenticated()]