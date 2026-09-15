"""
Views for the students app.
Handles both Web UI templates (ListView, DetailView, CreateView, UpdateView, DeleteView)
and REST API views for backward compatibility.
"""
from django.db import transaction
from django.urls import reverse_lazy
from django.shortcuts import redirect
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth import get_user_model
from django.db.models import Q

from .models import Student, StudentAdmission
from .forms import StudentUserForm, StudentUserEditForm, StudentProfileForm, StudentAdmissionForm
from apps.classes.models import Class, Section

# DRF Imports for backward compatibility
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
try:
    from django_filters.rest_framework import DjangoFilterBackend
except ImportError:
    DjangoFilterBackend = None

from .serializers import (
    StudentListSerializer,
    StudentDetailSerializer,
    StudentCreateSerializer,
    StudentUpdateSerializer,
)
from apps.accounts.permissions import IsAdminUser, IsAdminOrTeacher

User = get_user_model()


# ─────────────────────────────────────────────────────────────
# TEMPLATE-BASED VIEWS (Web UI)
# ─────────────────────────────────────────────────────────────

class StudentListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    """
    Renders student roster list, with complete search and filtering capabilities.
    """
    model = Student
    template_name = 'students/student_list.html'
    context_object_name = 'students'
    paginate_by = 10

    def test_func(self):
        return self.request.user.role in [User.Role.ADMIN, User.Role.TEACHER]

    def handle_no_permission(self):
        return redirect('unauthorized')

    def get_queryset(self):
        queryset = Student.objects.select_related('user', 'current_class', 'section').all()
        
        # Searching
        q = self.request.GET.get('q', '')
        if q:
            queryset = queryset.filter(
                Q(user__first_name__icontains=q) |
                Q(user__last_name__icontains=q) |
                Q(admission_number__icontains=q) |
                Q(roll_number__icontains=q) |
                Q(father_name__icontains=q)
            )

        # Filtering by Class
        class_id = self.request.GET.get('class_id', '')
        if class_id:
            queryset = queryset.filter(current_class_id=class_id)

        # Filtering by Section
        section_id = self.request.GET.get('section_id', '')
        if section_id:
            queryset = queryset.filter(section_id=section_id)

        # Filtering by Status
        status_filter = self.request.GET.get('status', '')
        if status_filter:
            queryset = queryset.filter(status=status_filter)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['classes'] = Class.objects.all()
        context['sections'] = Section.objects.all()
        # Preserve query string parameters in pagination links
        query_params = self.request.GET.copy()
        if 'page' in query_params:
            query_params.pop('page')
        context['query_params'] = query_params.urlencode()
        return context


class StudentDetailView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    """
    Renders detailed profile card of a single student.
    """
    model = Student
    template_name = 'students/student_detail.html'
    context_object_name = 'student'

    def test_func(self):
        # Admin, Teacher, or Student themselves can view
        user = self.request.user
        if user.role in [User.Role.ADMIN, User.Role.TEACHER]:
            return True
        return hasattr(user, 'student_profile') and user.student_profile.pk == self.get_object().pk

    def handle_no_permission(self):
        return redirect('unauthorized')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        student = self.object
        from apps.fees.models import FeeInvoice
        invoices = FeeInvoice.objects.filter(student=student).order_by('-issue_date')
        total_invoiced = sum(inv.total_amount for inv in invoices)
        total_paid = sum(inv.amount_paid for inv in invoices)
        context['fee_invoices'] = invoices
        context['fee_total_invoiced'] = total_invoiced
        context['fee_total_paid'] = total_paid
        context['fee_balance_due'] = max(0, total_invoiced - total_paid)
        return context


class StudentCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    """
    Form view to create a student user credential + student record in one transaction.
    """
    model = Student
    form_class = StudentProfileForm
    template_name = 'students/student_form.html'
    success_url = reverse_lazy('student_list')

    def test_func(self):
        return self.request.user.role == User.Role.ADMIN

    def handle_no_permission(self):
        return redirect('unauthorized')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['user_form'] = StudentUserForm(self.request.POST)
        else:
            context['user_form'] = StudentUserForm()
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        user_form = context['user_form']
        if user_form.is_valid():
            try:
                with transaction.atomic():
                    user = user_form.save(commit=False)
                    user.role = User.Role.STUDENT
                    user.username = user.email
                    user.set_password(user_form.cleaned_data['password'])
                    user.save()
                    
                    student = form.save(commit=False)
                    student.user = user
                    student.save()
                messages.success(self.request, f"Student {student.full_name} created successfully.")
                return redirect(self.success_url)
            except Exception as e:
                messages.error(self.request, f"Error saving records: {str(e)}")
                return self.form_invalid(form)
        else:
            return self.form_invalid(form)


class StudentUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """
    Updates a student profile and their associated User credentials.
    """
    model = Student
    form_class = StudentProfileForm
    template_name = 'students/student_form.html'
    success_url = reverse_lazy('student_list')

    def test_func(self):
        return self.request.user.role == User.Role.ADMIN

    def handle_no_permission(self):
        return redirect('unauthorized')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['user_form'] = StudentUserEditForm(self.request.POST, instance=self.object.user)
        else:
            context['user_form'] = StudentUserEditForm(instance=self.object.user)
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        user_form = context['user_form']
        if user_form.is_valid():
            try:
                with transaction.atomic():
                    user_form.save()
                    form.save()
                messages.success(self.request, f"Student {self.object.full_name} updated successfully.")
                return redirect(self.success_url)
            except Exception as e:
                messages.error(self.request, f"Error saving changes: {str(e)}")
                return self.form_invalid(form)
        else:
            return self.form_invalid(form)


class StudentDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    """
    Deletes a student record. Triggering a cascade delete on their User credentials.
    """
    model = Student
    template_name = 'students/student_confirm_delete.html'
    success_url = reverse_lazy('student_list')

    def test_func(self):
        return self.request.user.role == User.Role.ADMIN

    def handle_no_permission(self):
        return redirect('unauthorized')

    def post(self, request, *args, **kwargs):
        student = self.get_object()
        student_name = student.full_name
        # Delete user account, which deletes student profile via CASCADE
        student.user.delete()
        messages.success(request, f"Student {student_name} deleted successfully.")
        return redirect(self.success_url)


# ─────────────────────────────────────────────────────────────
# DRF VIEWSET (Backward Compatibility)
# ─────────────────────────────────────────────────────────────

class StudentViewSet(viewsets.ModelViewSet):
    queryset = Student.objects.select_related('user', 'current_class', 'section').all()
    filter_backends = [backend for backend in [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter] if backend is not None]
    search_fields = ['user__first_name', 'user__last_name', 'user__email', 'admission_number', 'roll_number', 'father_name']
    filterset_fields = ['status', 'gender', 'current_class', 'section', 'blood_group']
    ordering_fields = ['admission_number', 'created_at', 'admission_date']
    ordering = ['admission_number']

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes = [IsAdminUser]
        else:
            permission_classes = [IsAdminOrTeacher]
        return [permission() for permission in permission_classes]

    def get_serializer_class(self):
        if self.action == 'create':
            return StudentCreateSerializer
        if self.action in ['update', 'partial_update']:
            return StudentUpdateSerializer
        if self.action == 'retrieve':
            return StudentDetailSerializer
        return StudentListSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        student = serializer.save()
        detail_serializer = StudentDetailSerializer(student, context={'request': request})
        return Response({'message': f'Student {student.full_name} created successfully.', 'data': detail_serializer.data}, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['get'], permission_classes=[IsAdminOrTeacher])
    def stats(self, request):
        total = Student.objects.count()
        active = Student.objects.filter(status='ACTIVE').count()
        inactive = Student.objects.filter(status='INACTIVE').count()
        graduated = Student.objects.filter(status='GRADUATED').count()
        male = Student.objects.filter(gender='MALE').count()
        female = Student.objects.filter(gender='FEMALE').count()
        return Response({
            'total_students': total, 'active': active, 'inactive': inactive, 'graduated': graduated,
            'gender_breakdown': {'male': male, 'female': female}
        })

    @action(detail=True, methods=['get'], permission_classes=[IsAdminOrTeacher])
    def profile(self, request, pk=None):
        student = self.get_object()
        serializer = StudentDetailSerializer(student, context={'request': request})
        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        student = self.get_object()
        student_name = student.full_name
        student.user.delete()
        return Response({'message': f'Student {student_name} and their account have been deleted.'}, status=status.HTTP_200_OK)


