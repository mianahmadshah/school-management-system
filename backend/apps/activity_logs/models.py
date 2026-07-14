"""
Activity Log model — records every important action in the system.
"""
from django.db import models
from django.conf import settings
from django.contrib.contenttypes.models import ContentType


class ActivityLog(models.Model):
    """
    Stores a log entry for every significant action in the system.
    
    Examples:
      - Admin logged in
      - Student created (by Admin John)
      - Marks updated for Ahmed Khan
      - Announcement deleted
    """
    class ActionType(models.TextChoices):
        LOGIN = 'LOGIN', 'User Login'
        LOGOUT = 'LOGOUT', 'User Logout'
        CREATE = 'CREATE', 'Record Created'
        UPDATE = 'UPDATE', 'Record Updated'
        DELETE = 'DELETE', 'Record Deleted'
        VIEW = 'VIEW', 'Record Viewed'
        PAYMENT = 'PAYMENT', 'Fee Payment'
        MARK_ATTENDANCE = 'MARK_ATTENDANCE', 'Attendance Marked'
        GRADE_SUBMISSION = 'GRADE_SUBMISSION', 'Submission Graded'
        ASSIGN_MARKS = 'ASSIGN_MARKS', 'Marks Assigned'
        OTHER = 'OTHER', 'Other'

    # ─── WHO DID THE ACTION ──────────────────────────────
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='activity_logs',
        help_text="User who performed the action."
    )

    # ─── WHAT ACTION WAS PERFORMED ───────────────────────
    action = models.CharField(
        max_length=50,
        choices=ActionType.choices,
        default=ActionType.OTHER,
        help_text="Type of action performed."
    )

    # ─── WHAT WAS AFFECTED ───────────────────────────────
    model_name = models.CharField(
        max_length=100,
        help_text="Model/Table name (e.g. Student, Exam, Marks)."
    )
    object_id = models.PositiveIntegerField(
        help_text="ID of the object affected."
    )
    object_repr = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        help_text="String representation of the object (for display)."
    )

    # ─── ADDITIONAL DETAILS ──────────────────────────────
    description = models.TextField(
        blank=True,
        null=True,
        help_text="Detailed description of what happened."
    )
    ip_address = models.GenericIPAddressField(
        blank=True,
        null=True,
        help_text="IP address from which action was performed."
    )
    user_agent = models.TextField(
        blank=True,
        null=True,
        help_text="Browser/client user agent."
    )
    
    # ─── TIMESTAMP ──────────────────────────────────────
    timestamp = models.DateTimeField(
        auto_now_add=True,
        help_text="When the action happened."
    )

    class Meta:
        db_table = 'activity_logs'
        verbose_name = 'Activity Log'
        verbose_name_plural = 'Activity Logs'
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['user', '-timestamp']),
            models.Index(fields=['model_name', 'object_id']),
            models.Index(fields=['action', '-timestamp']),
        ]

    def __str__(self):
        return f"{self.user} - {self.get_action_display()} on {self.model_name} ({self.timestamp})"

    @classmethod
    def log(cls, user, action, model_name, object_id, object_repr=None, description=None, ip_address=None, user_agent=None, request=None):
        """
        Create a log entry.
        
        Usage:
            ActivityLog.log(
                user=request.user,
                action=ActivityLog.ActionType.CREATE,
                model_name='Student',
                object_id=student.id,
                object_repr=str(student),
                description=f"Created student {student.user.get_full_name()}"
            )
        """
        # Extract IP and user agent from request if provided
        if request:
            if ip_address is None:
                ip_address = cls._get_client_ip(request)
            if user_agent is None:
                user_agent = cls._get_user_agent(request)
        
        return cls.objects.create(
            user=user,
            action=action,
            model_name=model_name,
            object_id=object_id,
            object_repr=object_repr or str(object_id),
            description=description,
            ip_address=ip_address,
            user_agent=user_agent
        )
    
    @staticmethod
    def _get_client_ip(request):
        """Extract client IP address from request."""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0].strip()
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
    
    @staticmethod
    def _get_user_agent(request):
        """Extract user agent from request."""
        return request.META.get('HTTP_USER_AGENT', '')

    @classmethod
    def get_user_activity(cls, user, limit=50):
        """Get recent activity for a user."""
        return cls.objects.filter(user=user).order_by('-timestamp')[:limit]

    @classmethod
    def get_model_activity(cls, model_name, object_id):
        """Get all activity for a specific object."""
        return cls.objects.filter(
            model_name=model_name,
            object_id=object_id
        ).order_by('-timestamp')

