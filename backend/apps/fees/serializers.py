"""
Serializers for the fees and finance app.
"""
from rest_framework import serializers
from .models import FeeCategory, FeeInvoice, FeePayment
from apps.students.models import Student


class FeeCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = FeeCategory
        fields = ['id', 'name', 'description', 'default_amount', 'is_active', 'created_at']
        read_only_fields = ['id', 'created_at']


class FeePaymentSerializer(serializers.ModelSerializer):
    collected_by_name = serializers.CharField(source='collected_by.full_name', read_only=True)
    invoice_number = serializers.CharField(source='invoice.invoice_number', read_only=True)

    class Meta:
        model = FeePayment
        fields = [
            'id', 'invoice', 'invoice_number', 'amount', 'payment_date',
            'payment_method', 'reference_number', 'remarks',
            'collected_by', 'collected_by_name', 'created_at'
        ]
        read_only_fields = ['id', 'payment_date', 'collected_by', 'created_at']


class FeeInvoiceSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source='student.full_name', read_only=True)
    admission_number = serializers.CharField(source='student.admission_number', read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)
    balance_due = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    
    # Nested payments
    payments = FeePaymentSerializer(many=True, read_only=True)

    class Meta:
        model = FeeInvoice
        fields = [
            'id', 'student', 'student_name', 'admission_number',
            'category', 'category_name', 'invoice_number',
            'issue_date', 'due_date', 'total_amount', 'amount_paid',
            'balance_due', 'status', 'remarks', 'payments',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'issue_date', 'amount_paid', 'status', 'created_at', 'updated_at']


class BulkInvoiceSerializer(serializers.Serializer):
    """Serializer for generating invoices for an entire class at once."""
    school_class = serializers.IntegerField(help_text="Class ID to generate invoices for.")
    category = serializers.PrimaryKeyRelatedField(queryset=FeeCategory.objects.all())
    due_date = serializers.DateField()
    amount = serializers.DecimalField(max_digits=10, decimal_places=2, required=False, help_text="Overrides category default amount if provided.")
    invoice_prefix = serializers.CharField(max_length=10, default="INV")

    def create(self, validated_data):
        from django.db import transaction
        import uuid
        
        school_class_id = validated_data['school_class']
        category = validated_data['category']
        due_date = validated_data['due_date']
        amount = validated_data.get('amount', category.default_amount)
        prefix = validated_data.get('invoice_prefix')

        students = Student.objects.filter(current_class_id=school_class_id, status='ACTIVE')
        invoices = []

        with transaction.atomic():
            for student in students:
                invoice_number = f"{prefix}-{student.admission_number}-{uuid.uuid4().hex[:6].upper()}"
                invoice = FeeInvoice(
                    student=student,
                    category=category,
                    invoice_number=invoice_number,
                    due_date=due_date,
                    total_amount=amount
                )
                invoices.append(invoice)
            
            FeeInvoice.objects.bulk_create(invoices)

        return {
            "generated_count": len(invoices),
            "category": category.name,
            "amount_per_student": amount
        }
