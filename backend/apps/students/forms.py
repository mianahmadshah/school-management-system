from django import forms
from django.contrib.auth import get_user_model
from .models import Student, StudentAdmission
from apps.classes.models import Class, Section, AcademicSession

User = get_user_model()

class StudentUserForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Enter temporary password'}), required=True)
    
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'phone', 'password']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First Name'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last Name'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email Address'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Phone Number'}),
        }

class StudentUserEditForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'phone']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First Name'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last Name'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email Address'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Phone Number'}),
        }

class StudentProfileForm(forms.ModelForm):
    class Meta:
        model = Student
        exclude = ['user']
        widgets = {
            'admission_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Admission Number'}),
            'current_class': forms.Select(attrs={'class': 'form-select'}),
            'section': forms.Select(attrs={'class': 'form-select'}),
            'admission_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'roll_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Roll Number'}),
            'date_of_birth': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'gender': forms.Select(attrs={'class': 'form-select'}),
            'blood_group': forms.Select(attrs={'class': 'form-select'}),
            'religion': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Religion'}),
            'nationality': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Full Address'}),
            'photo': forms.FileInput(attrs={'class': 'form-control'}),
            'father_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': "Father's Name"}),
            'father_phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': "Father's Phone"}),
            'father_occupation': forms.TextInput(attrs={'class': 'form-control', 'placeholder': "Father's Occupation"}),
            'mother_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': "Mother's Name"}),
            'mother_phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': "Mother's Phone"}),
            'mother_occupation': forms.TextInput(attrs={'class': 'form-control', 'placeholder': "Mother's Occupation"}),
            'guardian_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': "Guardian's Name (Optional)"}),
            'guardian_phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': "Guardian's Phone"}),
            'guardian_relation': forms.TextInput(attrs={'class': 'form-control', 'placeholder': "Guardian's Relationship"}),
            'emergency_contact': forms.TextInput(attrs={'class': 'form-control', 'placeholder': "Emergency Contact Number"}),
            'medical_conditions': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': "Medical details (allergies, etc.)"}),
            'status': forms.Select(attrs={'class': 'form-select'}),
        }


class StudentAdmissionForm(forms.ModelForm):
    class Meta:
        model = StudentAdmission
        fields = [
            'admission_number', 'first_name', 'last_name', 'email', 'phone',
            'father_name', 'father_phone', 'date_of_birth', 'gender', 'address',
            'previous_school', 'academic_session', 'school_class', 'section',
            'admission_fee', 'amount_paid', 'remarks'
        ]
        widgets = {
            'admission_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. ADM2026-001'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First Name'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last Name'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email Address'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Phone'}),
            'father_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': "Father / Guardian Name"}),
            'father_phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': "Father / Guardian Phone"}),
            'date_of_birth': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'gender': forms.Select(attrs={'class': 'form-select'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'previous_school': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Previous School (if any)'}),
            'academic_session': forms.Select(attrs={'class': 'form-select'}),
            'school_class': forms.Select(attrs={'class': 'form-select'}),
            'section': forms.Select(attrs={'class': 'form-select'}),
            'admission_fee': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '10000'}),
            'amount_paid': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '8000'}),
            'remarks': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Optional remarks'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['academic_session'].queryset = AcademicSession.objects.filter(is_active=True)
        self.fields['school_class'].queryset = Class.objects.filter(is_active=True)
        self.fields['section'].queryset = Section.objects.filter(is_active=True)
        current = AcademicSession.get_current_session()
        if current:
            self.fields['academic_session'].initial = current

