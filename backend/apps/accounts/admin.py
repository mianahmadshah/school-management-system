"""
Register CustomUser in Django Admin panel.
Visit /admin/ to manage users through a web UI.
"""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    """
    Custom admin configuration for CustomUser.
    Extends Django's built-in UserAdmin for password handling.
    """
    # Columns displayed in the user list
    list_display = [
        'email', 'full_name', 'role', 'phone',
        'is_active', 'is_staff', 'created_at'
    ]

    # Clickable filter options in the right sidebar
    list_filter = ['role', 'is_active', 'is_staff', 'gender', 'created_at']

    # Search box searches these fields
    search_fields = ['email', 'first_name', 'last_name', 'phone']

    # Default sort order in admin
    ordering = ['-created_at']

    # Fields shown when editing a user
    fieldsets = (
        ('Login Info', {'fields': ('email', 'username', 'password')}),
        ('Personal Info', {
            'fields': (
                'first_name', 'last_name', 'phone',
                'date_of_birth', 'gender', 'profile_picture', 'address'
            )
        }),
        ('Role & Permissions', {
            'fields': ('role', 'is_active', 'is_staff', 'is_superuser', 'groups')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at', 'last_login'),
            'classes': ('collapse',)  # Collapsed by default
        }),
    )

    # Fields shown when creating a new user
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'email', 'username', 'first_name', 'last_name',
                'role', 'password1', 'password2'
            ),
        }),
    )

    # Make timestamps read-only (auto-set by Django)
    readonly_fields = ['created_at', 'updated_at']
