"""Django Admin for Class and Section models."""
from django.contrib import admin
from .models import Class, Section


class SectionInline(admin.TabularInline):
    """
    Show sections inline inside the Class admin edit page.
    This lets you add/edit sections without leaving the Class form.
    """
    model = Section
    extra = 1       # Show 1 blank row for adding a new section
    fields = ['name', 'section_teacher', 'room_number', 'max_capacity', 'is_active']


@admin.register(Class)
class ClassAdmin(admin.ModelAdmin):
    list_display = ['name', 'numeric_grade', 'class_teacher', 'total_sections', 'is_active']
    list_filter = ['is_active']
    search_fields = ['name', 'description']
    ordering = ['numeric_grade', 'name']
    # Show sections as a table inside the class edit page
    inlines = [SectionInline]

    def total_sections(self, obj):
        return obj.sections.count()
    total_sections.short_description = 'Sections'


@admin.register(Section)
class SectionAdmin(admin.ModelAdmin):
    list_display = [
        'school_class', 'name', 'section_teacher',
        'room_number', 'max_capacity', 'current_strength', 'is_active'
    ]
    list_filter = ['is_active', 'school_class']
    search_fields = ['name', 'school_class__name', 'room_number']
    ordering = ['school_class', 'name']

    def current_strength(self, obj):
        return obj.current_strength
    current_strength.short_description = 'Students'
