from django.contrib import admin
from .models import Exam, Marks, Result

@admin.register(Exam)
class ExamAdmin(admin.ModelAdmin):
    list_display = ['name', 'exam_type', 'start_date', 'end_date', 'is_active']
    list_filter = ['exam_type', 'is_active', 'start_date']
    search_fields = ['name']
    ordering = ['-start_date']

@admin.register(Marks)
class MarksAdmin(admin.ModelAdmin):
    list_display = ['student', 'exam', 'subject', 'obtained_marks', 'total_marks', 'grade', 'is_passed']
    list_filter = ['exam', 'subject', 'grade', 'is_passed']
    search_fields = ['student__user__first_name', 'student__user__last_name', 'subject__name']
    ordering = ['exam', 'student', 'subject']

@admin.register(Result)
class ResultAdmin(admin.ModelAdmin):
    list_display = ['student', 'exam', 'percentage', 'overall_grade', 'passed']
    list_filter = ['exam', 'overall_grade', 'passed']
    search_fields = ['student__user__first_name', 'student__user__last_name']
    ordering = ['exam', '-percentage']
