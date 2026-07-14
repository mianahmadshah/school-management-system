"""
Models for the reports app.
"""
from django.db import models
from django.conf import settings


class Report(models.Model):
    """
    Stores generated reports metadata.
    """
    class ReportType(models.TextChoices):
        ATTENDANCE = 'ATTENDANCE', 'Attendance Report'
        ACADEMIC = 'ACADEMIC', 'Academic Performance'
        FEE = 'FEE', 'Fee Collection'
        STUDENT = 'STUDENT', 'Student Summary'
        TEACHER = 'TEACHER', 'Teacher Summary'

    title = models.CharField(max_length=200)
    report_type = models.CharField(max_length=20, choices=ReportType.choices)
    generated_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='reports')
    generated_at = models.DateTimeField(auto_now_add=True)
    parameters = models.JSONField(blank=True, null=True, help_text="Filters used for this report")

    class Meta:
        db_table = 'reports'
        verbose_name = 'Report'
        verbose_name_plural = 'Reports'
        ordering = ['-generated_at']

    def __str__(self):
        return f"{self.title} ({self.get_report_type_display()})"