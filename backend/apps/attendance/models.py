"""
Attendance model for School Management System.

Tracks daily attendance for students.
"""
from django.db import models
from django.conf import settings


class Attendance(models.Model):
    """
    Daily attendance record for a student.
    
    Records whether a student was present, absent, late, etc. on a specific date.
    """
    class Status(models.TextChoices):
        PRESENT = 'PRESENT', 'Present'
        ABSENT = 'ABSENT', 'Absent'
        LATE = 'LATE', 'Late'
        HALF_DAY = 'HALF_DAY', 'Half Day'
        LEAVE = 'LEAVE', 'On Leave'

    student = models.ForeignKey(
        'students.Student',
        on_delete=models.CASCADE,
        related_name='attendance_records',
        help_text="The student this record belongs to."
    )
    school_class = models.ForeignKey(
        'classes.Class',
        on_delete=models.CASCADE,
        related_name='attendance_records'
    )
    section = models.ForeignKey(
        'classes.Section',
        on_delete=models.CASCADE,
        related_name='attendance_records'
    )
    date = models.DateField(
        help_text="The date of attendance."
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PRESENT,
        help_text="Attendance status for the day."
    )
    remarks = models.TextField(
        blank=True,
        null=True,
        help_text="Optional remarks (e.g. reason for absence)."
    )
    marked_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text="The user (Teacher/Admin) who marked the attendance."
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'attendance'
        verbose_name = 'Attendance'
        verbose_name_plural = 'Attendance Records'
        # A student can only have one attendance record per day
        unique_together = [['student', 'date']]
        ordering = ['-date', 'school_class', 'section', 'student__user__first_name']

    def __str__(self):
        return f"{self.student.full_name} - {self.date} - {self.status}"

    @classmethod
    def get_attendance_percentage(cls, student, start_date, end_date):
        """Calculate attendance percentage for a date range."""
        total_days = cls.objects.filter(
            student=student,
            date__range=[start_date, end_date]
        ).count()
        
        if total_days == 0:
            return 0
        
        present_days = cls.objects.filter(
            student=student,
            date__range=[start_date, end_date],
            status__in=[cls.Status.PRESENT, cls.Status.HALF_DAY]
        ).count()
        
        return (present_days / total_days) * 100