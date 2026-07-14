"""
Custom middleware for performance optimization.
"""

import time
from django.core.cache import cache
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.conf import settings


class PerformanceMiddleware:
    """Middleware to add performance headers and caching."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Start timer
        start_time = time.time()

        response = self.get_response(request)

        # Add performance header (only in debug mode)
        if settings.DEBUG:
            elapsed_time = time.time() - start_time
            response['X-Response-Time'] = f'{elapsed_time:.3f}s'

        # Add cache headers for static content
        if request.path.startswith(settings.STATIC_URL):
            response['Cache-Control'] = 'public, max-age=31536000'

        return response


class MinifyHTMLMiddleware:
    """Minify HTML output in production."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        # Only minify HTML responses
        if (response.get('Content-Type', '') == 'text/html; charset=utf-8' 
                and not settings.DEBUG):
            response.content = self.minify_html(response.content)

        return response

    def minify_html(self, html):
        """Basic HTML minification."""
        html = html.decode('utf-8')
        # Remove whitespace between tags
        html = ' '.join(html.split())
        # Remove comments
        html = html.replace('<!-- ', '<').replace(' -->', '>')
        return html.encode('utf-8')


class ETagMiddleware:
    """Add ETag support for caching."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        if request.method == 'GET' and response.get('Content-Type', '').startswith('text/html'):
            response = self.set_etag(request, response)

        return response

    def set_etag(self, request, response):
        """Generate and set ETag."""
        try:
            etag = str(hash(response.content.decode('utf-8')))
            response['ETag'] = etag

            # Check if client sent If-None-Match
            if 'HTTP_IF_NONE_MATCH' in request.environ:
                if request.environ['HTTP_IF_NONE_MATCH'] == etag:
                    return HttpResponse(status=304)

        except Exception:
            pass

        return response