# ─────────────────────────────────────────────────────────────
# STUDENT ADMISSION VIEWS
# ─────────────────────────────────────────────────────────────

class StudentAdmissionListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = StudentAdmission
    template_name = 'students/admission_list.html'
    context_object_name = 'admissions'
    paginate_by = 15

    def test_func(self):
        return self.request.user.role == User.Role.ADMIN

    def handle_no_permission(self):
        return redirect('unauthorized')


class StudentAdmissionCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = StudentAdmission
    form_class = StudentAdmissionForm
    template_name = 'students/admission_form.html'
    success_url = reverse_lazy('admission_list')

    def test_func(self):
        return self.request.user.role == User.Role.ADMIN

    def handle_no_permission(self):
        return redirect('unauthorized')

    def form_valid(self, form):
        from django.db import transaction
        with transaction.atomic():
            admission = form.save(commit=False)
            admission.update_payment_status()
            admission.save()

            messages.success(
                self.request,
                f"Admission application registered for {admission.first_name} {admission.last_name}. "
                f"Paid: Rs. {admission.amount_paid} out of Rs. {admission.admission_fee}. Balance: Rs. {admission.balance_due}."
            )
            return redirect('admission_receipt', pk=admission.pk)


class StudentAdmissionApproveView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    model = StudentAdmission

    def test_func(self):
        return self.request.user.role == User.Role.ADMIN

    def handle_no_permission(self):
        return redirect('unauthorized')

    def post(self, request, *args, **kwargs):
        from django.db import transaction
        from apps.subjects.models import Enrollment
        from apps.fees.models import FeeInvoice, FeePayment
        adm = self.get_object()

        if adm.status == StudentAdmission.AdmissionStatus.APPROVED:
            messages.info(request, "Student admission is already approved and enrolled.")
            return redirect('admission_list')

        with transaction.atomic():
            user = User.objects.create_user(
                username=adm.email,
                email=adm.email,
                first_name=adm.first_name,
                last_name=adm.last_name,
                phone=adm.phone,
                role=User.Role.STUDENT,
                password='StudentPassword123'
            )

            student = Student.objects.create(
                user=user,
                admission_number=adm.admission_number,
                current_class=adm.school_class,
                section=adm.section,
                admission_date=adm.admission_date,
                date_of_birth=adm.date_of_birth,
                gender=adm.gender,
                address=adm.address,
                father_name=adm.father_name,
                father_phone=adm.father_phone,
                status=Student.Status.ACTIVE
            )

            Enrollment.objects.create(
                student=student,
                school_class=adm.school_class,
                section=adm.section,
                academic_session=adm.academic_session,
                academic_year=adm.academic_session.name,
                status='ENROLLED',
                is_active=True
            )

            inv_number = f"INV-ADM-{adm.admission_number}"
            invoice = FeeInvoice.objects.create(
                student=student,
                academic_session=adm.academic_session,
                academic_year=adm.academic_session.name,
                invoice_number=inv_number,
                due_date=adm.admission_date,
                total_amount=adm.admission_fee,
                amount_paid=adm.amount_paid,
                status='PAID' if adm.amount_paid >= adm.admission_fee else ('PARTIAL' if adm.amount_paid > 0 else 'UNPAID'),
                remarks="Admission Fee"
            )

            if adm.amount_paid > 0:
                FeePayment.objects.create(
                    invoice=invoice,
                    amount=adm.amount_paid,
                    payment_method='CASH',
                    reference_number=f"REC-{adm.admission_number}",
                    remarks="Initial Admission Fee Payment",
                    collected_by=request.user
                )

            adm.status = StudentAdmission.AdmissionStatus.APPROVED
            adm.created_student = student
            adm.save()

        messages.success(
            request,
            f"Admission APPROVED! Account created for {student.full_name}. Credentials: {adm.email} / StudentPassword123."
        )
        return redirect('student_detail', pk=student.pk)


class AdmissionReceiptView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    model = StudentAdmission
    template_name = 'students/admission_receipt.html'
    context_object_name = 'admission'

    def test_func(self):
        return self.request.user.role in [User.Role.ADMIN, User.Role.TEACHER]

    def handle_no_permission(self):
        return redirect('unauthorized')

