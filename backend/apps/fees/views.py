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
        qs = FeeStructure.objects.filter(is_active=True).select_related('school_class', 'category')
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
        qs = FeeInvoice.objects.select_related('student__user')
        user = self.request.user
        if user.is_student:
            student = getattr(user, 'student_profile', None)
            if student:
                qs = qs.filter(student=student)
        student_id = self.request.GET.get('student_id', '')
        if student_id:
            qs = qs.filter(student_id=student_id)
        status = self.request.GET.get('status', '')
        if status:
            qs = qs.filter(status=status)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.role != User.Role.STUDENT:
            context['students'] = Student.objects.filter(status='ACTIVE').select_related('user')
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
        messages.success(self.request, f'Payment of {payment.amount} recorded.')
        return redirect('invoice_detail', pk=invoice.pk)


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