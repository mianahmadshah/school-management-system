from django.contrib import admin
from .models import Announcement

@admin.register(Announcement)
class AnnouncementAdmin(admin.ModelAdmin):
    list_display = ['title', 'target_audience', 'target_class', 'is_published', 'is_important']
    list_filter = ['target_audience', 'is_published', 'is_important']
    search_fields = ['title', 'content']
    ordering = ['-id']
