from django.contrib import admin
from .models import Period, Timetable

@admin.register(Period)
class PeriodAdmin(admin.ModelAdmin):
    list_display = ['name', 'start_time', 'end_time', 'is_break', 'order']
    list_filter = ['is_break']
    ordering = ['order', 'start_time']


@admin.register(Timetable)
class TimetableAdmin(admin.ModelAdmin):
    list_display = ['school_class', 'section', 'day_of_week', 'period', 'subject', 'teacher']
    list_filter = ['day_of_week', 'school_class', 'section', 'teacher']
    search_fields = ['subject__name', 'teacher__user__first_name']
    ordering = ['day_of_week', 'period__order']
