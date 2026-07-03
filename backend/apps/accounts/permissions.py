"""
Custom Permissions for School Management System.

DRF permissions are classes that decide if a request should be allowed.
We create role-based permissions to restrict access by user type.

Usage example in a view:
    permission_classes = [IsAdminUser]     # Only admins
    permission_classes = [IsTeacherUser]   # Only teachers
    permission_classes = [IsAdminOrTeacher]  # Either role
"""
from rest_framework.permissions import BasePermission


class IsAdminUser(BasePermission):
    """
    Allow access only to Admin users.
    Used for user management, reports, and system settings.
    """
    message = 'Access denied. Admin role required.'

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and
            request.user.role == 'ADMIN'
        )


class IsTeacherUser(BasePermission):
    """
    Allow access only to Teacher users.
    Used for attendance marking, marks entry, etc.
    """
    message = 'Access denied. Teacher role required.'

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and
            request.user.role == 'TEACHER'
        )


class IsStudentUser(BasePermission):
    """
    Allow access only to Student users.
    Used for viewing results, attendance, assignments.
    """
    message = 'Access denied. Student role required.'

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and
            request.user.role == 'STUDENT'
        )


class IsAdminOrTeacher(BasePermission):
    """
    Allow access to Admin or Teacher users.
    Useful for endpoints that both roles can access.
    """
    message = 'Access denied. Admin or Teacher role required.'

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and
            request.user.role in ['ADMIN', 'TEACHER']
        )


class IsAdminOrReadOnly(BasePermission):
    """
    Allow Admin users full access.
    Allow other authenticated users read-only access (GET, HEAD, OPTIONS).
    """
    message = 'Access denied. Write operations require Admin role.'

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False

        # Safe methods (read-only) are allowed for all authenticated users
        if request.method in ('GET', 'HEAD', 'OPTIONS'):
            return True

        # Write methods require Admin role
        return request.user.role == 'ADMIN'


class IsOwnerOrAdmin(BasePermission):
    """
    Object-level permission: allow access if user owns the object or is Admin.
    Used for profile updates where a user can only edit their own profile.
    """
    message = 'Access denied. You can only access your own data.'

    def has_object_permission(self, request, view, obj):
        # Admin can access any object
        if request.user.role == 'ADMIN':
            return True

        # Users can only access their own data
        # The object must have a 'user' field pointing to CustomUser
        if hasattr(obj, 'user'):
            return obj.user == request.user

        # If the object IS a user, check directly
        return obj == request.user
