from django import forms
from .models import Class, Section
from apps.teachers.models import Teacher


class ClassForm(forms.ModelForm):
    class Meta:
        model = Class
        fields = ['name', 'numeric_grade', 'description', 'class_teacher', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Grade 9'}),
            'numeric_grade': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'e.g. 9'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Optional description'}),
            'class_teacher': forms.Select(attrs={'class': 'form-select'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['class_teacher'].queryset = Teacher.objects.filter(status='ACTIVE').select_related('user')
        self.fields['class_teacher'].empty_label = "--- Select Class Teacher ---"


class SectionForm(forms.ModelForm):
    class Meta:
        model = Section
        fields = ['school_class', 'name', 'section_teacher', 'room_number', 'max_capacity', 'is_active']
        widgets = {
            'school_class': forms.Select(attrs={'class': 'form-select'}),
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. A'}),
            'section_teacher': forms.Select(attrs={'class': 'form-select'}),
            'room_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Room 101'}),
            'max_capacity': forms.NumberInput(attrs={'class': 'form-control'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['section_teacher'].queryset = Teacher.objects.filter(status='ACTIVE').select_related('user')
        self.fields['section_teacher'].empty_label = "--- Select Homeroom Teacher ---"