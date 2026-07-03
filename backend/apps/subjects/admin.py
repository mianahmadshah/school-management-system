from django.contrib import admin
from .models import Subject, Enrollment

@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'school_class', 'teacher', 'subject_type', 'is_active']
    list_filter = ['is_active', 'subject_type', 'school_class']
    search_fields = ['name', 'code', 'school_class__name']
    ordering = ['school_class', 'name']

@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ['student', 'school_class', 'section', 'academic_year', 'is_active']
    list_filter = ['academic_year', 'is_active', 'school_class']
    search_fields = ['student__user__first_name', 'student__user__last_name', 'student__admission_number']
    ordering = ['-academic_year', 'school_class', 'section']
