"""
Custom views for error pages and utility functions.
"""

from django.shortcuts import render
from django.http import HttpResponse
from django.conf import settings


def error_404(request, exception=None):
    """Custom 404 error page."""
    return render(request, 'errors/404.html', status=404)


def error_500(request):
    """Custom 500 error page."""
    return render(request, 'errors/500.html', status=500)


def error_403(request, exception=None):
    """Custom 403 error page."""
    return render(request, 'errors/403.html', status=403)


def health_check(request):
    """Health check endpoint for monitoring."""
    try:
        from django.db import connection
        connection.ensure_connection()
        return HttpResponse('OK', status=200)
    except Exception as e:
        return HttpResponse(f'Database Error: {str(e)}', status=500)