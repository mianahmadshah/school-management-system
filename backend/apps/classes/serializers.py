"""
Serializers for the classes app.
Handles both Class and Section serialization.
"""
from rest_framework import serializers
from .models import Class, Section


# ─────────────────────────────────────────────────────────────
# SECTION SERIALIZERS
# ─────────────────────────────────────────────────────────────
class SectionSerializer(serializers.ModelSerializer):
    """
    Full Section serializer for CRUD operations.
    Includes computed properties: current_strength and available_seats.
    """
    current_strength = serializers.IntegerField(read_only=True)
    available_seats = serializers.IntegerField(read_only=True)
    # Show class name alongside class ID
    school_class_name = serializers.CharField(
        source='school_class.name', read_only=True
    )
    # Show section teacher's name
    section_teacher_name = serializers.SerializerMethodField()

    class Meta:
        model = Section
        fields = [
            'id', 'school_class', 'school_class_name', 'name',
            'section_teacher', 'section_teacher_name',
            'room_number', 'max_capacity', 'current_strength',
            'available_seats', 'is_active', 'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_section_teacher_name(self, obj):
        if obj.section_teacher:
            return obj.section_teacher.user.full_name
        return None

    def validate(self, attrs):
        """
        Validate: section name must be unique within the same class.
        DRF checks unique_together but this gives a clearer error message.
        """
        school_class = attrs.get('school_class')
        name = attrs.get('name')

        # On update, exclude the current instance from uniqueness check
        instance = self.instance
        qs = Section.objects.filter(school_class=school_class, name=name)
        if instance:
            qs = qs.exclude(pk=instance.pk)

        if qs.exists():
            raise serializers.ValidationError(
                {'name': f'Section "{name}" already exists in {school_class.name}.'}
            )
        return attrs


class SectionListSerializer(serializers.ModelSerializer):
    """Lightweight section serializer for nested display inside Class."""
    current_strength = serializers.IntegerField(read_only=True)
    available_seats = serializers.IntegerField(read_only=True)

    class Meta:
        model = Section
        fields = [
            'id', 'name', 'section_teacher', 'room_number',
            'max_capacity', 'current_strength', 'available_seats', 'is_active'
        ]


# ─────────────────────────────────────────────────────────────
# CLASS SERIALIZERS
# ─────────────────────────────────────────────────────────────
class ClassSerializer(serializers.ModelSerializer):
    """
    Full Class serializer.
    Nests sections inside the class response.
    """
    # Nest all sections of this class
    sections = SectionListSerializer(many=True, read_only=True)
    total_students = serializers.IntegerField(read_only=True)
    total_sections = serializers.IntegerField(read_only=True)
    # Show class teacher name
    class_teacher_name = serializers.SerializerMethodField()

    class Meta:
        model = Class
        fields = [
            'id', 'name', 'numeric_grade', 'description',
            'class_teacher', 'class_teacher_name',
            'is_active', 'total_sections', 'total_students',
            'sections', 'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_class_teacher_name(self, obj):
        if obj.class_teacher:
            return obj.class_teacher.user.full_name
        return None


class ClassListSerializer(serializers.ModelSerializer):
    """Lightweight Class serializer for list views (no nested sections)."""
    total_students = serializers.IntegerField(read_only=True)
    total_sections = serializers.IntegerField(read_only=True)
    class_teacher_name = serializers.SerializerMethodField()

    class Meta:
        model = Class
        fields = [
            'id', 'name', 'numeric_grade', 'class_teacher',
            'class_teacher_name', 'is_active',
            'total_sections', 'total_students',
        ]

    def get_class_teacher_name(self, obj):
        if obj.class_teacher:
            return obj.class_teacher.user.full_name
        return None


class ClassCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer for creating and updating a Class."""
    class Meta:
        model = Class
        fields = [
            'name', 'numeric_grade', 'description',
            'class_teacher', 'is_active'
        ]

    def validate_name(self, value):
        """Ensure class name is unique (case-insensitive)."""
        qs = Class.objects.filter(name__iexact=value)
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise serializers.ValidationError(
                f'A class named "{value}" already exists.'
            )
        return value
