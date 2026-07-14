from django import forms
from .models import Announcement
from apps.classes.models import Class, Section


class AnnouncementForm(forms.ModelForm):
    class Meta:
        model = Announcement
        exclude = ['published_by', 'published_at', 'created_at', 'updated_at']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'content': forms.Textarea(attrs={'class': 'form-control', 'rows': 6}),
            'target_audience': forms.Select(attrs={'class': 'form-select', 'id': 'targetAudience'}),
            'target_class': forms.Select(attrs={'class': 'form-select', 'id': 'targetClass'}),
            'target_section': forms.Select(attrs={'class': 'form-select', 'id': 'targetSection'}),
            'is_important': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_published': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'attachment': forms.FileInput(attrs={'class': 'form-control'}),
            'expires_at': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
        }