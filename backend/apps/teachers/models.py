"""
Teacher Model for School Management System.

Like Student, Teacher links to CustomUser for authentication.
Teacher-specific fields: qualifications, experience, department, etc.
"""
from django.db import models
from django.conf import settings


class Teacher(models.Model):
    """
    Stores teacher profile and professional information.
    Each teacher has exactly one CustomUser account.
    """

    # ─── GENDER CHOICES ────────────────────────────────────
    class Gender(models.TextChoices):
        MALE = 'MALE', 'Male'
        FEMALE = 'FEMALE', 'Female'
        OTHER = 'OTHER', 'Other'

    # ─── EMPLOYMENT STATUS ─────────────────────────────────
    class Status(models.TextChoices):
        ACTIVE = 'ACTIVE', 'Active'
        INACTIVE = 'INACTIVE', 'Inactive'
        ON_LEAVE = 'ON_LEAVE', 'On Leave'
        RESIGNED = 'RESIGNED', 'Resigned'
        RETIRED = 'RETIRED', 'Retired'

    # ─── EMPLOYMENT TYPE ───────────────────────────────────
    class EmploymentType(models.TextChoices):
        FULL_TIME = 'FULL_TIME', 'Full Time'
        PART_TIME = 'PART_TIME', 'Part Time'
        CONTRACT = 'CONTRACT', 'Contract'
        VISITING = 'VISITING', 'Visiting'

    # ─── RELATIONSHIP ──────────────────────────────────────
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='teacher_profile',
        help_text="The user account linked to this teacher."
    )

    # ─── PROFESSIONAL FIELDS ───────────────────────────────
    employee_id = models.CharField(
        max_length=20,
        unique=True,
        help_text="Unique employee ID assigned by school."
    )
    department = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text="Department (Science, Arts, Mathematics, etc.)."
    )
    designation = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text="Job title (Senior Teacher, Head of Department, etc.)."
    )
    joining_date = models.DateField(
        help_text="Date when the teacher joined the school."
    )
    employment_type = models.CharField(
        max_length=20,
        choices=EmploymentType.choices,
        default=EmploymentType.FULL_TIME,
    )
    salary = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True,
        help_text="Monthly salary (optional, private)."
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.ACTIVE,
    )

    # ─── EDUCATIONAL QUALIFICATIONS ────────────────────────
    highest_qualification = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        help_text="e.g. M.Sc. Computer Science, B.Ed."
    )
    specialization = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        help_text="Subject specialization (e.g. Physics, English Literature)."
    )
    experience_years = models.PositiveIntegerField(
        default=0,
        help_text="Total years of teaching experience."
    )

    # ─── PERSONAL FIELDS ───────────────────────────────────
    date_of_birth = models.DateField(blank=True, null=True)
    gender = models.CharField(
        max_length=10,
        choices=Gender.choices,
        blank=True,
        null=True,
    )
    religion = models.CharField(max_length=50, blank=True, null=True)
    nationality = models.CharField(max_length=50, default='Pakistani')
    address = models.TextField(blank=True, null=True)
    emergency_contact = models.CharField(max_length=20, blank=True, null=True)
    photo = models.ImageField(
        upload_to='teachers/photos/',
        blank=True,
        null=True,
    )

    # ─── BANK / PAYROLL INFO (optional) ────────────────────
    bank_account_number = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        help_text="Bank account for salary transfer (private)."
    )
    bank_name = models.CharField(max_length=100, blank=True, null=True)

    # ─── TIMESTAMPS ────────────────────────────────────────
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'teachers'
        verbose_name = 'Teacher'
        verbose_name_plural = 'Teachers'
        ordering = ['employee_id']

    def __str__(self):
        return f"{self.user.full_name} ({self.employee_id})"

    @property
    def full_name(self):
        return self.user.full_name

    @property
    def email(self):
        return self.user.email

    @property
    def phone(self):
        return self.user.phone
