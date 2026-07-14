from django import forms
from .models import Subject, Enrollment
from apps.teachers.models import Teacher
from apps.classes.models import Class, Section
from apps.students.models import Student


class SubjectForm(forms.ModelForm):
    class Meta:
        model = Subject
        fields = ['name', 'code', 'school_class', 'teacher', 'subject_type', 'credits', 'description', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Mathematics'}),
            'code': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. MATH-101'}),
            'school_class': forms.Select(attrs={'class': 'form-select'}),
            'teacher': forms.Select(attrs={'class': 'form-select'}),
            'subject_type': forms.Select(attrs={'class': 'form-select'}),
            'credits': forms.NumberInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Optional description'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['teacher'].queryset = Teacher.objects.filter(status='ACTIVE').select_related('user')
        self.fields['teacher'].empty_label = "--- Select Teacher ---"
        self.fields['school_class'].queryset = Class.objects.filter(is_active=True)


class EnrollmentForm(forms.ModelForm):
    class Meta:
        model = Enrollment
        fields = ['student', 'school_class', 'section', 'academic_year', 'roll_number', 'is_active']
        widgets = {
            'student': forms.Select(attrs={'class': 'form-select'}),
            'school_class': forms.Select(attrs={'class': 'form-select'}),
            'section': forms.Select(attrs={'class': 'form-select'}),
            'academic_year': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. 2024-2025'}),
            'roll_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Optional roll number'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['student'].queryset = Student.objects.filter(status='ACTIVE').select_related('user')
        self.fields['section'].queryset = Section.objects.filter(is_active=True)