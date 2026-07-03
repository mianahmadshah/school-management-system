"""
Serializers for the subjects app.
Handles Subject and Enrollment models.
"""
from rest_framework import serializers
from .models import Subject, Enrollment
from apps.students.serializers import StudentListSerializer


class SubjectSerializer(serializers.ModelSerializer):
    """
    Serializer for the Subject model.
    """
    school_class_name = serializers.CharField(source='school_class.name', read_only=True)
    teacher_name = serializers.SerializerMethodField()

    class Meta:
        model = Subject
        fields = [
            'id', 'name', 'code', 'description', 'school_class', 'school_class_name',
            'teacher', 'teacher_name', 'subject_type', 'credits', 'is_active',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_teacher_name(self, obj):
        if obj.teacher:
            return obj.teacher.user.full_name
        return None

    def validate_code(self, value):
        qs = Subject.objects.filter(code__iexact=value)
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise serializers.ValidationError(f'Subject with code {value} already exists.')
        return value


class EnrollmentSerializer(serializers.ModelSerializer):
    """
    Serializer for Enrollment model.
    """
    student_name = serializers.CharField(source='student.user.full_name', read_only=True)
    admission_number = serializers.CharField(source='student.admission_number', read_only=True)
    school_class_name = serializers.CharField(source='school_class.name', read_only=True)
    section_name = serializers.CharField(source='section.name', read_only=True)

    class Meta:
        model = Enrollment
        fields = [
            'id', 'student', 'student_name', 'admission_number',
            'school_class', 'school_class_name', 'section', 'section_name',
            'academic_year', 'roll_number', 'enrollment_date', 'is_active'
        ]
        read_only_fields = ['id', 'enrollment_date']

    def validate(self, attrs):
        """Ensure a student isn't enrolled twice in the same academic year."""
        student = attrs.get('student')
        academic_year = attrs.get('academic_year')
        
        # If updating, exclude self
        instance = self.instance
        qs = Enrollment.objects.filter(student=student, academic_year=academic_year)
        if instance:
            qs = qs.exclude(pk=instance.pk)
            
        if qs.exists():
            raise serializers.ValidationError(
                {'academic_year': f'Student is already enrolled for the academic year {academic_year}.'}
            )
        return attrs
