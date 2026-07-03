"""
Pagination classes for API responses.
"""
from rest_framework.pagination import PageNumberPagination


class StandardResultsSetPagination(PageNumberPagination):
    """
    Standard pagination for API results.
    
    Query parameters:
    - ?page=1 (default)
    - ?page_size=20 (customizable, default 20, max 100)
    """
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100
    page_query_param = 'page'


class LargeResultsSetPagination(PageNumberPagination):
    """
    Pagination for endpoints that return larger datasets.
    Default 50 per page, max 500.
    """
    page_size = 50
    page_size_query_param = 'page_size'
    max_page_size = 500
    page_query_param = 'page'


class SmallResultsSetPagination(PageNumberPagination):
    """
    Pagination for endpoints that should return fewer results.
    Default 10 per page, max 20.
    """
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 20
    page_query_param = 'page'
