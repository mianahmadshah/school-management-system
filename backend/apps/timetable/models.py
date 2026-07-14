"""
Models for the Timetable and Scheduling app.
"""
from django.db import models


class Period(models.Model):
    """
    Defines the time slots for classes.
    Example: '1st Period', 'Lunch Break'
    """
    name = models.CharField(
        max_length=50,
        help_text="e.g. 1st Period, Lunch Break"
    )
    start_time = models.TimeField()
    end_time = models.TimeField()
    is_break = models.BooleanField(
        default=False,
        help_text="Check if this period is a break/recess."
    )
    
    # Ordering order (e.g. 1 for first period, 2 for second)
    order = models.PositiveIntegerField(
        default=0,
        help_text="Used to sort periods chronologically."
    )

    class Meta:
        db_table = 'periods'
        verbose_name = 'Period'
        verbose_name_plural = 'Periods'
        ordering = ['order', 'start_time']

    def __str__(self):
        return f"{self.name} ({self.start_time.strftime('%H:%M')} - {self.end_time.strftime('%H:%M')})"


class Timetable(models.Model):
    """
    Maps a Class + Section + Subject + Teacher to a specific Period and Day.
    """
    class DayOfWeek(models.TextChoices):
        MONDAY = 'MONDAY', 'Monday'
        TUESDAY = 'TUESDAY', 'Tuesday'
        WEDNESDAY = 'WEDNESDAY', 'Wednesday'
        THURSDAY = 'THURSDAY', 'Thursday'
        FRIDAY = 'FRIDAY', 'Friday'
        SATURDAY = 'SATURDAY', 'Saturday'
        SUNDAY = 'SUNDAY', 'Sunday'

    school_class = models.ForeignKey(
        'classes.Class',
        on_delete=models.CASCADE,
        related_name='timetable_entries'
    )
    section = models.ForeignKey(
        'classes.Section',
        on_delete=models.CASCADE,
        related_name='timetable_entries'
    )
    subject = models.ForeignKey(
        'subjects.Subject',
        on_delete=models.CASCADE,
        related_name='timetable_entries'
    )
    teacher = models.ForeignKey(
        'teachers.Teacher',
        on_delete=models.CASCADE,
        related_name='timetable_entries'
    )
    period = models.ForeignKey(
        Period,
        on_delete=models.CASCADE,
        related_name='timetable_entries'
    )
    
    day_of_week = models.CharField(
        max_length=20,
        choices=DayOfWeek.choices,
        help_text="Which day of the week."
    )
    room_number = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        help_text="Classroom number where the class is held."
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Active timetable entries are in effect."
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'timetable'
        verbose_name = 'Timetable Entry'
        verbose_name_plural = 'Timetable Entries'
        # No duplicate class-section-period-day combinations
        unique_together = [['school_class', 'section', 'period', 'day_of_week']]
        ordering = ['section', 'day_of_week', 'period__order']

    def __str__(self):
        return f"{self.section} - {self.get_day_of_week_display()} - {self.period.name} ({self.subject.name})"

    @property
    def class_time(self):
        """Return the time slot."""
        return f"{self.period.start_time.strftime('%H:%M')} - {self.period.end_time.strftime('%H:%M')}"

