from django import forms
from .models import Report
from apps.classes.models import Class
from apps.examinations.models import Exam
import datetime


class ReportFilterForm(forms.Form):
    report_type = forms.ChoiceField(choices=Report.ReportType.choices, widget=forms.Select(attrs={'class': 'form-select'}))
    class_id = forms.ModelChoiceField(queryset=Class.objects.filter(is_active=True), required=False, empty_label="All Classes", widget=forms.Select(attrs={'class': 'form-select'}))
    exam_id = forms.ModelChoiceField(queryset=Exam.objects.all(), required=False, empty_label="All Exams", widget=forms.Select(attrs={'class': 'form-select'}))
    from_date = forms.DateField(required=False, widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}))
    to_date = forms.DateField(required=False, widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set default from_date to first day of current month
        today = datetime.date.today()
        self.fields['from_date'].initial = today.replace(day=1)
        self.fields['to_date'].initial = today