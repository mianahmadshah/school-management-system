"""
Subject and Enrollment models for School Management System.

Design:
    Subject    → e.g. "Mathematics", "Science". 
                 Linked to a specific Class and optionally assigned to a Teacher.
    Enrollment → Links a Student to a Class and Section for an academic session.
"""
from django.db import models

class Subject(models.Model):
    """
    Represents an academic subject taught in a specific class.
    """
    class SubjectType(models.TextChoices):
        COMPULSORY = 'COMPULSORY', 'Compulsory'
        OPTIONAL = 'OPTIONAL', 'Optional'

    name = models.CharField(
        max_length=100,
        help_text="Name of the subject (e.g. Mathematics, English)."
    )
    code = models.CharField(
        max_length=20,
        unique=True,
        help_text="Unique subject code (e.g. MATH-101)."
    )
    description = models.TextField(
        blank=True,
        null=True,
    )
    school_class = models.ForeignKey(
        'classes.Class',
        on_delete=models.CASCADE,
        related_name='subjects',
        help_text="The class this subject is taught in."
    )
    teacher = models.ForeignKey(
        'teachers.Teacher',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='subjects',
        help_text="The teacher assigned to teach this subject."
    )
    subject_type = models.CharField(
        max_length=20,
        choices=SubjectType.choices,
        default=SubjectType.COMPULSORY,
    )
    credits = models.PositiveIntegerField(
        default=1,
        help_text="Credit hours for the subject."
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'subjects'
        verbose_name = 'Subject'
        verbose_name_plural = 'Subjects'
        ordering = ['school_class', 'name']

    def __str__(self):
        return f"{self.name} ({self.code}) - {self.school_class.name}"


class Enrollment(models.Model):
    """
    Enrollment links a student to a Class and Section for a specific academic year.
    It tracks the student's academic placement.
    """
    student = models.ForeignKey(
        'students.Student',
        on_delete=models.CASCADE,
        related_name='enrollments'
    )
    school_class = models.ForeignKey(
        'classes.Class',
        on_delete=models.CASCADE,
        related_name='enrollments'
    )
    section = models.ForeignKey(
        'classes.Section',
        on_delete=models.CASCADE,
        related_name='enrollments'
    )
    academic_year = models.CharField(
        max_length=20,
        help_text="e.g. 2023-2024"
    )
    roll_number = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        help_text="Roll number for this specific enrollment."
    )
    enrollment_date = models.DateField(auto_now_add=True)
    is_active = models.BooleanField(
        default=True,
        help_text="Whether this enrollment is currently active."
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'enrollments'
        verbose_name = 'Enrollment'
        verbose_name_plural = 'Enrollments'
        # Each student can only be enrolled once per academic year in a section
        unique_together = [['student', 'school_class', 'section', 'academic_year']]
        ordering = ['academic_year', 'section', 'roll_number']

    def __str__(self):
        return f"{self.student.user.get_full_name()} - {self.school_class.name} ({self.academic_year})"
