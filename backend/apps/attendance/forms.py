from django import forms
from .models import Attendance
from apps.students.models import Student
from apps.classes.models import Class, Section


class AttendanceForm(forms.ModelForm):
    """Form for marking single attendance record."""
    class Meta:
        model = Attendance
        fields = ['student', 'school_class', 'section', 'date', 'status', 'remarks']
        widgets = {
            'student': forms.Select(attrs={'class': 'form-select'}),
            'school_class': forms.Select(attrs={'class': 'form-select'}),
            'section': forms.Select(attrs={'class': 'form-select'}),
            'date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'remarks': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Optional remarks'}),
        }


class BulkAttendanceForm(forms.Form):
    """Form for marking attendance for an entire class/section at once."""
    date = forms.DateField(
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        required=True
    )
    school_class = forms.ModelChoiceField(
        queryset=Class.objects.filter(is_active=True),
        widget=forms.Select(attrs={'class': 'form-select'}),
        required=True
    )
    section = forms.ModelChoiceField(
        queryset=Section.objects.filter(is_active=True),
        widget=forms.Select(attrs={'class': 'form-select'}),
        required=True
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # These will be populated dynamically via JavaScript
        self.attendance_data = []

    def clean(self):
        cleaned_data = super().clean()
        # Get students from the submitted data
        student_ids = self.data.getlist('student_ids')
        statuses = self.data.getlist('statuses')
        remarks_list = self.data.getlist('remarks_list')
        
        self.attendance_data = []
        date = cleaned_data.get('date')
        school_class = cleaned_data.get('school_class')
        section = cleaned_data.get('section')
        
        if student_ids and date and school_class and section:
            for i, student_id in enumerate(student_ids):
                status = statuses[i] if i < len(statuses) else 'PRESENT'
                remarks = remarks_list[i] if i < len(remarks_list) else ''
                self.attendance_data.append({
                    'student_id': int(student_id),
                    'status': status,
                    'remarks': remarks,
                    'date': date,
                    'school_class': school_class,
                    'section': section,
                })
        return cleaned_data

    def save(self, commit=True):
        """Create attendance records from the cleaned data."""
        records = []
        for data in self.attendance_data:
            # Upsert: update if exists, create if not
            record, created = Attendance.objects.update_or_create(
                student_id=data['student_id'],
                date=data['date'],
                defaults={
                    'status': data['status'],
                    'remarks': data['remarks'],
                    'school_class': data['school_class'],
                    'section': data['section'],
                }
            )
            records.append(record)
        return records