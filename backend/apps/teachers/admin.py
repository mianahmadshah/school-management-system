"""Django Admin configuration for the Teacher model."""
from django.contrib import admin
from .models import Teacher


@admin.register(Teacher)
class TeacherAdmin(admin.ModelAdmin):
    list_display = [
        'employee_id', 'full_name', 'email', 'phone',
        'department', 'designation', 'employment_type', 'status'
    ]
    list_filter = ['status', 'gender', 'department', 'employment_type']
    search_fields = [
        'employee_id', 'user__first_name', 'user__last_name',
        'user__email', 'department', 'specialization'
    ]
    ordering = ['employee_id']

    fieldsets = (
        ('Account', {'fields': ('user',)}),
        ('Professional Info', {
            'fields': (
                'employee_id', 'department', 'designation',
                'joining_date', 'employment_type', 'status'
            )
        }),
        ('Qualifications', {
            'fields': ('highest_qualification', 'specialization', 'experience_years')
        }),
        ('Personal Info', {
            'fields': (
                'date_of_birth', 'gender', 'religion',
                'nationality', 'address', 'emergency_contact', 'photo'
            )
        }),
        ('Financial Info', {
            'fields': ('salary', 'bank_account_number', 'bank_name'),
            'classes': ('collapse',),
        }),
    )
    readonly_fields = ['created_at', 'updated_at']

    def full_name(self, obj):
        return obj.full_name
    full_name.short_description = 'Full Name'

    def email(self, obj):
        return obj.email
    email.short_description = 'Email'

    def phone(self, obj):
        return obj.phone
    phone.short_description = 'Phone'
