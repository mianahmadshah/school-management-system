"""
Serializers for the students app.

We have two serializers:
  1. StudentListSerializer  → Lightweight, for list views (less data)
  2. StudentDetailSerializer → Full data, for single student view
  3. StudentCreateSerializer → For creating a student + user account together
"""
from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from .models import Student
from apps.classes.models import Class, Section

User = get_user_model()


class StudentListSerializer(serializers.ModelSerializer):
    """
    Lightweight serializer for student lists.
    Only includes fields needed for a table row view.
    Avoids sending unnecessary data over the network.
    """
    full_name = serializers.CharField(source='user.full_name', read_only=True)
    email = serializers.CharField(source='user.email', read_only=True)
    photo = serializers.ImageField(read_only=True)
    class_name = serializers.CharField(source='current_class.name', read_only=True, default='')
    section_name = serializers.CharField(source='section.name', read_only=True, default='')

    class Meta:
        model = Student
        fields = [
            'id', 'admission_number', 'full_name', 'email',
            'current_class', 'class_name', 'section', 'section_name', 
            'gender', 'status', 'photo', 'admission_date',
        ]

    def to_representation(self, instance):
        data = super().to_representation(instance)
        # Pull phone from user model
        data['phone'] = instance.user.phone
        return data


class StudentDetailSerializer(serializers.ModelSerializer):
    """
    Full serializer with all student fields.
    Used for the student detail/profile page.
    """
    # Nested user data (read-only in this serializer)
    full_name = serializers.CharField(source='user.full_name', read_only=True)
    email = serializers.CharField(source='user.email', read_only=True)
    phone = serializers.CharField(source='user.phone', read_only=True)
    profile_picture = serializers.ImageField(
        source='user.profile_picture', read_only=True
    )
    age = serializers.IntegerField(read_only=True)
    class_name = serializers.CharField(source='current_class.name', read_only=True, default='')
    section_name = serializers.CharField(source='section.name', read_only=True, default='')

    class Meta:
        model = Student
        fields = [
            'id',
            # User info
            'full_name', 'email', 'phone', 'profile_picture',
            # Academic
            'admission_number', 'current_class', 'class_name', 
            'section', 'section_name', 'roll_number', 'admission_date', 'status',
            # Personal
            'date_of_birth', 'age', 'gender', 'blood_group',
            'religion', 'nationality', 'address', 'photo',
            # Parent info
            'father_name', 'father_phone', 'father_occupation',
            'mother_name', 'mother_phone', 'mother_occupation',
            'guardian_name', 'guardian_phone', 'guardian_relation',
            'emergency_contact',
            # Medical
            'medical_conditions',
            # Timestamps
            'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'age']


class StudentCreateSerializer(serializers.Serializer):
    """
    Serializer for creating a Student along with their User account.
    
    Why a plain Serializer (not ModelSerializer)?
    Because we're creating TWO models (User + Student) in one API call.
    A single ModelSerializer can't handle that cleanly.
    """

    # ─── USER ACCOUNT FIELDS ───────────────────────────────
    first_name = serializers.CharField(max_length=150)
    last_name = serializers.CharField(max_length=150)
    email = serializers.EmailField()
    username = serializers.CharField(max_length=150)
    password = serializers.CharField(
        write_only=True,
        validators=[validate_password]
    )
    phone = serializers.CharField(max_length=20, required=False, allow_blank=True)

    # ─── STUDENT FIELDS ────────────────────────────────────
    admission_number = serializers.CharField(max_length=20)
    current_class = serializers.PrimaryKeyRelatedField(
        queryset=Class.objects.all(), required=False, allow_null=True
    )
    section = serializers.PrimaryKeyRelatedField(
        queryset=Section.objects.all(), required=False, allow_null=True
    )
    roll_number = serializers.CharField(max_length=20, required=False, allow_blank=True)
    admission_date = serializers.DateField()
    date_of_birth = serializers.DateField()
    gender = serializers.ChoiceField(choices=Student.Gender.choices)
    blood_group = serializers.ChoiceField(
        choices=Student.BloodGroup.choices,
        required=False,
        allow_blank=True
    )
    religion = serializers.CharField(max_length=50, required=False, allow_blank=True)
    nationality = serializers.CharField(max_length=50, default='Pakistani')
    address = serializers.CharField()
    status = serializers.ChoiceField(
        choices=Student.Status.choices,
        default=Student.Status.ACTIVE
    )

    # Parent fields (all optional)
    father_name = serializers.CharField(max_length=100, required=False, allow_blank=True)
    father_phone = serializers.CharField(max_length=20, required=False, allow_blank=True)
    father_occupation = serializers.CharField(max_length=100, required=False, allow_blank=True)
    mother_name = serializers.CharField(max_length=100, required=False, allow_blank=True)
    mother_phone = serializers.CharField(max_length=20, required=False, allow_blank=True)
    mother_occupation = serializers.CharField(max_length=100, required=False, allow_blank=True)
    guardian_name = serializers.CharField(max_length=100, required=False, allow_blank=True)
    guardian_phone = serializers.CharField(max_length=20, required=False, allow_blank=True)
    guardian_relation = serializers.CharField(max_length=50, required=False, allow_blank=True)
    emergency_contact = serializers.CharField(max_length=20, required=False, allow_blank=True)
    medical_conditions = serializers.CharField(required=False, allow_blank=True)

    def validate_email(self, value):
        """Ensure email is not already taken."""
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value

    def validate_username(self, value):
        """Ensure username is not already taken."""
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("A user with this username already exists.")
        return value

    def validate_admission_number(self, value):
        """Ensure admission number is unique."""
        if Student.objects.filter(admission_number=value).exists():
            raise serializers.ValidationError("A student with this admission number already exists.")
        return value

    def create(self, validated_data):
        """
        Create User first, then Student.
        Runs inside a transaction so if Student creation fails,
        the User is also rolled back.
        """
        from django.db import transaction

        # Extract user-specific fields
        user_data = {
            'first_name': validated_data.pop('first_name'),
            'last_name': validated_data.pop('last_name'),
            'email': validated_data.pop('email'),
            'username': validated_data.pop('username'),
            'password': validated_data.pop('password'),
            'phone': validated_data.pop('phone', ''),
            'role': 'STUDENT',  # Always set role to STUDENT
        }

        with transaction.atomic():
            # Step 1: Create the User account
            user = User.objects.create_user(**user_data)

            # Step 2: Create the Student profile linked to that user
            student = Student.objects.create(user=user, **validated_data)

        return student


class StudentUpdateSerializer(serializers.ModelSerializer):
    """
    For updating student profile data only (not the user account).
    """
    class Meta:
        model = Student
        fields = [
            'current_class', 'section', 'roll_number', 'status',
            'blood_group', 'religion', 'nationality', 'address', 'photo',
            'father_name', 'father_phone', 'father_occupation',
            'mother_name', 'mother_phone', 'mother_occupation',
            'guardian_name', 'guardian_phone', 'guardian_relation',
            'emergency_contact', 'medical_conditions',
        ]
