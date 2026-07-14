from django.contrib import admin
from .models import Assignment, Submission


class SubmissionInline(admin.TabularInline):
    model = Submission
    extra = 0
    readonly_fields = ['submitted_at', 'status']


@admin.register(Assignment)
class AssignmentAdmin(admin.ModelAdmin):
    list_display = ['title', 'school_class', 'section', 'subject', 'teacher', 'due_date', 'is_active']
    list_filter = ['is_active', 'school_class', 'subject', 'due_date']
    search_fields = ['title', 'teacher__user__first_name', 'subject__name']
    ordering = ['-due_date']
    inlines = [SubmissionInline]


@admin.register(Submission)
class SubmissionAdmin(admin.ModelAdmin):
    list_display = ['student', 'assignment', 'status', 'submitted_at', 'marks_obtained']
    list_filter = ['status', 'assignment']
    search_fields = ['student__user__first_name', 'assignment__title']
    ordering = ['-submitted_at']
