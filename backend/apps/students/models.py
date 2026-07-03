"""
Student Model for School Management System.

The Student model stores all student-specific data.
It has a OneToOne link to CustomUser (so each student has login credentials).

Design Decision:
    We separate Student from CustomUser so the User table stays clean
    and focused on authentication. Student holds school-specific data.
"""
from django.db import models
from django.conf import settings


class Student(models.Model):
    """
    Stores student profile and academic information.
    Each student has exactly one CustomUser account.
    """

    # ─── GENDER CHOICES ────────────────────────────────────
    class Gender(models.TextChoices):
        MALE = 'MALE', 'Male'
        FEMALE = 'FEMALE', 'Female'
        OTHER = 'OTHER', 'Other'

    # ─── BLOOD GROUP CHOICES ───────────────────────────────
    class BloodGroup(models.TextChoices):
        A_POS = 'A+', 'A+'
        A_NEG = 'A-', 'A-'
        B_POS = 'B+', 'B+'
        B_NEG = 'B-', 'B-'
        AB_POS = 'AB+', 'AB+'
        AB_NEG = 'AB-', 'AB-'
        O_POS = 'O+', 'O+'
        O_NEG = 'O-', 'O-'

    # ─── STATUS CHOICES ────────────────────────────────────
    class Status(models.TextChoices):
        ACTIVE = 'ACTIVE', 'Active'
        INACTIVE = 'INACTIVE', 'Inactive'
        GRADUATED = 'GRADUATED', 'Graduated'
        EXPELLED = 'EXPELLED', 'Expelled'
        TRANSFERRED = 'TRANSFERRED', 'Transferred'

    # ─── RELATIONSHIPS ─────────────────────────────────────
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='student_profile',
        help_text="The user account linked to this student."
    )

    # ─── ACADEMIC FIELDS ───────────────────────────────────
    admission_number = models.CharField(
        max_length=20,
        unique=True,
        help_text="Unique admission/roll number assigned by school."
    )
    # Note: current_class and section will be linked in Module 3
    # when we build the Class and Section models.
    # For now we use CharField as temporary placeholders.
    current_class = models.ForeignKey(
        'classes.Class',
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='students',
        help_text="The class the student is currently enrolled in."
    )
    section = models.ForeignKey(
        'classes.Section',
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='students',
        help_text="The section the student is currently enrolled in."
    )
    admission_date = models.DateField(
        help_text="Date when the student was admitted to the school."
    )
    roll_number = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        help_text="Roll number within the class."
    )

    # ─── PERSONAL FIELDS ───────────────────────────────────
    date_of_birth = models.DateField(
        help_text="Student's date of birth."
    )
    gender = models.CharField(
        max_length=10,
        choices=Gender.choices,
    )
    blood_group = models.CharField(
        max_length=5,
        choices=BloodGroup.choices,
        blank=True,
        null=True,
    )
    religion = models.CharField(
        max_length=50,
        blank=True,
        null=True,
    )
    nationality = models.CharField(
        max_length=50,
        default='Pakistani',
    )
    address = models.TextField(
        help_text="Residential address of the student."
    )
    photo = models.ImageField(
        upload_to='students/photos/',
        blank=True,
        null=True,
        help_text="Student photo (optional)."
    )

    # ─── PARENT / GUARDIAN INFORMATION ────────────────────
    father_name = models.CharField(max_length=100, blank=True, null=True)
    father_phone = models.CharField(max_length=20, blank=True, null=True)
    father_occupation = models.CharField(max_length=100, blank=True, null=True)

    mother_name = models.CharField(max_length=100, blank=True, null=True)
    mother_phone = models.CharField(max_length=20, blank=True, null=True)
    mother_occupation = models.CharField(max_length=100, blank=True, null=True)

    guardian_name = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text="Emergency guardian (if different from parents)."
    )
    guardian_phone = models.CharField(max_length=20, blank=True, null=True)
    guardian_relation = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        help_text="Relationship of guardian to student (Uncle, Aunt, etc.)."
    )
    emergency_contact = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        help_text="Primary emergency contact number."
    )

    # ─── MEDICAL INFORMATION ───────────────────────────────
    medical_conditions = models.TextField(
        blank=True,
        null=True,
        help_text="Any known medical conditions or allergies."
    )

    # ─── STATUS ────────────────────────────────────────────
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.ACTIVE,
    )

    # ─── TIMESTAMPS ────────────────────────────────────────
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'students'
        verbose_name = 'Student'
        verbose_name_plural = 'Students'
        ordering = ['admission_number']

    def __str__(self):
        return f"{self.user.full_name} ({self.admission_number})"

    @property
    def full_name(self):
        return self.user.full_name

    @property
    def email(self):
        return self.user.email

    @property
    def age(self):
        """Calculate age from date of birth."""
        from datetime import date
        today = date.today()
        dob = self.date_of_birth
        return today.year - dob.year - (
            (today.month, today.day) < (dob.month, dob.day)
        )
