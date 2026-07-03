"""
Models for the fees and finance module.
"""
from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator


class FeeCategory(models.Model):
    """
    Types of fees (e.g. Tuition Fee, Transport, Library, Exam Fee).
    """
    name = models.CharField(
        max_length=100,
        unique=True,
        help_text="Fee category name."
    )
    code = models.CharField(
        max_length=20,
        unique=True,
        help_text="Fee code (e.g. TF, TRF, LF)."
    )
    description = models.TextField(
        blank=True,
        null=True
    )
    default_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        help_text="Default amount to charge for this category."
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'fee_categories'
        verbose_name = 'Fee Category'
        verbose_name_plural = 'Fee Categories'
        ordering = ['name']

    def __str__(self):
        return f"{self.name} (Default: {self.default_amount})"


class FeeStructure(models.Model):
    """
    Fee structure for a specific class (can vary per class).
    """
    school_class = models.ForeignKey(
        'classes.Class',
        on_delete=models.CASCADE,
        related_name='fee_structures'
    )
    academic_year = models.CharField(
        max_length=20,
        help_text="e.g. 2023-2024"
    )
    category = models.ForeignKey(
        FeeCategory,
        on_delete=models.CASCADE,
        related_name='structures'
    )
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    due_date = models.DateField(
        help_text="When this fee is due."
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'fee_structures'
        verbose_name = 'Fee Structure'
        verbose_name_plural = 'Fee Structures'
        unique_together = [['school_class', 'academic_year', 'category']]

    def __str__(self):
        return f"{self.school_class.name} - {self.category.name} ({self.academic_year})"


class FeeInvoice(models.Model):
    """
    An invoice generated for a specific student.
    """
    class Status(models.TextChoices):
        UNPAID = 'UNPAID', 'Unpaid'
        PARTIAL = 'PARTIAL', 'Partially Paid'
        PAID = 'PAID', 'Fully Paid'

    student = models.ForeignKey(
        'students.Student',
        on_delete=models.CASCADE,
        related_name='fee_invoices'
    )
    academic_year = models.CharField(
        max_length=20,
        help_text="e.g. 2023-2024"
    )
    invoice_number = models.CharField(
        max_length=50,
        unique=True
    )
    issue_date = models.DateField(auto_now_add=True)
    due_date = models.DateField()
    
    total_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    amount_paid = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.00,
        validators=[MinValueValidator(0)]
    )
    
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.UNPAID
    )
    remarks = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'fee_invoices'
        verbose_name = 'Fee Invoice'
        verbose_name_plural = 'Fee Invoices'
        ordering = ['-issue_date', 'student']

    def __str__(self):
        return f"{self.invoice_number} - {self.student.user.get_full_name()} ({self.status})"

    @property
    def balance_due(self):
        """Calculate remaining balance."""
        return max(0, self.total_amount - self.amount_paid)

    @property
    def paid_percentage(self):
        """Calculate percentage paid."""
        if self.total_amount == 0:
            return 0
        return (self.amount_paid / self.total_amount) * 100

    def update_status(self):
        """Update invoice status based on amount paid."""
        if self.amount_paid >= self.total_amount:
            self.status = self.Status.PAID
        elif self.amount_paid > 0:
            self.status = self.Status.PARTIAL
        else:
            self.status = self.Status.UNPAID
        self.save()


class FeePayment(models.Model):
    """
    A payment transaction against a specific invoice.
    """
    class PaymentMethod(models.TextChoices):
        CASH = 'CASH', 'Cash'
        BANK = 'BANK', 'Bank Transfer'
        CHEQUE = 'CHEQUE', 'Cheque'
        ONLINE = 'ONLINE', 'Online Gateway'

    invoice = models.ForeignKey(
        FeeInvoice,
        on_delete=models.CASCADE,
        related_name='payments'
    )
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    payment_date = models.DateField(auto_now_add=True)
    payment_method = models.CharField(
        max_length=20,
        choices=PaymentMethod.choices,
        default=PaymentMethod.CASH
    )
    reference_number = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text="Transaction ID, Cheque Number, etc."
    )
    remarks = models.TextField(blank=True, null=True)
    
    collected_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        help_text="Admin who processed the payment."
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'fee_payments'
        verbose_name = 'Fee Payment'
        verbose_name_plural = 'Fee Payments'
        ordering = ['-payment_date']

    def __str__(self):
        return f"Payment of {self.amount} for {self.invoice.invoice_number}"

    def save(self, *args, **kwargs):
        """Update invoice amount_paid and status when payment is recorded."""
        super().save(*args, **kwargs)
        # Update invoice
        self.invoice.amount_paid = sum(
            p.amount for p in self.invoice.payments.all()
        )
        self.invoice.update_status()


    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'fee_payments'
        verbose_name = 'Fee Payment'
        verbose_name_plural = 'Fee Payments'
        ordering = ['-payment_date']

    def __str__(self):
        return f"Payment of {self.amount} for {self.invoice.invoice_number}"

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)
        
        # When a payment is created, update the invoice's amount_paid and status
        if is_new:
            self.invoice.amount_paid += self.amount
            self.invoice.update_status()
