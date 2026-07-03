from django.contrib import admin
from .models import Attendance

@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ['student', 'date', 'status', 'school_class', 'section', 'marked_by']
    list_filter = ['date', 'status', 'school_class', 'section']
    search_fields = ['student__user__first_name', 'student__user__last_name', 'student__admission_number']
    ordering = ['-date', 'school_class', 'section']
    date_hierarchy = 'date'
