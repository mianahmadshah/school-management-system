"""
Class and Section models for School Management System.

Design:
    Class  → e.g. "Grade 9", "Grade 10", "KG"
    Section → e.g. "A", "B", "C" — always belongs to a Class

Why separate? A school has many classes, each with multiple sections.
Grade 9-A and Grade 9-B are the same class but different sections.
"""
from django.db import models
from django.conf import settings


class Class(models.Model):
    """
    Represents an academic class/grade level.
    Example: Grade 1, Grade 9, KG, Pre-KG, A-Level
    """

    name = models.CharField(
        max_length=100,
        unique=True,
        help_text="Class name (e.g. Grade 9, KG, A-Level Year 1)."
    )
    numeric_grade = models.PositiveIntegerField(
        blank=True,
        null=True,
        help_text="Numeric grade level for sorting (1-12). Leave blank for KG/Pre-KG."
    )
    description = models.TextField(
        blank=True,
        null=True,
        help_text="Optional description of the class."
    )
    # Class teacher (head teacher responsible for this class)
    class_teacher = models.ForeignKey(
        'teachers.Teacher',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_classes',
        help_text="The main teacher responsible for this class."
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Inactive classes won't appear in dropdowns."
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'classes'
        verbose_name = 'Class'
        verbose_name_plural = 'Classes'
        # Sort by numeric grade, then by name
        ordering = ['numeric_grade', 'name']

    def __str__(self):
        return self.name

    @property
    def total_students(self):
        """Count total students enrolled in this class (all sections)."""
        return self.sections.aggregate(
            total=models.Count('enrollments')
        )['total'] or 0

    @property
    def total_sections(self):
        """Count how many sections this class has."""
        return self.sections.count()


class Section(models.Model):
    """
    A section within a class.
    Example: Grade 9 → Section A, Grade 9 → Section B

    A section belongs to exactly one Class.
    Students are enrolled into a specific Section (not just the Class).
    """

    school_class = models.ForeignKey(
        Class,
        on_delete=models.CASCADE,
        related_name='sections',
        help_text="The class this section belongs to."
    )
    name = models.CharField(
        max_length=10,
        help_text="Section name (e.g. A, B, C, Blue, Red)."
    )
    # Section teacher (homeroom teacher)
    section_teacher = models.ForeignKey(
        'teachers.Teacher',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_sections',
        help_text="The homeroom teacher for this section."
    )
    room_number = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        help_text="Physical classroom number (e.g. Room 101)."
    )
    max_capacity = models.PositiveIntegerField(
        default=40,
        help_text="Maximum number of students allowed in this section."
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'sections'
        verbose_name = 'Section'
        verbose_name_plural = 'Sections'
        # A class cannot have two sections with the same name
        unique_together = [['school_class', 'name']]
        ordering = ['school_class', 'name']

    def __str__(self):
        return f"{self.school_class.name} - Section {self.name}"

    @property
    def current_strength(self):
        """Count currently enrolled active students."""
        return self.enrollments.filter(is_active=True).count()

    @property
    def available_seats(self):
        """How many more students can join."""
        return max(0, self.max_capacity - self.current_strength)

    @property
    def is_full(self):
        """Check if section has reached capacity."""
        return self.current_strength >= self.max_capacity
