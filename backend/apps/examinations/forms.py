from django import forms
from .models import Exam, Marks
from apps.classes.models import Class
from apps.subjects.models import Subject


class ExamForm(forms.ModelForm):
    class Meta:
        model = Exam
        exclude = ['created_by']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Midterm Fall 2024'}),
            'exam_type': forms.Select(attrs={'class': 'form-select'}),
            'subject': forms.Select(attrs={'class': 'form-select'}),
            'school_class': forms.Select(attrs={'class': 'form-select'}),
            'total_marks': forms.NumberInput(attrs={'class': 'form-control'}),
            'passing_marks': forms.NumberInput(attrs={'class': 'form-control'}),
            'start_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'end_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'exam_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'exam_time_start': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'exam_time_end': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'duration_minutes': forms.NumberInput(attrs={'class': 'form-control'}),
            'room_number': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_published': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class MarksForm(forms.ModelForm):
    class Meta:
        model = Marks
        fields = ['exam', 'student', 'subject', 'obtained_marks', 'practical_marks', 'remarks']
        widgets = {
            'exam': forms.Select(attrs={'class': 'form-select'}),
            'student': forms.Select(attrs={'class': 'form-select'}),
            'subject': forms.Select(attrs={'class': 'form-select'}),
            'obtained_marks': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'practical_marks': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'remarks': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }


class MarksEntryForm(forms.Form):
    exam = forms.ModelChoiceField(
        queryset=Exam.objects.filter(is_active=True),
        widget=forms.Select(attrs={'class': 'form-select'}),
        required=True
    )
    school_class = forms.ModelChoiceField(
        queryset=Class.objects.filter(is_active=True),
        widget=forms.Select(attrs={'class': 'form-select'}),
        required=True
    )
    subject = forms.ModelChoiceField(
        queryset=Subject.objects.filter(is_active=True),
        widget=forms.Select(attrs={'class': 'form-select'}),
        required=True
    )