"""
Django Admin configuration for the Student model.
"""
from django.contrib import admin
from .models import Student


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    """
    Admin configuration for Student model.
    """
    # Table columns in the admin list view
    list_display = [
        'admission_number', 'full_name', 'email',
        'current_class', 'section', 'gender', 'status', 'admission_date'
    ]

    # Right-side filter panel
    list_filter = ['status', 'gender', 'current_class', 'section', 'blood_group']

    # Search box
    search_fields = [
        'admission_number', 'user__first_name', 'user__last_name',
        'user__email', 'father_name', 'roll_number'
    ]

    # Default ordering
    ordering = ['admission_number']

    # Fields shown when editing a student
    fieldsets = (
        ('Account Info', {
            'fields': ('user',)
        }),
        ('Academic Information', {
            'fields': (
                'admission_number', 'roll_number', 'current_class',
                'section', 'admission_date', 'status'
            )
        }),
        ('Personal Information', {
            'fields': (
                'date_of_birth', 'gender', 'blood_group',
                'religion', 'nationality', 'address', 'photo'
            )
        }),
        ('Parent Information', {
            'fields': (
                'father_name', 'father_phone', 'father_occupation',
                'mother_name', 'mother_phone', 'mother_occupation',
            ),
            'classes': ('collapse',),  # Collapsed by default
        }),
        ('Guardian & Emergency', {
            'fields': (
                'guardian_name', 'guardian_phone', 'guardian_relation',
                'emergency_contact'
            ),
            'classes': ('collapse',),
        }),
        ('Medical Information', {
            'fields': ('medical_conditions',),
            'classes': ('collapse',),
        }),
    )

    # Read-only timestamp fields
    readonly_fields = ['created_at', 'updated_at']

    def full_name(self, obj):
        return obj.full_name
    full_name.short_description = 'Full Name'

    def email(self, obj):
        return obj.email
    email.short_description = 'Email'
