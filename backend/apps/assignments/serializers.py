"""
Serializers for the assignments app.
"""
from rest_framework import serializers
from django.utils import timezone
from .models import Assignment, Submission


class AssignmentSerializer(serializers.ModelSerializer):
    class_name = serializers.CharField(source='school_class.name', read_only=True)
    section_name = serializers.CharField(source='section.name', read_only=True)
    subject_name = serializers.CharField(source='subject.name', read_only=True)
    teacher_name = serializers.CharField(source='teacher.user.full_name', read_only=True)
    is_overdue = serializers.SerializerMethodField()

    class Meta:
        model = Assignment
        fields = [
            'id', 'title', 'description',
            'school_class', 'class_name', 'section', 'section_name',
            'subject', 'subject_name', 'teacher', 'teacher_name',
            'due_date', 'attachment', 'max_marks', 'is_active',
            'is_overdue', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_is_overdue(self, obj):
        return timezone.now() > obj.due_date


class SubmissionSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source='student.user.full_name', read_only=True)
    admission_number = serializers.CharField(source='student.admission_number', read_only=True)
    assignment_title = serializers.CharField(source='assignment.title', read_only=True)

    class Meta:
        model = Submission
        fields = [
            'id', 'assignment', 'assignment_title',
            'student', 'student_name', 'admission_number',
            'status', 'submission_date', 'attachment',
            'student_notes', 'obtained_marks', 'teacher_feedback'
        ]
        read_only_fields = ['id', 'submission_date']

    def validate(self, attrs):
        assignment = attrs.get('assignment') or (self.instance and self.instance.assignment)
        # Auto-mark as late if submitted after due date
        if attrs.get('attachment') or attrs.get('student_notes'):
            if assignment and timezone.now() > assignment.due_date:
                attrs['status'] = Submission.Status.LATE
            else:
                attrs['status'] = Submission.Status.SUBMITTED
            attrs['submission_date'] = timezone.now()
        return attrs
