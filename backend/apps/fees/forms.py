from django import forms
from .models import FeeCategory, FeeStructure, FeeInvoice, FeePayment
from apps.students.models import Student
from apps.classes.models import Class, AcademicSession


class FeeCategoryForm(forms.ModelForm):
    class Meta:
        model = FeeCategory
        fields = ['name', 'code', 'default_amount', 'description', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Tuition Fee'}),
            'code': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. TF'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Category description'}),
            'default_amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'placeholder': '5000.00'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class FeeStructureForm(forms.ModelForm):
    class Meta:
        model = FeeStructure
        fields = ['school_class', 'academic_session', 'academic_year', 'category', 'amount', 'due_date', 'is_active']
        widgets = {
            'school_class': forms.Select(attrs={'class': 'form-select'}),
            'academic_session': forms.Select(attrs={'class': 'form-select'}),
            'academic_year': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. 2026-2027'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'due_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['school_class'].queryset = Class.objects.filter(is_active=True)
        self.fields['academic_session'].queryset = AcademicSession.objects.filter(is_active=True)
        self.fields['category'].queryset = FeeCategory.objects.filter(is_active=True)
        current = AcademicSession.get_current_session()
        if current and not self.instance.pk:
            self.fields['academic_session'].initial = current
            self.fields['academic_year'].initial = current.name


class FeeInvoiceForm(forms.ModelForm):
    class Meta:
        model = FeeInvoice
        fields = [
            'student', 'academic_session', 'academic_year', 'invoice_number',
            'due_date', 'total_amount', 'amount_paid', 'status', 'remarks'
        ]
        widgets = {
            'student': forms.Select(attrs={'class': 'form-select'}),
            'academic_session': forms.Select(attrs={'class': 'form-select'}),
            'academic_year': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. 2026-2027'}),
            'invoice_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Auto-generated if empty'}),
            'due_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'total_amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'amount_paid': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'remarks': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['student'].queryset = Student.objects.filter(status='ACTIVE').select_related('user')
        self.fields['academic_session'].queryset = AcademicSession.objects.filter(is_active=True)
        self.fields['invoice_number'].required = False
        current = AcademicSession.get_current_session()
        if current and not self.instance.pk:
            self.fields['academic_session'].initial = current
            self.fields['academic_year'].initial = current.name

    def clean(self):
        cleaned_data = super().clean()
        invoice_number = cleaned_data.get('invoice_number')
        if not invoice_number:
            import random
            from django.utils import timezone
            rand_num = random.randint(1000, 9999)
            cleaned_data['invoice_number'] = f"INV-{timezone.now().strftime('%Y%m%d')}-{rand_num}"
        return cleaned_data


class FeePaymentForm(forms.ModelForm):
    class Meta:
        model = FeePayment
        fields = ['amount', 'payment_method', 'reference_number', 'remarks']
        widgets = {
            'amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'payment_method': forms.Select(attrs={'class': 'form-select'}),
            'reference_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Transaction ID or Receipt #'}),
            'remarks': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }