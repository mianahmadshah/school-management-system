from django import forms
from django.contrib.auth import get_user_model
from .models import Student
from apps.classes.models import Class, Section

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
