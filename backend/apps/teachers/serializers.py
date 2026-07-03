"""
Serializers for the teachers app.
Same pattern as students: List, Detail, Create, Update serializers.
"""
from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from .models import Teacher

User = get_user_model()


class TeacherListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for teacher table/list views."""
    full_name = serializers.CharField(source='user.full_name', read_only=True)
    email = serializers.CharField(source='user.email', read_only=True)
    phone = serializers.CharField(source='user.phone', read_only=True)

    class Meta:
        model = Teacher
        fields = [
            'id', 'employee_id', 'full_name', 'email', 'phone',
            'department', 'designation', 'employment_type',
            'experience_years', 'status', 'joining_date', 'photo',
        ]


class TeacherDetailSerializer(serializers.ModelSerializer):
    """Full serializer with all teacher fields for the profile page."""
    full_name = serializers.CharField(source='user.full_name', read_only=True)
    email = serializers.CharField(source='user.email', read_only=True)
    phone = serializers.CharField(source='user.phone', read_only=True)
    profile_picture = serializers.ImageField(
        source='user.profile_picture', read_only=True
    )

    class Meta:
        model = Teacher
        fields = [
            'id',
            # User info
            'full_name', 'email', 'phone', 'profile_picture',
            # Professional
            'employee_id', 'department', 'designation',
            'joining_date', 'employment_type', 'status',
            'highest_qualification', 'specialization', 'experience_years',
            # Personal
            'date_of_birth', 'gender', 'religion', 'nationality',
            'address', 'emergency_contact', 'photo',
            # Financial (hidden from non-admin via permissions in views)
            'salary', 'bank_account_number', 'bank_name',
            # Timestamps
            'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class TeacherCreateSerializer(serializers.Serializer):
    """
    Creates both User + Teacher in one API call.
    Uses a transaction to ensure data consistency.
    """

    # ─── USER FIELDS ───────────────────────────────────────
    first_name = serializers.CharField(max_length=150)
    last_name = serializers.CharField(max_length=150)
    email = serializers.EmailField()
    username = serializers.CharField(max_length=150)
    password = serializers.CharField(
        write_only=True,
        validators=[validate_password]
    )
    phone = serializers.CharField(max_length=20, required=False, allow_blank=True)

    # ─── TEACHER FIELDS ────────────────────────────────────
    employee_id = serializers.CharField(max_length=20)
    department = serializers.CharField(max_length=100, required=False, allow_blank=True)
    designation = serializers.CharField(max_length=100, required=False, allow_blank=True)
    joining_date = serializers.DateField()
    employment_type = serializers.ChoiceField(
        choices=Teacher.EmploymentType.choices,
        default=Teacher.EmploymentType.FULL_TIME
    )
    status = serializers.ChoiceField(
        choices=Teacher.Status.choices,
        default=Teacher.Status.ACTIVE
    )
    highest_qualification = serializers.CharField(max_length=200, required=False, allow_blank=True)
    specialization = serializers.CharField(max_length=200, required=False, allow_blank=True)
    experience_years = serializers.IntegerField(min_value=0, default=0)
    date_of_birth = serializers.DateField(required=False, allow_null=True)
    gender = serializers.ChoiceField(
        choices=Teacher.Gender.choices,
        required=False,
        allow_blank=True
    )
    religion = serializers.CharField(max_length=50, required=False, allow_blank=True)
    nationality = serializers.CharField(max_length=50, default='Pakistani')
    address = serializers.CharField(required=False, allow_blank=True)
    emergency_contact = serializers.CharField(max_length=20, required=False, allow_blank=True)
    salary = serializers.DecimalField(
        max_digits=10, decimal_places=2,
        required=False, allow_null=True
    )

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value

    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("This username is already taken.")
        return value

    def validate_employee_id(self, value):
        if Teacher.objects.filter(employee_id=value).exists():
            raise serializers.ValidationError("A teacher with this employee ID already exists.")
        return value

    def create(self, validated_data):
        from django.db import transaction

        user_data = {
            'first_name': validated_data.pop('first_name'),
            'last_name': validated_data.pop('last_name'),
            'email': validated_data.pop('email'),
            'username': validated_data.pop('username'),
            'password': validated_data.pop('password'),
            'phone': validated_data.pop('phone', ''),
            'role': 'TEACHER',  # Always TEACHER role
        }

        with transaction.atomic():
            user = User.objects.create_user(**user_data)
            teacher = Teacher.objects.create(user=user, **validated_data)

        return teacher


class TeacherUpdateSerializer(serializers.ModelSerializer):
    """Update teacher profile (not the user account)."""
    class Meta:
        model = Teacher
        fields = [
            'department', 'designation', 'employment_type', 'status',
            'highest_qualification', 'specialization', 'experience_years',
            'date_of_birth', 'gender', 'religion', 'nationality',
            'address', 'emergency_contact', 'photo', 'salary',
            'bank_account_number', 'bank_name',
        ]
