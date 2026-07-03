"""
Serializers for the timetable app.
"""
from rest_framework import serializers
from .models import Period, Timetable


class PeriodSerializer(serializers.ModelSerializer):
    class Meta:
        model = Period
        fields = ['id', 'name', 'start_time', 'end_time', 'is_break', 'order']


class TimetableSerializer(serializers.ModelSerializer):
    class_name = serializers.CharField(source='school_class.name', read_only=True)
    section_name = serializers.CharField(source='section.name', read_only=True)
    subject_name = serializers.CharField(source='subject.name', read_only=True, default='')
    teacher_name = serializers.CharField(source='teacher.user.full_name', read_only=True, default='')
    period_details = PeriodSerializer(source='period', read_only=True)

    class Meta:
        model = Timetable
        fields = [
            'id', 'school_class', 'class_name', 'section', 'section_name',
            'period', 'period_details', 'day_of_week', 
            'subject', 'subject_name', 'teacher', 'teacher_name', 'room_number'
        ]

    def validate(self, attrs):
        teacher = attrs.get('teacher')
        period = attrs.get('period')
        day_of_week = attrs.get('day_of_week')

        # If a teacher is assigned, ensure they are not double-booked
        if teacher:
            qs = Timetable.objects.filter(teacher=teacher, period=period, day_of_week=day_of_week)
            if self.instance:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                raise serializers.ValidationError(
                    f"Teacher is already scheduled for another class during {period.name} on {day_of_week}."
                )
        return attrs
