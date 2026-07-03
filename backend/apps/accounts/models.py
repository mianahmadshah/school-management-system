"""
Custom User Model for School Management System.

Why custom user? Django's default User is limited.
We add: role, phone, profile picture, and address fields.

All three roles (Admin, Teacher, Student) share this base model.
Each role gets a separate profile model (Teacher/Student) with extra details.
"""
from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    """
    Extended User model replacing Django's default User.
    Adds role-based access control and profile information.
    """

    # ─── ROLE CHOICES ──────────────────────────────────────
    class Role(models.TextChoices):
        ADMIN = 'ADMIN', 'Admin'
        TEACHER = 'TEACHER', 'Teacher'
        STUDENT = 'STUDENT', 'Student'

    # ─── FIELDS ────────────────────────────────────────────
    email = models.EmailField(
        unique=True,
        help_text="Required. Used for login and notifications."
    )
    role = models.CharField(
        max_length=10,
        choices=Role.choices,
        default=Role.STUDENT,
        help_text="Determines what the user can access."
    )
    phone = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        help_text="Contact phone number."
    )
    profile_picture = models.ImageField(
        upload_to='profiles/',  # Saved to media/profiles/
        blank=True,
        null=True,
        help_text="Profile photo (optional)."
    )
    address = models.TextField(
        blank=True,
        null=True,
        help_text="Full residential address."
    )
    date_of_birth = models.DateField(
        blank=True,
        null=True,
        help_text="Date of birth."
    )
    gender = models.CharField(
        max_length=10,
        choices=[('MALE', 'Male'), ('FEMALE', 'Female'), ('OTHER', 'Other')],
        blank=True,
        null=True,
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Uncheck to disable login without deleting the account."
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Use email as the login identifier instead of username
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    class Meta:
        db_table = 'users'
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.get_full_name()} ({self.role})"

    # ─── HELPER PROPERTIES ─────────────────────────────────
    @property
    def is_admin(self):
        """Check if the user has admin role."""
        return self.role == self.Role.ADMIN

    @property
    def is_teacher(self):
        """Check if the user has teacher role."""
        return self.role == self.Role.TEACHER

    @property
    def is_student(self):
        """Check if the user has student role."""
        return self.role == self.Role.STUDENT

    @property
    def full_name(self):
        """Return formatted full name."""
        return self.get_full_name() or self.username
