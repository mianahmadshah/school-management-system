"""
Serializers for the attendance app.
"""
from rest_framework import serializers
from .models import Attendance
from apps.students.models import Student
from apps.classes.models import Class, Section


class AttendanceSerializer(serializers.ModelSerializer):
    """
    Serializer for viewing and updating individual attendance records.
    """
    student_name = serializers.CharField(source='student.full_name', read_only=True)
    admission_number = serializers.CharField(source='student.admission_number', read_only=True)
    class_name = serializers.CharField(source='school_class.name', read_only=True)
    section_name = serializers.CharField(source='section.name', read_only=True)
    marked_by_name = serializers.SerializerMethodField()

    class Meta:
        model = Attendance
        fields = [
            'id', 'student', 'student_name', 'admission_number',
            'school_class', 'class_name', 'section', 'section_name',
            'date', 'status', 'remarks', 'marked_by', 'marked_by_name',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'marked_by', 'created_at', 'updated_at']

    def get_marked_by_name(self, obj):
        if obj.marked_by:
            return obj.marked_by.full_name
        return None


class BulkAttendanceRecordSerializer(serializers.Serializer):
    """
    Validates a single student's attendance record within a bulk request.
    """
    student = serializers.PrimaryKeyRelatedField(queryset=Student.objects.all())
    status = serializers.ChoiceField(choices=Attendance.Status.choices)
    remarks = serializers.CharField(max_length=255, required=False, allow_blank=True)


class BulkAttendanceSerializer(serializers.Serializer):
    """
    Validates a bulk attendance submission for a specific class, section, and date.
    """
    school_class = serializers.PrimaryKeyRelatedField(queryset=Class.objects.all())
    section = serializers.PrimaryKeyRelatedField(queryset=Section.objects.all())
    date = serializers.DateField()
    records = BulkAttendanceRecordSerializer(many=True)

    def validate(self, attrs):
        school_class = attrs.get('school_class')
        section = attrs.get('section')
        
        # Ensure section belongs to the class
        if section.school_class != school_class:
            raise serializers.ValidationError(
                {'section': f'Section {section.name} does not belong to Class {school_class.name}.'}
            )
            
        # Ensure all students belong to the class and section
        student_ids = [record['student'].id for record in attrs.get('records', [])]
        invalid_students = Student.objects.filter(id__in=student_ids).exclude(
            current_class=school_class, section=section, status='ACTIVE'
        )
        
        if invalid_students.exists():
            invalid_names = ", ".join([s.full_name for s in invalid_students])
            raise serializers.ValidationError(
                {'records': f'The following students are not active in this class/section: {invalid_names}'}
            )
            
        return attrs

    def create(self, validated_data):
        school_class = validated_data['school_class']
        section = validated_data['section']
        date = validated_data['date']
        records_data = validated_data['records']
        marked_by = self.context['request'].user

        created_records = []
        updated_records = []

        for record_data in records_data:
            student = record_data['student']
            status = record_data['status']
            remarks = record_data.get('remarks', '')

            # Use update_or_create to handle cases where attendance was already marked
            attendance, created = Attendance.objects.update_or_create(
                student=student,
                date=date,
                defaults={
                    'school_class': school_class,
                    'section': section,
                    'status': status,
                    'remarks': remarks,
                    'marked_by': marked_by
                }
            )
            if created:
                created_records.append(attendance)
            else:
                updated_records.append(attendance)

        return {
            'created_count': len(created_records),
            'updated_count': len(updated_records),
            'date': date,
            'school_class': school_class.name,
            'section': section.name
        }
