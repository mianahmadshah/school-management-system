"""
Serializers for the examinations app.
"""
from rest_framework import serializers
from .models import Exam, Marks, Result
from apps.students.models import Student
from apps.subjects.models import Subject


class ExamSerializer(serializers.ModelSerializer):
    class Meta:
        model = Exam
        fields = [
            'id', 'name', 'exam_type', 'start_date', 'end_date',
            'description', 'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class MarksSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source='student.full_name', read_only=True)
    admission_number = serializers.CharField(source='student.admission_number', read_only=True)
    subject_name = serializers.CharField(source='subject.name', read_only=True)
    exam_name = serializers.CharField(source='exam.name', read_only=True)

    class Meta:
        model = Marks
        fields = [
            'id', 'exam', 'exam_name', 'student', 'student_name', 'admission_number',
            'subject', 'subject_name', 'total_marks', 'passing_marks',
            'obtained_marks', 'practical_marks', 'grade', 'is_passed',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'grade', 'is_passed', 'created_at', 'updated_at']


class ResultSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source='student.full_name', read_only=True)
    admission_number = serializers.CharField(source='student.admission_number', read_only=True)
    exam_name = serializers.CharField(source='exam.name', read_only=True)
    class_name = serializers.CharField(source='student.current_class.name', read_only=True, default='')

    class Meta:
        model = Result
        fields = [
            'id', 'exam', 'exam_name', 'student', 'student_name', 'admission_number', 'class_name',
            'total_marks_obtained', 'total_maximum_marks', 'percentage',
            'overall_grade', 'passed', 'remarks', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class BulkMarkRecordSerializer(serializers.Serializer):
    """Single student marks in a bulk upload."""
    student = serializers.PrimaryKeyRelatedField(queryset=Student.objects.all())
    obtained_marks = serializers.DecimalField(max_digits=5, decimal_places=2)
    practical_marks = serializers.DecimalField(max_digits=5, decimal_places=2, required=False, allow_null=True)


class BulkMarksEntrySerializer(serializers.Serializer):
    """
    Validates a bulk marks submission for an exam and subject.
    """
    exam = serializers.PrimaryKeyRelatedField(queryset=Exam.objects.all())
    subject = serializers.PrimaryKeyRelatedField(queryset=Subject.objects.all())
    total_marks = serializers.DecimalField(max_digits=5, decimal_places=2, default=100.00)
    passing_marks = serializers.DecimalField(max_digits=5, decimal_places=2, default=33.00)
    records = BulkMarkRecordSerializer(many=True)

    def validate(self, attrs):
        # Validate that the obtained marks are not greater than total marks
        total_marks = attrs.get('total_marks', 100)
        for record in attrs.get('records', []):
            if record['obtained_marks'] > total_marks:
                raise serializers.ValidationError(
                    f"Obtained marks for student {record['student'].id} cannot exceed total marks ({total_marks})."
                )
        return attrs

    def create(self, validated_data):
        exam = validated_data['exam']
        subject = validated_data['subject']
        total_marks = validated_data.get('total_marks', 100)
        passing_marks = validated_data.get('passing_marks', 33)
        records_data = validated_data['records']

        created_records = []
        updated_records = []

        for record_data in records_data:
            student = record_data['student']
            obtained_marks = record_data['obtained_marks']
            practical_marks = record_data.get('practical_marks', 0)

            marks, created = Marks.objects.update_or_create(
                exam=exam,
                student=student,
                subject=subject,
                defaults={
                    'total_marks': total_marks,
                    'passing_marks': passing_marks,
                    'obtained_marks': obtained_marks,
                    'practical_marks': practical_marks,
                }
            )
            if created:
                created_records.append(marks)
            else:
                updated_records.append(marks)

        return {
            'created_count': len(created_records),
            'updated_count': len(updated_records),
            'exam': exam.name,
            'subject': subject.name
        }
