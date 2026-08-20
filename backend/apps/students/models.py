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


class StudentAdmission(models.Model):
    """
    Student Admission application and payment tracking.
    
    Workflow:
    Admin receives application -> Registers admission details -> Records initial fee payment
    (e.g., Rs. 8,000 paid out of Rs. 10,000) -> Generates receipt -> On approval,
    system automatically creates the Student account, Profile, and active Session Enrollment.
    """
    class AdmissionStatus(models.TextChoices):
        PENDING = 'PENDING', 'Pending Payment'
        PARTIAL = 'PARTIAL', 'Partially Paid'
        PAID = 'PAID', 'Fully Paid'
        APPROVED = 'APPROVED', 'Approved & Enrolled'
        REJECTED = 'REJECTED', 'Rejected'

    admission_number = models.CharField(max_length=20, unique=True, help_text="Application / Admission Number")
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    father_name = models.CharField(max_length=100)
    father_phone = models.CharField(max_length=20, blank=True, null=True)
    date_of_birth = models.DateField()
    gender = models.CharField(max_length=10, choices=Student.Gender.choices)
    address = models.TextField()
    previous_school = models.CharField(max_length=200, blank=True, null=True)
    
    academic_session = models.ForeignKey('classes.AcademicSession', on_delete=models.CASCADE, related_name='admissions')
    school_class = models.ForeignKey('classes.Class', on_delete=models.CASCADE, related_name='admissions')
    section = models.ForeignKey('classes.Section', on_delete=models.CASCADE, related_name='admissions')
    admission_date = models.DateField(auto_now_add=True)
    
    admission_fee = models.DecimalField(max_digits=10, decimal_places=2, default=10000.00)
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    status = models.CharField(max_length=20, choices=AdmissionStatus.choices, default=AdmissionStatus.PENDING)
    remarks = models.TextField(blank=True, null=True)
    
    created_student = models.ForeignKey(Student, on_delete=models.SET_NULL, null=True, blank=True, related_name='admission_record')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'student_admissions'
        verbose_name = 'Student Admission'
        verbose_name_plural = 'Student Admissions'
        ordering = ['-admission_date']

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.admission_number}) - {self.status}"

    @property
    def balance_due(self):
        return max(0, self.admission_fee - self.amount_paid)

    def update_payment_status(self):
        if self.status == self.AdmissionStatus.APPROVED:
            return
        if self.amount_paid >= self.admission_fee:
            self.status = self.AdmissionStatus.PAID
        elif self.amount_paid > 0:
            self.status = self.AdmissionStatus.PARTIAL
        else:
            self.status = self.AdmissionStatus.PENDING
        self.save()

