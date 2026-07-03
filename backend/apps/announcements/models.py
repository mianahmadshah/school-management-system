"""
Models for the announcements app.
"""
from django.db import models
from django.conf import settings


class Announcement(models.Model):
    """
    School-wide or targeted announcements/notices.
    """
    class Audience(models.TextChoices):
        ALL = 'ALL', 'Everyone'
        TEACHERS = 'TEACHERS', 'Teachers Only'
        STUDENTS = 'STUDENTS', 'Students Only'
        SPECIFIC_CLASS = 'SPECIFIC_CLASS', 'Specific Class'
        SPECIFIC_SECTION = 'SPECIFIC_SECTION', 'Specific Section'

    title = models.CharField(
        max_length=200,
        help_text="Announcement title."
    )
    content = models.TextField(
        help_text="Announcement content/body."
    )
    
    target_audience = models.CharField(
        max_length=20,
        choices=Audience.choices,
        default=Audience.ALL,
        help_text="Who should see this announcement?"
    )
    # If audience is SPECIFIC_CLASS or SPECIFIC_SECTION
    target_class = models.ForeignKey(
        'classes.Class',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='announcements',
        help_text="Select class if audience is 'Specific Class' or 'Specific Section'"
    )
    target_section = models.ForeignKey(
        'classes.Section',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='announcements',
        help_text="Select section if audience is 'Specific Section'"
    )
    
    is_important = models.BooleanField(
        default=False,
        help_text="Mark as important announcement."
    )
    is_published = models.BooleanField(
        default=True,
        help_text="Published announcements are visible to users."
    )
    attachment = models.FileField(
        upload_to='announcements/',
        blank=True,
        null=True,
        help_text="Optional attachment (PDF, image, etc.)"
    )
    
    published_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='published_announcements',
        help_text="Admin/User who published this."
    )
    published_at = models.DateTimeField(
        auto_now_add=True
    )
    expires_at = models.DateTimeField(
        blank=True,
        null=True,
        help_text="Announcement auto-hides after this date."
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'announcements'
        verbose_name = 'Announcement'
        verbose_name_plural = 'Announcements'
        ordering = ['-published_at']

    def __str__(self):
        return self.title

    @property
    def is_expired(self):
        """Check if announcement has expired."""
        from django.utils import timezone
        if self.expires_at:
            return timezone.now() > self.expires_at
        return False

    @property
    def audience_display(self):
        """Return readable audience description."""
        if self.target_audience == self.Audience.SPECIFIC_CLASS:
            return f"Specific Class: {self.target_class.name}"
        elif self.target_audience == self.Audience.SPECIFIC_SECTION:
            return f"Specific Section: {self.target_section}"
        return self.get_target_audience_display()
