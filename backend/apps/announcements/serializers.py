"""
Serializers for the announcements app.
"""
from rest_framework import serializers
from .models import Announcement

class AnnouncementSerializer(serializers.ModelSerializer):
    created_by_name = serializers.CharField(source='created_by.full_name', read_only=True)
    target_class_name = serializers.CharField(source='target_class.name', read_only=True)

    class Meta:
        model = Announcement
        fields = [
            'id', 'title', 'content', 'target_audience', 
            'target_class', 'target_class_name', 
            'attachment', 'created_by', 'created_by_name', 
            'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_by', 'created_at', 'updated_at']

    def validate(self, attrs):
        audience = attrs.get('target_audience')
        target_class = attrs.get('target_class')

        if audience == Announcement.Audience.SPECIFIC_CLASS and not target_class:
            raise serializers.ValidationError(
                {"target_class": "Class must be specified if audience is 'Specific Class'."}
            )
        
        # If audience is not specific class, ensure target_class is cleared
        if audience != Announcement.Audience.SPECIFIC_CLASS and target_class:
            attrs['target_class'] = None
            
        return attrs
