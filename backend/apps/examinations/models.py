"""
Examinations, Marks, and Results models.
"""
from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator


class Exam(models.Model):
    """
    Represents an academic examination/assessment.
    
    Examples: Midterm, Final, Quiz, Unit Test, etc.
    """
    class ExamType(models.TextChoices):
        MIDTERM = 'MIDTERM', 'Midterm Examination'
        FINAL = 'FINAL', 'Final Examination'
        UNIT_TEST = 'UNIT_TEST', 'Unit Test'
        MONTHLY = 'MONTHLY', 'Monthly Test'
        QUIZ = 'QUIZ', 'Quiz'
        PRACTICAL = 'PRACTICAL', 'Practical'
        CUSTOM = 'CUSTOM', 'Custom Exam'

    name = models.CharField(
        max_length=150,
        help_text="e.g. Midterm Fall 2024"
    )
    exam_type = models.CharField(
        max_length=20,
        choices=ExamType.choices,
        default=ExamType.FINAL
    )
    subject = models.ForeignKey(
        'subjects.Subject',
        on_delete=models.CASCADE,
        related_name='exams',
        help_text="Subject for this exam."
    )
    school_class = models.ForeignKey(
        'classes.Class',
        on_delete=models.CASCADE,
        related_name='exams'
    )
    total_marks = models.PositiveIntegerField(
        default=100,
        help_text="Total marks for this exam."
    )
    passing_marks = models.PositiveIntegerField(
        default=40,
        validators=[MinValueValidator(0)],
        help_text="Minimum marks to pass."
    )
    start_date = models.DateField()
    end_date = models.DateField()
    exam_date = models.DateField(
        blank=True,
        null=True,
        help_text="Specific exam date (if single day)."
    )
    exam_time_start = models.TimeField(
        blank=True,
        null=True
    )
    exam_time_end = models.TimeField(
        blank=True,
        null=True
    )
    duration_minutes = models.PositiveIntegerField(
        blank=True,
        null=True,
        help_text="Duration in minutes."
    )
    room_number = models.CharField(
        max_length=20,
        blank=True,
        null=True
    )
    description = models.TextField(
        blank=True,
        null=True,
        help_text="Exam instructions/description."
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Is this exam currently active/ongoing?"
    )
    is_published = models.BooleanField(
        default=False,
        help_text="If true, marks are visible to students."
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_exams'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'exams'
        verbose_name = 'Exam'
        verbose_name_plural = 'Exams'
        ordering = ['-start_date']

    def __str__(self):
        return f"{self.name} - {self.subject.name}"

    @property
    def total_enrolled_students(self):
        """Count students in this class."""
        return self.school_class.students.filter(status='ACTIVE').count()

    @property
    def marks_submitted_count(self):
        """Count how many students have marks."""
        return self.marks.exclude(obtained_marks=None).count()


class Marks(models.Model):
    """
    Marks obtained by a student in a specific exam/subject.
    """
    exam = models.ForeignKey(
        Exam,
        on_delete=models.CASCADE,
        related_name='marks'
    )
    student = models.ForeignKey(
        'students.Student',
        on_delete=models.CASCADE,
        related_name='marks'
    )
    subject = models.ForeignKey(
        'subjects.Subject',
        on_delete=models.CASCADE,
        related_name='marks'
    )
    
    total_marks = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        default=100.00
    )
    passing_marks = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        default=33.00
    )
    obtained_marks = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        blank=True,
        null=True
    )
    practical_marks = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        blank=True,
        null=True,
        default=0.00
    )
    
    grade = models.CharField(
        max_length=5,
        blank=True,
        null=True,
        help_text="Automatically calculated."
    )
    is_passed = models.BooleanField(
        default=False,
        help_text="Pass/Fail status."
    )
    remarks = models.TextField(
        blank=True,
        null=True,
        help_text="Teacher remarks."
    )
    submitted_by = models.ForeignKey(
        'teachers.Teacher',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='submitted_marks'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'marks'
        verbose_name = 'Marks'
        verbose_name_plural = 'Marks'
        unique_together = [['exam', 'student', 'subject']]
        ordering = ['exam', 'student__user__first_name']

    def __str__(self):
        return f"{self.student.full_name} - {self.subject.name} - {self.obtained_marks}/{self.total_marks}"

    def save(self, *args, **kwargs):
        """Auto-calculate grade and pass/fail status."""
        if self.obtained_marks is not None:
            self.is_passed = self.obtained_marks >= self.passing_marks
            percentage = (self.obtained_marks / self.total_marks) * 100 if self.total_marks > 0 else 0
            if percentage >= 90:
                self.grade = 'A+'
            elif percentage >= 80:
                self.grade = 'A'
            elif percentage >= 70:
                self.grade = 'B'
            elif percentage >= 60:
                self.grade = 'C'
            elif percentage >= 50:
                self.grade = 'D'
            else:
                self.grade = 'F'
        super().save(*args, **kwargs)

    @property
    def percentage(self):
        """Calculate percentage."""
        if self.obtained_marks is None or self.total_marks == 0:
            return 0
        return (self.obtained_marks / self.total_marks) * 100


class Result(models.Model):
    """
    Overall result for a student in a specific exam (consolidating all subject marks).
    """
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE, related_name='results')
    student = models.ForeignKey('students.Student', on_delete=models.CASCADE, related_name='results')
    
    total_marks_obtained = models.DecimalField(max_digits=7, decimal_places=2, default=0.00)
    total_maximum_marks = models.DecimalField(max_digits=7, decimal_places=2, default=0.00)
    percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    
    overall_grade = models.CharField(max_length=5, blank=True, null=True)
    passed = models.BooleanField(default=False)
    remarks = models.TextField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'results'
        verbose_name = 'Result'
        verbose_name_plural = 'Results'
        unique_together = [['exam', 'student']]
        ordering = ['exam', '-percentage']

    def __str__(self):
        return f"{self.student.full_name} - {self.exam.name} - {self.percentage}%"