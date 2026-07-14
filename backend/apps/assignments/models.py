"""
Models for the assignments app.
"""
from django.db import models
from django.conf import settings


class Assignment(models.Model):
    """
    Homework or Project assigned to a specific class and section.
    """
    title = models.CharField(
        max_length=200,
        help_text="Assignment title."
    )
    description = models.TextField(
        help_text="Detailed instructions for the assignment."
    )
    
    school_class = models.ForeignKey(
        'classes.Class',
        on_delete=models.CASCADE,
        related_name='assignments'
    )
    section = models.ForeignKey(
        'classes.Section',
        on_delete=models.CASCADE,
        related_name='assignments'
    )
    subject = models.ForeignKey(
        'subjects.Subject',
        on_delete=models.CASCADE,
        related_name='assignments'
    )
    
    teacher = models.ForeignKey(
        'teachers.Teacher',
        on_delete=models.CASCADE,
        related_name='given_assignments'
    )
    
    assigned_date = models.DateField(auto_now_add=True)
    due_date = models.DateTimeField(
        help_text="When this assignment is due."
    )
    attachment = models.FileField(
        upload_to='assignments/questions/',
        null=True,
        blank=True,
        help_text="Assignment file (PDF, Word doc, etc.)"
    )
    
    max_marks = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=100.00,
        help_text="Total marks for this assignment."
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Inactive assignments won't be shown to students."
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'assignments'
        verbose_name = 'Assignment'
        verbose_name_plural = 'Assignments'
        ordering = ['-due_date']

    def __str__(self):
        return f"{self.title} - {self.school_class.name} {self.section.name}"

    @property
    def is_overdue(self):
        """Check if assignment is overdue."""
        from django.utils import timezone
        return timezone.now() > self.due_date

    @property
    def submissions_count(self):
        """Count total submissions."""
        return self.submissions.count()

    @property
    def pending_submissions_count(self):
        """Count pending submissions."""
        return self.submissions.filter(
            status__in=[self.submissions.model.Status.PENDING]
        ).count()


class Submission(models.Model):
    """
    A student's submission for an assignment.
    """
    class Status(models.TextChoices):
        PENDING = 'PENDING', 'Pending/Not Submitted'
        SUBMITTED = 'SUBMITTED', 'Submitted'
        LATE = 'LATE', 'Submitted Late'
        GRADED = 'GRADED', 'Graded'

    assignment = models.ForeignKey(
        Assignment,
        on_delete=models.CASCADE,
        related_name='submissions'
    )
    student = models.ForeignKey(
        'students.Student',
        on_delete=models.CASCADE,
        related_name='submissions'
    )
    
    submission_text = models.TextField(
        blank=True,
        null=True,
        help_text="Text-based submission."
    )
    submission_file = models.FileField(
        upload_to='assignments/submissions/',
        blank=True,
        null=True,
        help_text="Submitted file."
    )
    submitted_at = models.DateTimeField(
        blank=True,
        null=True
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING
    )
    
    marks_obtained = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        blank=True,
        null=True,
        help_text="Marks given by teacher."
    )
    teacher_remarks = models.TextField(
        blank=True,
        null=True,
        help_text="Teacher feedback on submission."
    )
    graded_at = models.DateTimeField(
        blank=True,
        null=True
    )
    graded_by = models.ForeignKey(
        'teachers.Teacher',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='graded_submissions'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'submissions'
        verbose_name = 'Submission'
        verbose_name_plural = 'Submissions'
        unique_together = [['assignment', 'student']]
        ordering = ['assignment', 'student__user__first_name']

    def __str__(self):
        return f"{self.student.user.get_full_name()} - {self.assignment.title}"

    @property
    def is_late(self):
        """Check if submitted after due date."""
        if self.submitted_at and self.assignment.due_date:
            return self.submitted_at > self.assignment.due_date
        return False

