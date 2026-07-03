"""
Serializers for the activity_logs app.
"""
from rest_framework import serializers
from .models import ActivityLog

class ActivityLogSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.full_name', read_only=True, default='System')

    class Meta:
        model = ActivityLog
        fields = [
            'id', 'user', 'user_name', 'action', 'model_name', 
            'object_id', 'description', 'ip_address', 'timestamp'
        ]
        read_only_fields = ['id', 'user', 'action', 'model_name', 'object_id', 'description', 'ip_address', 'timestamp']
